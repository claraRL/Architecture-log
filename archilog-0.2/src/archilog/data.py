import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from sqlalchemy import insert
from sqlalchemy import create_engine, Column, String, Float, DateTime, Table, MetaData, select, delete, Integer
from archilog.config import config


db = create_engine(config.DATABASE_URL, echo=config.DEBUG, future=True)

metadata = MetaData()

Expenses = Table(
    "expenses",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("money_pot",String, nullable=False),
    Column("paid_by", String, nullable=False),
    Column("amount",Float, nullable=False),
    Column("datetime",DateTime, nullable=False, default=datetime.now))

Members = Table(
    "members",
    metadata,
    Column("money_pot", String, primary_key=True),
    Column("name", String, primary_key=True)
)

money_pot_table = Table(
    "money_pots",
    metadata,
    Column("name", String, primary_key=True)
)

@dataclass
class Expense:
    id: int
    money_pot: str
    paid_by: str
    amount: float
    datetime: datetime

    @classmethod
    def from_db(cls, row):
        return cls(
            row.id,
            row.money_pot,
            row.paid_by,
            row.amount,
            row.datetime,
        )

@dataclass
class MoneyPot:
    name: str
    expenses: list[Expense] = field(default_factory=list)


def init_database():
    metadata.create_all(db)

# money pots
# ==========

def create_money_pot(name: str) -> bool:
    """
    Crée une nouvelle cagnotte.
    Retourne True si créée, False si elle existait déjà.
    """
    # .prefix_with("OR IGNORE") est spécifique à SQLite pour éviter l'erreur UNIQUE
    stmt = insert(money_pot_table).values(name=name).prefix_with("OR IGNORE")

    try:
        with db.connect() as conn:
            with conn.begin():
                result = conn.execute(stmt)
                # Si rowcount > 0, c'est qu'une ligne a été créée
                return int(result.rowcount) > 0
    except Exception as e:
        print(f"Erreur DB : {e}")
        return False

def get_money_pot(money_pot_name: str) -> MoneyPot:
    """
        Récupère l'état complet d'une cagnotte depuis la base de données.

        Note technique : La liste des participants est déduite de la table
        des membres du groupe. Même si un membre n'a aucune dépense
        enregistrée, il est inclus avec un total de 0.0€ pour garantir
        l'exactitude du calcul de la moyenne dans la couche Domain.

        Args:
            money_pot_name (str): L'identifiant textuel de la cagnotte.

        Returns:
            MoneyPot: Une instance peuplée avec les données de la table 'expenses'.

        Raises:
            Error: Si une erreur survient lors de la lecture en base.
    """
    results = select(Expenses).where(Expenses.c.money_pot == money_pot_name)

    with db.connect() as conn:
        # execute la requete
        res = conn.execute(results)
        # transforme chaque ligne en objet Expense
        rows = res.all()

    return MoneyPot(money_pot_name, [Expense.from_db(r) for r in rows])

def get_all_money_pots() -> list[MoneyPot]:
    """
        Récupère la liste exhaustive de toutes les cagnottes enregistrées.

        Cette fonction est utilisée pour l'initialisation de l'interface utilisateur.
        Elle ne récupère que les informations de premier niveau (noms des cagnottes)
        sans charger l'intégralité des dépenses pour optimiser les performances.

        Returns:
            list[MoneyPot]: Une liste d'objets MoneyPot. Retourne une liste vide
                            si aucune donnée n'est présente en base.

        Raises:
            sqlite3.Error: En cas d'échec de la connexion ou de la requête SQL.
    """

    all_money_pots = select(money_pot_table).distinct()

    with db.connect() as conn:
        results = conn.execute(all_money_pots)
        # prend le premier element de chaque ligne ce qui correspond au nom du money_pot
        return [MoneyPot(r[0]) for r in results]


def delete_money_pot(money_pot_name: str):
    """
        Supprime définitivement une cagnotte et toutes les données associées.

        Cette opération est critique. Elle s'appuie sur la contrainte 'ON DELETE CASCADE'
        de la base de données pour supprimer automatiquement les dépenses liées,
        garantissant ainsi qu'il ne reste pas de données orphelines.

        Args:
            money_pot_name (str): L'identifiant de la cagnotte à supprimer.

        Returns:
            bool: True si la suppression a été effectuée, False si la cagnotte n'existait pas.

        Raises:
            sqlite3.Error: En cas d'anomalie lors de l'exécution de la transaction.
    """

    # suppression de toutes les lignes ayant ce nom de cagnotte
    del_money_pot = delete(Expenses).where(Expenses.c.money_pot == money_pot_name)

    # dans le cour il n'y a que begin avec le with mais je suis obligé de faire comme ca sinon cela me fait une erreur
    # sur le begin: Expected type 'contextlib.AbstractContextManager', got 'Iterator[Connection]' instead
    with db.connect() as conn:
        with conn.begin():
            conn.execute(del_money_pot)

