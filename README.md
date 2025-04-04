# Mov2Quarantine

Outil de gestion des comptes Active Directory inactifs.

## Fonctionnalités

- Analyse des comptes utilisateurs dans l'Active Directory
- Déplacement automatique ou manuel des comptes inactifs vers une OU de quarantaine
- Interface web interactive avec options de filtrage :
  - Recherche textuelle
  - Filtre par statut (Tous, Aucune action, À déplacer)
  - Filtre par dernière connexion (Jamais connecté)
- Mise en évidence des comptes à déplacer
- Journalisation des actions

## Configuration

Utilisez le fichier `config_ad.json` pour configurer :
- Les informations de connexion AD
- Les OUs source et destination
- Le mode d'opération (manuel/automatique)
- Le nombre de jours d'inactivité

## Utilisation

1. Configurez le fichier `config_ad.json`
2. Exécutez `mov2quarantine.py`
3. Un navigateur s'ouvrira avec l'interface de gestion
4. Utilisez les filtres pour analyser les comptes
5. En mode manuel, confirmez chaque déplacement
