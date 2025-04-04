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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LDAP Query Results</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/fomantic-ui@2.9.2/dist/semantic.min.css">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/fomantic-ui@2.9.2/dist/semantic.min.js"></script>
    <script src="https://semantic-ui.com/javascript/library/tablesort.js"></script>
    <script type="text/javascript">
        $(document).ready(function() {{
            // Fonctions existantes de filtrage
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
                $('#resultCount').text(count + " results");
            }}

            function filterAction() {{
                var filter = $('#actionFilter').val();
                var count = 0;
                $('#resultsTable tbody tr').each(function() {{
                    var action = $(this).find('td:eq(2)').text();
                    var lastLogon = $(this).find('td:eq(1)').text();
                    if (filter === 'all' || 
                        (filter === 'never' && lastLogon === 'Never') ||
                        action === filter) {{
                        $(this).show();
                        count++;
                    }} else {{
                        $(this).hide();
                    }}
                }});
                $('#resultCount').text(count + " results");
            }}

            // Nouvelle fonction pour le tri des colonnes
            $('.sortable.table').tablesort();

            $('#searchInput').on('keyup', filterTable);
            $('#actionFilter').on('change', filterAction);
            $('#resultCount').text($('#resultsTable tbody tr').length + " results");
        }});
    </script>
</head>
<body>
    <div class="ui container">
        <h1 class="ui header">LDAP Query Results</h1>
        
        <div class="ui info message">
            <div class="header"><i class="info circle icon"></i>About this tool</div>
            <ul class="ui list">
                <li><i class="search icon"></i>Analyzes user accounts in Active Directory and possibly moves them from <div class="ui tiny label">{ou_dn_source}</div> to <div class="ui tiny label">{ou_dn_destination}</div></li>
                <li><i class="exclamation triangle icon"></i>Identifies accounts inactive for more than {inactivity_days} days</li>
                <li><i class="hand point up icon"></i>Manual mode: asks for confirmation before moving</li>
                <li><i class="cogs icon"></i>Automatic mode: automatically moves inactive accounts</li>
                <li><i class="filter icon"></i>Real-time search and filtering of results</li>
                <li><i class="warning sign icon"></i>Red rows indicate accounts to be moved</li>
            </ul>
        </div>

        <div class="ui form">
            <div class="field">
                <div class="ui icon input">
                    <input id="searchInput" type="text" placeholder="Search...">
                    <i class="search icon"></i>
                </div>
            </div>
            <div class="field">
                <select class="ui dropdown" id="actionFilter">
                    <option value="all">All results</option>
                    <option value="never">Never connected</option>
                    <option value="No action">No action</option>
                    <option value="Moved">To be moved</option>
                </select>
            </div>
        </div>
        <div id="resultCount" class="ui label"></div>
        <table class="ui sortable celled striped table" id="resultsTable">
            <thead>
                <tr>
                    <th class="sorted ascending">Username</th>
                    <th>Last login</th>
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
            print(f"👤 User {user_samaccountname} has never logged in and exists for {account_age.days} days. ❌")
            should_move = True
        else:
            print(f"👤 User {user_samaccountname} has never logged in but was created less than {inactivity_days} days ago. ✅")
            should_move = False
        last_logon_str = "Never"
    else:
        # Vérifier si last_logon est déjà un objet datetime
        if isinstance(last_logon, datetime):
            last_logon_date = last_logon
        else:
            try:
                last_logon_date = datetime.fromtimestamp(int(last_logon) / 1e7 - 11644473600)
            except Exception as e:
                print(f"Error converting last login date for {user_samaccountname}: {e}")
                should_move = False
                continue

        inactivity_time = datetime.now(timezone.utc) - last_logon_date.replace(tzinfo=timezone.utc)
        last_logon_str = last_logon_date.strftime('%Y-%m-%d %H:%M:%S')

        if inactivity_time > timedelta(days=inactivity_days) and account_age > timedelta(days=inactivity_days):
            print(f"⚠️ User {user_samaccountname} hasn't logged in for {inactivity_time.days} days. ❌")
            should_move = True
        else:
            print(f"✅ User {user_samaccountname} is active or too recent.")
            should_move = False

    # Gestion du mode d'opération pour le déplacement
    if should_move:
        if operation_mode == 'manuel':
            confirmation = input(f"Do you want to move user {user_samaccountname} to the destination OU? (Yes/No): ")
            if confirmation.lower() == 'yes':
                # Déplacer l'utilisateur vers l'OU de destination (commenté pour le test)
                # conn.modify_dn(entry, new_dn=f'CN={user_samaccountname},{ou_dn_destination}')
                logging.info(f"User {user_samaccountname} has been moved to destination OU.")
                print(f"User {user_samaccountname} has been moved to destination OU.")
            else:
                print("No action taken.")
                logging.info(f"No action taken for user {user_samaccountname}.")
        elif operation_mode == 'automatique':
            # Déplacer l'utilisateur vers l'OU de destination sans confirmation (commenté pour le test)
            # conn.modify_dn(entry, new_dn=f'CN={user_samaccountname},{ou_dn_destination}')
            logging.info(f"User {user_samaccountname} has been automatically moved to destination OU.")
            print(f"User {user_samaccountname} has been automatically moved to destination OU.")

    action = "Moved" if should_move else "No action"
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
