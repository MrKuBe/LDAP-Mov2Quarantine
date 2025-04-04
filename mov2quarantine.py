# Importer les bibliothèques nécessaires
import json
from ldap3 import Server, Connection, ALL
from datetime import datetime, timedelta, timezone
import logging

# Configurer le logging
logging.basicConfig(filename='mov2quarantine.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Charger les paramètres de connexion depuis le fichier JSON
with open('config_ad.json', 'r') as config_file:
    config = json.load(config_file)

# Définir les OU à partir du fichier de configuration
ou_dn_source = config['ou_dn_source']  # OU de scrutation
ou_dn_destination = config['ou_dn_destination']  # OU de destination
operation_mode = config['operation_mode']  # Mode d'opération
inactivity_days = config.get('inactivity_days', 90)  # Nombre de jours d'inactivité

# Se connecter au serveur LDAP
server = Server(config['server_address'], get_info=ALL)
conn = Connection(server, user=config['username'], password=config['password'], auto_bind=True)

# Rechercher tous les utilisateurs dans l'OU de scrutation avec la date de création
conn.search(ou_dn_source, '(objectClass=user)', attributes=['sAMAccountName', 'lastLogon', 'whenCreated'])

# Générer le contenu HTML
html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Résultats de la requête LDAP</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/fomantic-ui@2.9.2/dist/semantic.min.css">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/fomantic-ui@2.9.2/dist/semantic.min.js"></script>
    <script type="text/javascript">
        $(document).ready(function() {{
            function filterTable() {{
                var input = $('#searchInput').val().toUpperCase();
                var count = 0;
                $('#resultsTable tbody tr').each(function() {{
                    var text = $(this).text().toUpperCase();
                    if (text.indexOf(input) > -1) {{
                        $(this).show();
                        count++;
                    }} else {{
                        $(this).hide();
                    }}
                }});
                $('#resultCount').text(count + " résultats");
            }}

            function filterAction() {{
                var filter = $('#actionFilter').val();
                var count = 0;
                $('#resultsTable tbody tr').each(function() {{
                    var action = $(this).find('td:eq(2)').text();
                    var lastLogon = $(this).find('td:eq(1)').text();
                    if (filter === 'all' || 
                        (filter === 'never' && lastLogon === 'Jamais') ||
                        action === filter) {{
                        $(this).show();
                        count++;
                    }} else {{
                        $(this).hide();
                    }}
                }});
                $('#resultCount').text(count + " résultats");
            }}

            $('#searchInput').on('keyup', filterTable);
            $('#actionFilter').on('change', filterAction);
            $('#resultCount').text($('#resultsTable tbody tr').length + " résultats");
        }});
    </script>
</head>
<body>
    <div class="ui container">
        <h1 class="ui header">Résultats de la requête LDAP</h1>
        
        <div class="ui info message">
            <div class="header"><i class="info circle icon"></i>À propos de cet outil</div>
            <ul class="ui list">
                <li><i class="search icon"></i>Analyse les comptes utilisateurs dans l'Active Directory et éventuellement, les déplace de <div class="ui tiny label">{ou_dn_source}</div> vers <div class="ui tiny label">{ou_dn_destination}</div></li>
                <li><i class="exclamation triangle icon"></i>Identifie les comptes inactifs depuis plus de {inactivity_days} jours</li>
                <li><i class="hand point up icon"></i>Mode manuel : demande confirmation avant déplacement</li>
                <li><i class="cogs icon"></i>Mode automatique : déplace automatiquement les comptes inactifs</li>
                <li><i class="filter icon"></i>Recherche et filtrage des résultats en temps réel</li>
                <li><i class="warning sign icon"></i>Les lignes en rouge indiquent les comptes à déplacer</li>
            </ul>
        </div>

        <div class="ui form">
            <div class="field">
                <div class="ui icon input">
                    <input id="searchInput" type="text" placeholder="Rechercher...">
                    <i class="search icon"></i>
                </div>
            </div>
            <div class="field">
                <select class="ui dropdown" id="actionFilter">
                    <option value="all">Tous les résultats</option>
                    <option value="never">Jamais connecté</option>
                    <option value="Aucune action">Aucune action</option>
                    <option value="Déplacé">A déplacer</option>
                </select>
            </div>
        </div>
        <div id="resultCount" class="ui label"></div>
        <table class="ui celled striped table" id="resultsTable">
            <thead>
                <tr>
                    <th>Nom d'utilisateur</th>
                    <th>Dernière connexion</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
"""

# Traiter chaque utilisateur trouvé
for entry in conn.entries:
    user_samaccountname = entry.sAMAccountName.value
    last_logon = entry.lastLogon.value
    when_created = entry.whenCreated.value

    # Calculer le temps écoulé depuis la création du compte
    account_age = datetime.now(timezone.utc) - when_created.replace(tzinfo=timezone.utc)
    
    if last_logon is None:
        # Si le compte n'a jamais été utilisé, vérifier s'il est assez ancien
        if account_age > timedelta(days=inactivity_days):
            print(f"👤 L'utilisateur {user_samaccountname} n'a jamais ouvert sa session et existe depuis {account_age.days} jours. ❌")
            should_move = True
        else:
            print(f"👤 L'utilisateur {user_samaccountname} n'a jamais ouvert sa session mais a été créé il y a moins de {inactivity_days} jours. ✅")
            should_move = False
        last_logon_str = "Jamais"
    else:
        # Vérifier si last_logon est déjà un objet datetime
        if isinstance(last_logon, datetime):
            last_logon_date = last_logon
        else:
            try:
                last_logon_date = datetime.fromtimestamp(int(last_logon) / 1e7 - 11644473600)
            except Exception as e:
                print(f"Erreur lors de la conversion de la date de dernière connexion pour {user_samaccountname}: {e}")
                should_move = False
                continue

        inactivity_time = datetime.now(timezone.utc) - last_logon_date.replace(tzinfo=timezone.utc)
        last_logon_str = last_logon_date.strftime('%Y-%m-%d %H:%M:%S')

        if inactivity_time > timedelta(days=inactivity_days) and account_age > timedelta(days=inactivity_days):
            print(f"⚠️ L'utilisateur {user_samaccountname} n'a pas ouvert sa session depuis {inactivity_time.days} jours. ❌")
            should_move = True
        else:
            print(f"✅ L'utilisateur {user_samaccountname} est actif ou trop récent.")
            should_move = False

    # Gestion du mode d'opération pour le déplacement
    if should_move:
        if operation_mode == 'manuel':
            confirmation = input(f"Voulez-vous déplacer l'utilisateur {user_samaccountname} vers l'OU de destination ? (Oui/Non) : ")
            if confirmation.lower() == 'oui':
                # Déplacer l'utilisateur vers l'OU de destination (commenté pour le test)
                # conn.modify_dn(entry, new_dn=f'CN={user_samaccountname},{ou_dn_destination}')
                logging.info(f"L'utilisateur {user_samaccountname} a été déplacé vers l'OU de destination.")
                print(f"L'utilisateur {user_samaccountname} a été déplacé vers l'OU de destination.")
            else:
                print("Aucune action effectuée.")
                logging.info(f"Aucune action effectuée pour l'utilisateur {user_samaccountname}.")
        elif operation_mode == 'automatique':
            # Déplacer l'utilisateur vers l'OU de destination sans confirmation (commenté pour le test)
            # conn.modify_dn(entry, new_dn=f'CN={user_samaccountname},{ou_dn_destination}')
            logging.info(f"L'utilisateur {user_samaccountname} a été déplacé vers l'OU de destination automatiquement.")
            print(f"L'utilisateur {user_samaccountname} a été déplacé vers l'OU de destination automatiquement.")

    action = "Déplacé" if should_move else "Aucune action"
    row_class = "negative" if should_move else ""
    html_content += f"""
                <tr class="{row_class}">
                    <td>{user_samaccountname}</td>
                    <td>{last_logon_str}</td>
                    <td>{action}</td>
                </tr>
    """

html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""

with open('resultats_ldap.html', 'w', encoding='utf-8') as html_file:
    html_file.write(html_content)

# Fermer la connexion
conn.unbind()

# Ouvrir le fichier HTML dans le navigateur par défaut
import webbrowser
webbrowser.open('resultats_ldap.html')
