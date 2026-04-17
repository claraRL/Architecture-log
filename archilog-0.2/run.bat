@echo off
:: =================================================================
:: SCRIPT DE LANCEMENT AUTOMATISÉ
:: =================================================================
:: Ce script simule le comportement d'un environnement de production
:: en chargeant dynamiquement les variables de configuration.
::
:: 1. LECTURE DU FICHIER .ENV : Le script parcourt 'dev.env' pour
::    extraire ARCHILOG_DATABASE_URL et ARCHILOG_DEBUG.
::
:: 2. INJECTION DANS L'ENVIRONNEMENT : Chaque ligne est passée à la
::    commande 'set', permettant à Python (via os.getenv) de lire
::    ces réglages sans qu'ils ne soient écrits en dur dans le code.
::
:: 3. DÉMARRAGE DE LA FACTORY : On lance Flask en pointant vers le
::    package 'archilog'. Cela exécute create_app() dans __init__.py.
:: =================================================================

:: Boucle pour charger chaque ligne de dev.env comme variable d'environnement
for /f "tokens=*" %%i in (dev.env) do set %%i

uv run flask --app archilog run --debug

pause