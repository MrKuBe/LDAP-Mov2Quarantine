# Mov2Quarantine

[English](#english) | [Français](#français)

# English

Tool for managing inactive Active Directory accounts.

## Features

- Analysis of user accounts in Active Directory
- Automatic or manual movement of inactive accounts to a quarantine OU
- Interactive web interface with filtering options:
  - Text search
  - Status filter (All, No action, To move)
  - Last login filter (Never connected)
- Highlighting of accounts to be moved
- Action logging

## Configuration

Use the `config_ad.json` file to configure:
- AD connection information
- Source and destination OUs
- Operation mode (manual/automatic)
- Number of days of inactivity

## Usage

1. Configure the `config_ad.json` file
2. Run `mov2quarantine.py`
3. A browser will open with the management interface
4. Use filters to analyze accounts
5. In manual mode, confirm each move

---

# Français

## Mov2Quarantine

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
