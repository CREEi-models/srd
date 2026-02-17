"""
Utilitaires de formatage pour l'affichage des resultats.
"""


def fmt_currency(value):
    """Formate un montant en dollars avec 2 decimales et separateur de milliers."""
    if value is None:
        return "0.00 $"
    return f"{value:,.2f} $"


def fmt_int(value):
    """Formate un entier avec separateur de milliers."""
    if value is None:
        return "0"
    return f"{value:,.0f}"


def safe_value(value, default=0):
    """Retourne la valeur ou un defaut si None."""
    if value is None:
        return default
    if isinstance(value, dict):
        return value.get("amount", default)
    return value
