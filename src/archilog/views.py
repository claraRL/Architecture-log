import click

from archilog.data import (
    create_expense,
    delete_expense,
    delete_money_pot,
    get_all_money_pots,
    init_database,
    add_members_to_pot,
    delete_expense_by_id,
    get_members,
    get_expense_by_id,
)
from archilog.domain import get_money_pot_details
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
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
    return render_template("home.html", pots=cagnottes, cagnottes=cagnottes_avec_stats)

@app.route("/pot/<name>")
def view_pot(name: str):
    # On récupère les détails (dépenses + transactions)
    pot, transactions = get_money_pot_details(name)

    # On récupère la liste des membres pour le formulaire d'ajout
    liste_membres = get_members(name)
    total_amount = 0
    for elt in pot.expenses:
        total_amount += elt.amount
    # On compte le nombre d'éléments dans la liste des membres
    nb_membres = len(liste_membres)

    # On calcule la part (en vérifiant qu'il y a au moins un membre pour éviter une division par zéro !)
    part_individuelle = round(total_amount / nb_membres if nb_membres > 0 else 0, 2)

    return render_template("details.html",
                           pot=pot,
                           transactions=transactions,
                           membres=liste_membres,
                           total=total_amount,
                           part_individuelle=part_individuelle,
                           nb_membres=nb_membres,)


@app.route("/pot/<name>/add", methods=["POST"])
def add_expense_to_pot(name: str):
    # On récupère les données envoyées par le formulaire
    paid_by = request.form.get("paid_by")
    amount_str = request.form.get("amount")

    # On convertit le montant en nombre décimal (float)
    amount = float(amount_str)

    # 1. On enregistre la dépense dans la base de données
    create_expense(name, paid_by, amount)

    # 2. On renvoie l'utilisateur sur la page des détails de la cagnotte
    return redirect(url_for("view_pot", name=name))

@app.route("/pot/create", methods=["POST"])
def create_pot():
    pot_name = request.form.get("pot_name")
    paid_by = request.form.get("paid_by")
    amount = float(request.form.get("amount"))

    # On récupère la liste des membres
    members = request.form.getlist('members[]')

    # Créer la dépense
    create_expense(pot_name, paid_by, amount)

    # Enregistrer les membres
    add_members_to_pot(pot_name, members)

    return redirect(url_for("view_pot", name=pot_name))

@app.route("/expense/delete/<int:expense_id>", methods=["POST"])
def delete_expense_route(expense_id: int):
    # On a besoin de savoir de quel pot vient la dépense pour pouvoir y retourner après la suppression.
    # On récupère donc l'info avant de supprimer.
    expense = get_expense_by_id(expense_id)
    pot_name = expense.money_pot

    # Appelle fonction de suppression
    delete_expense_by_id(expense_id)

    # On redirige vers la page du pot
    return redirect(url_for("view_pot", name=pot_name))

@app.route("/pot/delete/<cagnotte_name>", methods=["POST"])
def delete_pot(cagnotte_name):
    delete_money_pot(cagnotte_name)

    return redirect(url_for("home"))

@click.group()
def cli():
    pass

@cli.command(help="Initialize the database.")
def init_db():
    init_database()

# money pots
# ==========

@cli.command(help="Get the list of all money pots.")
def get_all_mp():
    for m in get_all_money_pots():
        click.echo(m.name)


@cli.command(help="Get details of a money pot.")
@click.option("-m", "--money-pot", required=True)
def get_mp(money_pot: str):
    mp, transactions = get_money_pot_details(money_pot)

    click.echo("The money pot contains:")
    for e in mp.expenses:
        click.echo(f"  {e.paid_by} : {e.amount}€ ({e.datetime})")

    click.echo("To balance the money pot:")
    if transactions:
        for t in transactions:
            click.echo(f"  {t.sender} must send {t.amount}€ to {t.receiver}.")
    else:
        click.echo("  Nothing to do.")


@cli.command(help="Delete a money pot with all associated expenses.")
@click.option("-m", "--money-pot", required=True)
def delete_mp(money_pot: str):
    delete_money_pot(money_pot)


# expenses
# ========


@cli.command(help="Add an expense to a money pot, create a money pot if needed.")
@click.option("-m", "--money-pot", required=True)
@click.option("-p", "--paid-by", required=True)
@click.option("-a", "--amount", type=float, required=True)
def add_expense(money_pot: str, paid_by: str, amount: float):
    create_expense(money_pot, paid_by, amount)


@cli.command(
    help="Remove an expense from a money pot, delete the money pot if no more expense."
)
@click.option("-m", "--money-pot", required=True)
@click.option("-p", "--paid-by", required=True)
def remove_expense(money_pot: str, paid_by: str):
    delete_expense(money_pot, paid_by)


if __name__ == "__main__":
    cli() # ou app.run()