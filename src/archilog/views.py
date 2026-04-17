import logging
from archilog.data import (
    create_expense,
    delete_money_pot,
    get_all_money_pots,
    add_members_to_pot,
    delete_expense_by_id,
    get_members,
    get_expense_by_id,
)
from archilog.domain import get_money_pot_details
from flask import Blueprint, render_template, request, redirect, url_for, flash
from archilog.forms import ExpenseForm, MoneyPotForm

web_ui = Blueprint("web_ui", __name__)

@web_ui.route("/")
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
def view_pot(name: str):
    pot, transactions = get_money_pot_details(name)
    liste_membres = get_members(name)

    # Calculs
    total_amount = sum(elt.amount for elt in pot.expenses)
    nb_membres = len(liste_membres)
    part_individuelle = round(total_amount / nb_membres if nb_membres > 0 else 0, 2)
    totaux_par_membre = {membre: 0.0 for membre in liste_membres}

    for depense in pot.expenses:
        if depense.paid_by in totaux_par_membre:
            totaux_par_membre[depense.paid_by] += depense.amount

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
def create_pot():
    form = MoneyPotForm()
    if form.validate_on_submit():
        # On récupère les données propres depuis le formulaire
        pot_name = form.pot_name.data
        paid_by = form.paid_by.data
        amount = form.amount.data

        # Les membres sont toujours récupérés via request car ils sont dynamiques en JS
        members = request.form.getlist('members[]')

        create_expense(pot_name, paid_by, amount)
        add_members_to_pot(pot_name, members)

        logging.info(f"Cagnotte '{pot_name}' créée avec succès.")
        return redirect(url_for("web_ui.view_pot", name=pot_name))

    # Si la validation échoue (ex: nom trop court)
    flash("Erreur lors de la création : vérifiez les informations saisies.", "error")
    return redirect(url_for("web_ui.home"))

@web_ui.route("/expense/delete/<int:expense_id>", methods=["POST"])
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
def delete_pot(cagnotte_name):
    delete_money_pot(cagnotte_name)

    return redirect(url_for("web_ui.home"))


@web_ui.route("/pot/<name>/add_expense", methods=["POST"])
def add_expense_route(name: str):
    liste_membres = get_members(name)
    form = ExpenseForm()
    form.paid_by.choices = [(m, m) for m in liste_membres]
    if form.validate_on_submit():
        # Données validées !
        create_expense(name, form.paid_by.data, form.amount.data)
        flash(f"Dépense de {form.amount.data}€ ajoutée !", "success")
        return redirect(url_for("web_ui.view_pot", name=name))

    # Si validation échoue
    print(form.errors)
    flash(f"Erreur : {form.errors.get('paid_by', ['Montant invalide'])[0]}", "error")
    return redirect(url_for("web_ui.view_pot", name=name))

@web_ui.route("/test-crash")
def crash():
    return 1 / 0  # Division par zéro -> Erreur 500