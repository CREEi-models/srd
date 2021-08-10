from srd import add_params_as_attr
import os
from srd.covid import template
module_dir = os.path.dirname(os.path.dirname(__file__))

def program(year):
    """
    Fonction qui permet de sélectionner le programme par année.

    Parameters
    ----------
    year: int
        année (présentement entre 2020 et 2021)
    Returns
    -------
    class instance
        Une instance de la classe de l'année sélectionnée.
    """
    if year == 2020:
        p = program_2020()
    if year == 2021:
        p = program_2021()
    return p
class program_2020(template):
    """
    Version du programme de 2020.

    Calcul des prestations d'urgence liées à la COVID-19: la Prestation canadienne d'urgence (PCU), la Prestation canadienne d'urgence pour les étudiants (PCUE), le Programme incitatif pour la rétention des travailleurs essentiels (PIRTE) et la Prestation canadienne de la relance économique (PCRE).

    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/covid/params/covid.csv')
        add_params_as_attr(self, module_dir + '/covid/params/params_2020.csv')
class program_2021(program_2020):
    """
    Version du programme de 2021.

    Calcule principalement la Prestation canadienne de la relance économique (PCRE)
    """

    def __init__(self):
        add_params_as_attr(self, module_dir + "/covid/params/params_2021.csv")