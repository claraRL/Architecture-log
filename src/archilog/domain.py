from dataclasses import dataclass

from archilog.data import MoneyPot, get_money_pot, get_members

@dataclass
class MeanDeviation:
    """
        Représente l'état financier d'un participant par rapport à la moyenne.

        Attributs:
            name (str) : Nom du participant.
            amount (float) : Écart à la moyenne.
                - Positif (+) : La personne a trop payé et doit être remboursée.
                - Négatif (-) : La personne n'a pas assez payé et a une dette.
    """
    name: str
    amount: float


@dataclass
class Transaction:
    """
        Modélise un transfert d'argent entre deux membres du groupe.

        Cette entité est le résultat final de l'algorithme d'équilibrage.

        Attributs:
            sender (str) : Nom de la personne qui donne l'argent (le débiteur).
            receiver (str) : Nom de la personne qui reçoit l'argent (le créditeur).
            amount (float) : Somme exacte à transférer.
    """
    sender: str
    receiver: str
    amount: float


def get_money_pot_details(money_pot_name: str) -> tuple[MoneyPot, list[Transaction]]:
    """
    Récupère l'état d'une cagnotte et calcule les flux financiers de régularisation.

    Cette fonction fait le pont entre la couche d'accès aux données et la logique
    métier. Elle agrège les informations brutes pour fournir une vue exploitable.

    Args:
        money_pot_name (str) : L'identifiant unique (nom) de la cagnotte en base.

    Returns:
        tuple[MoneyPot, list[Transaction]] : Un tuple contenant :
            - L'objet MoneyPot (modèle de données complet).
            - Une liste d'objets Transaction (résultat de l'algorithme d'équilibrage).
    """
    pot = get_money_pot(money_pot_name)
    members = get_members(money_pot_name)

    # On lance le calcul (Logic)
    transactions = compute_transactions(pot, members)

    return pot, transactions


# pure function, easily testable
def compute_transactions(money_pot: MoneyPot, members: list[str]) -> list[Transaction]:
    """
    Exécute l'algorithme de compensation pour équilibrer les comptes du groupe.

    L'algorithme calcule l'écart à la moyenne pour chaque participant, puis
    minimise le nombre de transferts nécessaires (complexité O(n)) pour
    solder les dettes.

    Args:
        members (list[str]) : liste des participants
        money_pot (MoneyPot) : L'instance contenant les dépenses agrégées.

    Returns:
        list[Transaction] : Une liste d'objets Transaction indiquant qui doit payer quoi à qui.
    """
    if not money_pot.expenses:
        return []

    totals = {name.strip(): 0.0 for name in members}

    # Ajout des dépenses réelles
    for e in money_pot.expenses:
        payer_name = e.paid_by.strip()
        if payer_name in totals:
            totals[payer_name] += e.amount
        else:
            # Si le nom n'est pas dans la liste des membres, on l'ignore au lieu de planter
            print(f"Attention: {payer_name} n'est pas un membre de la cagnotte.")

    # Calcul de la moyenne sur le nombre réel de membres
    total_general = sum(totals.values())
    nb_participants = len(members)
    mean = total_general / nb_participants

    # On calcule l'écart à la moyenne pour chaque personne
    mean_deviations = [
        MeanDeviation(name, round(amount - mean, 2))
        for name, amount in totals.items()
    ]
    transactions: list[Transaction] = []

    # abs permet d'avoir un montant positif a manipuler
    debtors = [[d.name, abs(d.amount)] for d in mean_deviations if d.amount < 0]
    creditors = [[d.name, d.amount] for d in mean_deviations if d.amount > 0]
    while debtors and creditors:
        debtor = debtors[0]  # [nom, montant restant a payer]
        creditor = creditors[0]  # [nom, montant restant a recevoir]

        # Le montant de la transaction est le plus petit des deux
        amount = min(debtor[1], creditor[1])

        # On crée l'objet Transaction
        if amount > 0:
            transactions.append(Transaction(
                sender=debtor[0],
                receiver=creditor[0],
                amount=round(amount, 2)
            ))

        # On met à jour les montants restants
        debtor[1] -= amount
        creditor[1] -= amount

        # Si le montant restant est (presque) nul, on retire la personne de la liste
        # empeche les floats a 0.00000001 de bloquer
        if debtor[1] < 0.01:
            debtors.pop(0)
        if creditor[1] < 0.01:
            creditors.pop(0)

    return transactions


