import click

from archilog.data import (
    create_expense,
    delete_expense,
    delete_money_pot,
    get_all_money_pots,
    init_database,
)
from archilog.domain import get_money_pot_details

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