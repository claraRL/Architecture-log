import logging
from flask import Flask, flash, redirect, url_for
from archilog.config import config
from archilog.cli import cli

def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY

    app.cli.add_command(cli)

    # Configuration du Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("archilog.log"), # Trace dans un fichier
            logging.StreamHandler()              # Trace dans la console
        ]
    )

    from archilog.views import web_ui
    app.register_blueprint(web_ui)

    # Gestion globale des erreurs 500
    @app.errorhandler(500)
    def handle_internal_error(error):
        logging.exception("Erreur 500 détectée !") # Trace l'erreur complète
        flash("Oups ! Une erreur interne est survenue.", "error")
        return redirect(url_for("web_ui.home"))

    return app