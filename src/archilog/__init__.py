import logging
from flask import Flask, flash, redirect, url_for, jsonify
from archilog.cli import cli
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from werkzeug.security import generate_password_hash
from spectree import SpecTree, SecurityScheme
from archilog.config import config

auth = HTTPBasicAuth()
users = {
    "admin": {
        "password": generate_password_hash("admin"),
        "roles": ["admin"]
    },
    "user": {
        "password": generate_password_hash("user"),
        "roles": ["user"]
    }
}
auth_token = HTTPTokenAuth(scheme='Bearer')
api_spec = SpecTree(
    "flask",
    security_schemes=[
        SecurityScheme(
            name="bearer_token",
            data={"type": "http", "scheme": "bearer"}
        )
    ],
    security=[{"bearer_token": []}]
)
TOKENS = {"mon-super-token-secret": "admin"}

@auth_token.verify_token
def verify_token(token):
    if token in TOKENS:
        return TOKENS[token] # Retourne "admin" (le nom de l'utilisateur)
    return None

@auth_token.get_user_roles
def get_user_roles(payload):
    # Ici, payload est ce qui est retourné par verify_token (donc "admin")
    # On va chercher les rôles dans notre dictionnaire d'utilisateurs
    user_info = users.get(payload)
    if user_info:
        return user_info.get("roles", [])
    return []

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

    from archilog.views import api,web_ui
    app.register_blueprint(web_ui)
    app.register_blueprint(api, url_prefix="/api")


    # Gestion globale des erreurs 500
    @app.errorhandler(500)
    def handle_internal_error(error):
        logging.exception("Erreur 500 détectée !") # Trace l'erreur complète
        flash("Oups ! Une erreur interne est survenue.", "error")
        return redirect(url_for("web_ui.home"))

    @app.errorhandler(404)
    def api_not_found(error):
        return jsonify({"error": "Ressource non trouvée"}), 404

    @app.errorhandler(400)
    def handle_api_error(error):
        return jsonify({"error": str(error)}), 400

    @app.errorhandler(500)
    def api_internal_error(error):
        return jsonify({"error": "Erreur interne du serveur"}), 500

    api_spec.register(app)
    return app