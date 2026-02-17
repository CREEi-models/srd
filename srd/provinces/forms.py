"""
Formulaires d'impôt provinciaux simplifiés (version barebones).

Ce module contient les formulaires simplifiés pour toutes les provinces et territoires.
Pour QC et ON, des modèles complets existent aussi dans srd/quebec/ et srd/ontario/.

Chaque province a uniquement:
- Les paliers d'imposition (tax brackets)
- Le montant personnel de base (basic personal amount)

Codes des provinces/territoires:
- qc: Québec (version barebones, modèle complet disponible dans srd/quebec/)
- on: Ontario (version barebones, modèle complet disponible dans srd/ontario/)
- ab: Alberta
- bc: Colombie-Britannique
- sk: Saskatchewan
- mb: Manitoba
- nb: Nouveau-Brunswick
- ns: Nouvelle-Écosse
- pe: Île-du-Prince-Édouard
- nl: Terre-Neuve-et-Labrador
- nt: Territoires du Nord-Ouest
- nu: Nunavut
- yt: Yukon
"""
import os
from srd import add_params_as_attr, add_schedule_as_attr
from srd.provinces.template import template

module_dir = os.path.dirname(os.path.dirname(__file__))

# Liste des provinces/territoires disponibles (incluant QC et ON en version barebones)
PROVINCES = ['qc', 'on', 'ab', 'bc', 'sk', 'mb', 'nb', 'ns', 'pe', 'nl', 'nt', 'nu', 'yt']

# Années disponibles par province
YEARS_AVAILABLE = {
    'qc': [2023],
    'on': [2023],
    'ab': [2023],
    'bc': [2023],
    'sk': [2023],
    'mb': [2023],
    'nb': [2023],
    'ns': [2023],
    'pe': [2023],
    'nl': [2023],
    'nt': [2023],
    'nu': [2023],
    'yt': [2023],
}


def form(prov, year):
    """
    Fonction qui permet de sélectionner le formulaire d'impôt provincial par province et année.

    Parameters
    ----------
    prov: str
        code de la province (ab, bc, sk, mb, nb, ns, pe, nl, nt, nu, yt)
    year: int
        année fiscale

    Returns
    -------
    class instance
        Une instance du formulaire pour la province et l'année sélectionnées.

    Raises
    ------
    ValueError
        Si la province n'est pas disponible ou si l'année n'est pas supportée.
    """
    prov = prov.lower()
    
    if prov not in PROVINCES:
        raise ValueError(f"Province '{prov}' non disponible. Provinces disponibles: {PROVINCES}")
    
    if year not in YEARS_AVAILABLE[prov]:
        raise ValueError(f"Année {year} non disponible pour {prov}. Années disponibles: {YEARS_AVAILABLE[prov]}")
    
    return ProvincialForm(prov, year)


class ProvincialForm(template):
    """
    Formulaire d'impôt provincial simplifié (barebones).
    
    Parameters
    ----------
    prov: str
        code de la province
    year: int
        année fiscale
    """
    def __init__(self, prov, year):
        self.prov = prov
        self.year = year
        add_params_as_attr(self, f"{module_dir}/provinces/params/{prov}_measures_{year}.csv")
        add_schedule_as_attr(self, f"{module_dir}/provinces/params/{prov}_schedule_{year}.csv")
