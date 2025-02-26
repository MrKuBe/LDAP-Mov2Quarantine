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

# Se connecter au serveur LDAP
server = Server(config['server_address'], get_info=ALL)
conn = Connection(server, user=config['username'], password=config['password'], auto_bind=True)

# Rechercher tous les utilisateurs dans l'OU de scrutation
conn.search(ou_dn_source, '(objectClass=user)', attributes=['sAMAccountName', 'lastLogon'])

# Traiter chaque utilisateur trouvé
for entry in conn.entries:
    user_samaccountname = entry.sAMAccountName.value
    last_logon = entry.lastLogon.value

    if last_logon is None:
        print(f"👤 L'utilisateur {user_samaccountname} n'a jamais ouvert sa session. ❌")
        should_move = True
        last_logon_date = None  # Définir last_logon_date à None
    else:
        # Vérifier si last_logon est déjà un objet datetime
        if isinstance(last_logon, datetime):
            last_logon_date = last_logon
        else:
            # Conversion de last_logon en datetime
            try:
                last_logon_date = datetime.fromtimestamp(int(last_logon) / 1e7 - 11644473600)  # Conversion de la date
            except Exception as e:
                print(f"Erreur lors de la conversion de la date de dernière connexion pour {user_samaccountname}: {e}")
                should_move = False
                continue  # Passer à l'utilisateur suivant

        print(f"🗓️ L'utilisateur {user_samaccountname} a ouvert sa session pour la dernière fois le {last_logon_date.strftime('%Y-%m-%d %H:%M:%S')}.")

        if last_logon_date and datetime.now(timezone.utc) - last_logon_date.replace(tzinfo=timezone.utc) > timedelta(days=90):  # Plus de 3 mois
            print(f"⚠️ L'utilisateur {user_samaccountname} n'a pas ouvert sa session depuis plus de trois mois. ❌")
            should_move = True
        else:
            print(f"✅ L'utilisateur {user_samaccountname} a ouvert sa session récemment.")
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

# Fermer la connexion
conn.unbind()
