# Mov2Quarantine

[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/downloads/)
[![LDAP3](https://img.shields.io/badge/ldap3-latest-green.svg)](https://ldap3.readthedocs.io/)

Un outil Python pour la gestion automatisée des comptes Active Directory inactifs.

## 📋 Description

Mov2Quarantine est un script Python qui analyse et gère les comptes Active Directory inactifs. Il permet de déplacer automatiquement ou manuellement les comptes qui n'ont pas été utilisés depuis une période définie vers une OU de quarantaine.

## ✨ Fonctionnalités

- 🔍 Analyse des comptes utilisateurs dans l'Active Directory
- ⚠️ Identification des comptes inactifs selon des critères configurables
- 🤖 Mode automatique pour le déplacement des comptes
- 👆 Mode manuel avec confirmation pour chaque déplacement
- 📊 Interface web pour visualiser les résultats
- 📝 Journalisation détaillée des opérations

## 🚀 Installation

```bash
git clone https://github.com/votre-username/Mov2Quarantine.git
cd Mov2Quarantine
pip install -r requirements.txt
```

## ⚙️ Configuration

Créez un fichier `config_ad.json` avec les paramètres suivants :

```json
{
    "server_address": "votre-serveur-ad",
    "username": "admin-username",
    "password": "admin-password",
    "ou_dn_source": "OU=Users,DC=domain,DC=com",
    "ou_dn_destination": "OU=Quarantine,DC=domain,DC=com",
    "operation_mode": "manuel",
    "inactivity_days": 90
}
```

## 🎯 Utilisation

```bash
python mov2quarantine.py
```

## 📝 Journalisation

Les opérations sont enregistrées dans `mov2quarantine.log` avec les informations suivantes :
- Date et heure de l'opération
- Utilisateur concerné
- Action effectuée
- Résultat de l'opération

## 🔒 Sécurité

- Nécessite des droits d'administration Active Directory
- Utilise une connexion LDAP sécurisée
- Stockage sécurisé des identifiants dans un fichier de configuration

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Distribué sous la licence MIT. Voir `LICENSE` pour plus d'informations.

## 👥 Contact

Votre Nom - [@votre_twitter](https://twitter.com/votre_twitter)

Lien du projet : [https://github.com/votre-username/Mov2Quarantine](https://github.com/votre-username/Mov2Quarantine)
