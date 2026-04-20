# 💰 Archilog - Gestionnaire de Cagnottes Partagées

Archilog est une application de gestion de dépenses de groupe (type "Tricount"). Elle permet de créer des cagnottes, d'enregistrer des dépenses et de calculer automatiquement qui doit quoi à qui pour équilibrer les comptes.

Ce projet a été conçu avec une **architecture modulaire et robuste**, séparant les interfaces (Web, API, CLI) de la logique métier.

## 🚀 Fonctionnalités

- **🌐 Interface Web** : Interface utilisateur conviviale pour gérer les cagnottes au quotidien.
- **🔌 API REST** : API sécurisée par Token (Bearer) avec documentation OpenAPI/Swagger intégrée.
- **🖥️ CLI (Terminal)** : Interface en ligne de commande pour l'administration et les actions rapides.
- **⚖️ Algorithme d'Équilibrage** : Calcul optimisé des remboursements pour minimiser le nombre de transactions.
- **🔒 Sécurité** : Gestion des rôles (Admin/User) avec authentification Basic (Web) et Token (API).

---

## 🛠️ Architecture Technique

Le projet suit une structure de package Python moderne :

* **`archilog/`** : Cœur de l'application (Package).
    * `data.py` : Persistance avec **SQLAlchemy Core** (SQLite).
    * `domain.py` : Logique métier (Algorithme de calcul).
    * `views.py` : Blueprints Flask pour le Web et l'API.
    * `cli.py` : Commandes terminal avec **Click**.
* **Packaging** : Gestion des dépendances et build avec **uv**.
* **Production** : Serveur WSGI haute performance **Granian**.

---

📂 Organisation des fichiers (Mise à jour)

Voici la structure finale à inclure pour montrer que les templates sont intégrés au package :
Plaintext

archilog/

├── templates/ &nbsp; &nbsp; &nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Dossier racine des vues HTML

│  &nbsp;&nbsp;&nbsp;&nbsp;├── layout.html &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Template parent

│  &nbsp;&nbsp;&nbsp;&nbsp;├── home.html &nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Page d'accueil (Liste & Création)

│  &nbsp;&nbsp;&nbsp;&nbsp;└── details.html &nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Page de statistiques & dépenses

├── views.py &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Contrôleurs faisant le lien avec les templates

├── domain.py &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Logique métier appelée par les vues

└── data.py &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Accès aux données affichées dans les vues

---

## 📦 Installation & Setup

### 1. Prérequis
- Python 3.11 ou supérieur.
- [uv](https://github.com/astral-sh/uv) installé.

### 2. Installation
Clonez le dépôt et installez les dépendances :

```bash
uv sync
```

### 3. Initialisation de la base de données

Cette commande est obligatoire avant le premier lancement pour créer data.db :

```bash
uv run archilog init-db
```

## 🚦 Utilisation
Lancer le serveur (Production)

```bash
uv run granian --interface wsgi archilog:create_app --bind 127.0.0.1:8000
```

Accès : http://127.0.0.1:8000
Utilisation de l'API (Swagger)

Une fois le serveur lancé, la documentation interactive est disponible ici :
http://127.0.0.1:8000/apidoc/swagger
Commandes CLI (Interface terminal)

Le package installe un point d'entrée système archilog :

  Lister les cagnottes : 
  
  ```bash 
  uv run archilog get-all-mp
  ```

  Ajouter une dépense :
  
  ```bash 
  uv run archilog add-expense -m Voyage -p Clara -a 50
  ```

  Calculer les remboursements :
  
  ```bash 
  uv run archilog get-mp -m Voyage
  ```

## 🔐 Identifiants & Accès
Ce tableau récapitule les moyens de connexion pour les différentes interfaces de l'application Archilog.

| Interface | Type d'accès | Identifiant / Token | Mot de passe | Rôles / Permissions |
|:------------:|:-----------:|:-----------:|:-------------:|:-------------:|
| Web UI (Interface) | Login Basic | admin | admin | "Administrateur (Lecture, Ajout, Suppression)" |
| Web UI (Interface) | Login Basic | user | user | "Utilisateur (Lecture, Ajout uniquement)" |
| API REST | Bearer Token | mon-super-token-secret | N/A | Accès complet (Admin par défaut) |
| Base de données | Fichier Local | data.db | Aucun | Accès direct via SQLite |

## 🐳 Déploiement Docker

Le projet est conteneurisé pour un déploiement facilité :

### 1. Build du package

```bash
uv build
```

### 2. Build de l'image

```bash
docker build -t archilog-app .
```

### 3. Lancement

```bash
docker run -p 8080:8080 archilog-app
```

Course & examples : [https://kathode.neocities.org](https://kathode.neocities.org)