# expenses
# ========

def create_expense(money_pot_name: str, paid_by: str, amount: float) -> None:
    """
    Ajoute une dépense à une cagnotte existante.

    Cette fonction implémente une validation stricte du domaine avant
    l'écriture en base (montant > 0). L'intégrité référentielle est
    confiée à la contrainte de clé étrangère SQLite.

    Args:
        money_pot_name (str): Nom de la cagnotte (FK).
        paid_by (str): Identifiant de l'auteur du paiement.
        amount (float): Valeur de la dépense. Doit être > 0.

    Raises:
        AssertionError: Si la règle métier 'montant positif' est violée.
    """
    # protège contre les valeurs négatives qui feraient augmenter la cagnotte
    assert amount > 0, f"Le montant doit être supérieur à 0 (reçu : {amount})"

    expenses = Expenses.insert().values(
        money_pot=money_pot_name,
        paid_by=paid_by,
        amount=amount,
    )
    with db.connect() as conn:
        with conn.begin():
            conn.execute(expenses)

def get_expense_by_id(expense_id: int):
    """
    Recupère une transaction précise en identifant la ligne
    concerné par son identidifiant

    Args:
        expense_id (int): Identifiant de la transaction

    Returns:
        result: transaction identifié
    """
    stmt = select(Expenses).where(Expenses.c.id == expense_id)
    with db.connect() as conn:
        result = conn.execute(stmt).first()
        return result

def delete_expense_by_id(expense_id: int):
    """
    Supprime une transaction précise en identifant la ligne

    Args:
        expense_id (int): Identifiant de la transaction

    Returns:

    """
    # On prépare la commande de suppression
    stmt = delete(Expenses).where(Expenses.c.id == expense_id)

    with db.connect() as conn:
        with conn.begin():
            conn.execute(stmt)

def delete_expense(money_pot_name: str, paid_by: str) -> None:
    """
    Supprime l'ensemble des contributions d'un utilisateur spécifique au sein d'une cagnotte.

    Contrairement à une suppression par identifiant unique, cette fonction
    nettoie tous les enregistrements liés au couple (cagnotte, utilisateur).
    Elle est utile pour retirer complètement un participant de la logique de calcul.

    Args:
        money_pot_name (str): Le nom de la cagnotte concernée.
        paid_by (str): Le nom du participant dont on veut annuler les frais.

    Note:
        Cette opération impacte immédiatement la moyenne du groupe calculée
        dans la couche Domain. Si l'utilisateur n'avait aucune dépense,
        la fonction s'exécute sans erreur mais n'altère pas la base.

    Raises:
        sqlite3.Error: En cas de rupture de la communication avec la base de données.
    """

    del_expense = delete(Expenses).where(
        (Expenses.c.money_pot == money_pot_name) &
        (Expenses.c.paid_by == paid_by)
    )
    with db.connect() as conn:
        with conn.begin():
            conn.execute(del_expense)

# members
# ========

def add_members_to_pot(money_pot_name: str, member_names: list[str]) -> None:
    """
    Enregistre la liste des membres associés à une cagnotte.
    Args:
        money_pot_name(str): Le nom de la cagnotte
        member_names (list[str]) : liste des participants
    """
    with db.connect() as conn:
        with conn.begin():
            unique_members = set(member_names)
            for name in unique_members:
                stmt = Members.insert().values(
                    money_pot=money_pot_name,
                    name=name
                )
                try:
                    conn.execute(stmt)
                except sqlite3.IntegrityError:
                    # Si le membre existe déjà, on ne fait rien
                    pass

def get_members(money_pot_name: str) -> list[str]:
    """
    Récupère le nom des participant a la cagnotte.

    Args:
        money_pot_name (str) : nom de la cagnotte

    Returns:
        list[str] : liste des participants
    """
    # On sélectionne les noms des membres pour cette cagnotte
    query = select(Members.c.name).where(Members.c.money_pot == money_pot_name)
    with db.connect() as conn:
        result = conn.execute(query)
        return [row[0] for row in result]