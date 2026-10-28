# 💰 Architecture-log — Application de Gestion de Cagnottes

Application web et interface en ligne de commande (CLI) de gestion de cagnottes et de répartition de dépenses partagées. 

Projet réalisé dans le cadre du **BUT Informatique**, mettant en œuvre une **architecture n-tier** moderne avec Flask, SQLAlchemy, Click et le gestionnaire de paquets `uv`.

---

## 🏗️ Structure du Projet

```text
Architecture-log/
├── pyproject.toml              # Configuration du projet, dépendances (uv) et entrées CLI
├── README.md                   # Documentation du projet
└── src/
    └── archilog/               # Code source principal
        ├── __init__.py         # Fabrique d'application (create_app), sécurité & logs
        ├── views.py            # Contrôleur Web (Blueprints, routes & API)
        ├── domain.py           # Logique métier (calculs de répartition)
        ├── data.py             # Couche de données (SQLAlchemy / SQLite)
        ├── cli.py              # Interface en ligne de commande (Click)
        ├── forms.py            # Formulaires (Flask-WTF)
        └── templates/          # Interfaces HTML (Jinja2)
            ├── layout.html     # Squelette HTML global
            ├── home.html       # Liste des cagnottes & création
            └── details.html    # Détails d'une cagnotte & dépenses
```

---

## 🛠️ Stack Technique

- **Langage :** Python 3.11+
- **Framework Web :** Flask
- **Gestionnaire de dépendances :** `uv`
- **ORM / Base de données :** SQLAlchemy (SQLite)
- **CLI :** Click
- **Sécurité :** Flask-HTTPAuth (Basic Auth & Token Bearer)
- **Validation & Doc API :** SpecTree / Pydantic

---

## 🚀 Installation et Lancement

### 1. Prérequis & Installation
Assure-toi d'avoir `uv` installé. À la racine du projet, exécute :
```powershell
uv sync
```

### 2. Initialisation de la Base de Données
Avant le premier lancement, initialise la base de données SQLite via la CLI :
```powershell
uv run archilog init-db
```

### 3. Lancement du Serveur Web (Flask)
Pour démarrer le serveur web localement en utilisant la fabrique d'application (`create_app`) :
```powershell
uv run flask --app "archilog:create_app()" run
```

Une fois le serveur lancé, accède à l'application via ton navigateur :
👉 **`http://127.0.0.1:5000/`**

> 🔑 **Authentification requise (HTTP Basic Auth) :**
> - **Nom d'utilisateur :** `admin`
> - **Mot de passe :** `admin`
> *(Accès direct : `http://admin:admin@127.0.0.1:5000/`)*

---

## 💻 Utilisation de la CLI

Le projet embarque un outil en ligne de commande pour gérer les données directement en terminal :

```powershell
# Afficher l'aide et les commandes disponibles
uv run archilog --help

# Initialiser la base de données
uv run archilog init-db
```

---

## 📡 API REST

L'application expose également des endpoints d'API sous le préfixe `/api` sécurisés par Bearer Token :

- **`GET /api/pots`** : Lister les cagnottes
- **`POST /api/pots`** : Créer une nouvelle cagnotte
- **`DELETE /api/pots/<name>`** : Supprimer une cagnotte (rôle `admin`)
---
![Aperçu de l'application](assets/screenshot.png)
---
Course & examples : [https://kathode.neocities.org/data/archilog](https://kathode.neocities.org/data/archilog)
