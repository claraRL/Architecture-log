import logging
from archilog.data import (
    create_expense,
    create_money_pot,
    delete_money_pot,
    get_all_money_pots,
    add_members_to_pot,
    delete_expense_by_id,
    get_members,
    get_expense_by_id,
)
from archilog.domain import get_money_pot_details
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from archilog.forms import ExpenseForm, MoneyPotForm
from werkzeug.security import check_password_hash
from archilog import auth, users, api_spec, auth_token
from pydantic import BaseModel, Field

web_ui = Blueprint("web_ui", __name__)
api = Blueprint("api", __name__)


class PotSchema(BaseModel):
    name: str = Field(min_length=3, max_length=50, description="Nom de la cagnotte")

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users[username]["password"], password):
        return username
    return None


@auth.get_user_roles
def get_user_roles(username):
    return users.get(username, {}).get("roles", [])

@web_ui.route("/")
@auth.login_required
def home():
    cagnottes = get_all_money_pots()
    cagnottes_avec_stats = []

    for m in cagnottes:
        # On récupère les détails pour avoir accès à .expenses
        pot, transactions = get_money_pot_details(m.name)

        # On crée un petit dictionnaire avec toutes les infos nécessaires
        cagnottes_avec_stats.append({
            'objet': m.name,
            'nb_depenses': len(pot.expenses)  # On compte les dépenses réelles
        })

    form = MoneyPotForm()

    return render_template("home.html", pots=cagnottes, cagnottes=cagnottes_avec_stats, form=form)

@web_ui.route("/pot/<name>")
@auth.login_required
def view_pot(name: str):
    pot, transactions = get_money_pot_details(name)
    liste_membres = get_members(name)

    # Calculs
    total_amount = sum(elt.amount for elt in pot.expenses)
    nb_membres = len(liste_membres)
    part_individuelle = round(total_amount / nb_membres if nb_membres > 0 else 0, 2)
    totaux_par_membre = {m: 0.0 for m in liste_membres}
    for e in pot.expenses:
        clean_name = e.paid_by.strip()
        if clean_name in totaux_par_membre:
            totaux_par_membre[clean_name] += e.amount
        else:
            # Si c'est un nom inconnu, on ne fait rien (cela évite le crash)
            continue

    # AJOUT DU FORMULAIRE
    form = ExpenseForm()
    form.paid_by.choices = [(m, m) for m in liste_membres]

    return render_template(
        "details.html",
        pot=pot,
        transactions=transactions,
        membres=liste_membres,
        total_general=total_amount,
        part_individuelle=part_individuelle,
        totaux_par_membre=totaux_par_membre,
        nb_membres=nb_membres,
        form=form
    )


@web_ui.route("/pot/<name>/add", methods=["POST"])
@auth.login_required
def add_expense_to_pot(name: str):
    # On récupère les données envoyées par le formulaire
    paid_by = request.form.get("paid_by")
    amount_str = request.form.get("amount")

    # On convertit le montant en nombre décimal (float)
    amount = float(amount_str)

    # 1. On enregistre la dépense dans la base de données
    create_expense(name, paid_by, amount)

    # 2. On renvoie l'utilisateur sur la page des détails de la cagnotte
    return redirect(url_for("web_ui.view_pot", name=name))

@web_ui.route("/pot/create", methods=["POST"])
@auth.login_required(role="admin")
def create_pot():
    form = MoneyPotForm()
    if form.validate_on_submit():
        # On récupère les données propres depuis le formulaire
        pot_name = form.pot_name.data.strip()
        paid_by = form.paid_by.data.strip()
        amount = form.amount.data

        # Les membres sont toujours récupérés via request car ils sont dynamiques en JS
        members_r = request.form.getlist('members[]')

        # On crée une liste propre : sans espaces et sans doublons
        # On ajoute le payeur à la liste des membres pour être sûr
        members_list = [m.strip() for m in members_r if m.strip()]
        members_list.append(paid_by)

        # On utilise set() pour supprimer les doublons (ex: si Harry était dans les deux)
        members = list(set(members_list))

        success = create_money_pot(pot_name)

        if success:
            add_members_to_pot(pot_name, members)
            create_expense(pot_name, paid_by, amount)
            flash(f"Cagnotte '{pot_name}' créée !", "success")
            return redirect(url_for("web_ui.view_pot", name=pot_name))
        else:
            flash(f"La cagnotte '{pot_name}' existe déjà !", "error")
            return redirect(url_for("web_ui.view_pot", name=pot_name))

    # Si la validation échoue (ex: nom trop court)
    flash("Erreur lors de la création : vérifiez les informations saisies.", "error")
    return redirect(url_for("web_ui.home"))

@web_ui.route("/expense/delete/<int:expense_id>", methods=["POST"])
@auth.login_required(role="admin")
def delete_expense_route(expense_id: int):
    # On a besoin de savoir de quel pot vient la dépense pour pouvoir y retourner après la suppression.
    # On récupère donc l'info avant de supprimer.
    expense = get_expense_by_id(expense_id)
    pot_name = expense.money_pot

    # Appelle fonction de suppression
    delete_expense_by_id(expense_id)

    # On redirige vers la page du pot
    return redirect(url_for("web_ui.view_pot", name=pot_name))

@web_ui.route("/pot/delete/<cagnotte_name>", methods=["POST"])
@auth.login_required(role="admin")
def delete_pot(cagnotte_name):
    delete_money_pot(cagnotte_name)

    return redirect(url_for("web_ui.home"))


@web_ui.route("/pot/<name>/add_expense", methods=["POST"])
@auth.login_required
def add_expense_route(name: str):
    form = ExpenseForm()
    liste_membres = get_members(name)
    form.paid_by.choices = [(m, m) for m in liste_membres]

    if form.validate_on_submit():
        try:
            # On tente d'exécuter la logique métier
            create_expense(name, form.paid_by.data, form.amount.data)
            flash("Dépense ajoutée !", "success")
        except Exception as e:
            # Si une erreur survient (ex: KeyError), on l'attrape ici
            flash(f"Erreur technique : {str(e)}", "error")
    else:
        # Si le formulaire est invalide (ex: texte au lieu de nombre)
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Erreur dans le champ {field} : {error}", "error")

    return redirect(url_for("web_ui.view_pot", name=name))

@web_ui.route("/test-crash")
@auth.login_required(role="admin")
def crash():
    return 1 / 0  # Division par zéro → Erreur 500


@api.get("/pots")
@api_spec.validate(tags=["api"])
@auth_token.login_required
def get_pots():
    """Read: Liste toutes les cagnottes"""
    cagnottes = get_all_money_pots()
    return jsonify([{"name": c.name} for c in cagnottes])

@api.post("/pots")
@api_spec.validate(json=PotSchema, tags=["api"], security={"bearer_token": []})
@auth_token.login_required(role="admin")
def post_pot(json: PotSchema):
    """Create: Crée une nouvelle cagnotte"""
    create_money_pot(json.name)
    return {"message": f"Cagnotte '{json.name}' créée avec succès"}, 201

@api.delete("/pots/<name>")
@api_spec.validate(tags=["api"])
@auth_token.login_required(role="admin")
def delete_pot_api(name: str):
    """Delete: Supprimer une cagnotte"""
    delete_money_pot(name)
    return {"message": "Cagnotte supprimée"}, 200