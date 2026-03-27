# Archilog

  Permet de créer des cagnottes, d'y ajouter ou supprimer des participants, de calculer le total de la cagnotte et qui doit rembourser qui

## 📋 Table des matières

* [Présentation](#-presentation)
* [Fonctionnalités](#-fonctionnalites)
* [Installation](#-installation)

## 🚀 Présentation

Projet développer dans le cadre du cours d'architecture logiciel de deuxieme année de BUT informatique. L'idée est de développer une application permettant la gestion de cagnotte.
Evalué sur les fonctionnalités, l'esprit du code et l'architecture du logiciel.

## ✨ Fonctionnalités

* Création d'une cagnotte si le nom entrer n'existe pas encore dans la base de donnée
* Suppression de la cagnotte
* Ajouter à une dépense et créer une dépense si l'utilisateur n'a pas encore participé à la cagnotte
* Supprimer une dépense
* Faire l'équilibre en calculant les dépenses de chaqu'un 

## 🛠️ Installation

installer archilog sur votre pc, ouvrir un terminal à la racine puis :
```
$ uv sync
```

Pour utiliser click et tester les fonctions via le terminal :
```
$ uv run archilog
Usage: archilog [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
```
Pour utiliser flask et accéder à l'interface graphique sur votre navigateur :
```
uv run flask --app archilog.views --debug run  
```

Cours: https://kathode.neocities.org
