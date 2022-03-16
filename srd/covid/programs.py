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
    if year == 2022:
        p = program_2022()
    return p
class program_2020(template):
    """
    Version du programme de 2020.

    Calcul des prestations d'urgence liées à la COVID-19: la Prestation canadienne d'urgence (PCU), la Prestation canadienne d'urgence pour les étudiants (PCUE), le Programme incitatif pour la rétention des travailleurs essentiels (PIRTE) et la Prestation canadienne de la relance économique (PCRE).

    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/covid/params/measures_2020.csv')
class program_2021(program_2020):
    """
    Version du programme de 2021.

    Calcule principalement la Prestation canadienne de la relance économique (PCRE)
    """

    def __init__(self):
        add_params_as_attr(self, module_dir + "/covid/params/measures_2021.csv")

    def compute_cerb(self, p):
        """
        Fonction pour le calcul de la PCU.

        Calcule la PCU en fonction du nombre de blocs de 4 semaines (mois) pour lesquels la prestation est demandée.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant de la PCU.
        """
        return 0

    def compute_cesb(self, p, hh):
        """
        Fonction pour le calcul de la PCUE.

        Calcule la PCUE en fonction de la prestation mensuelle à laquelle l'individu a droit et du nombre de blocs de 4 semaines (mois) pour lesquels la prestation est demandée.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant de la PCUE.
        """
        return 0

    def compute_monthly_cesb(self, p, hh):
        """
        Calcule le montant mensuel de la PCUE en fonction du statut (invalidité, dépendants).

        Parameters
        ----------

        Returns
        -------
        float
            Prestation mensuelle de PCUE.
        """

        return 0

    def compute_iprew(self, p):
        """
        Fonction pour le calcul du PIRTE.

        Calcule la PIRTE pour la période de 16 semaines (4 mois) si le travailleur est admissible.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant de PIRTE pour les 16 semaines.
        """
        return 0

class program_2022(program_2021):
    """
    Version du programme de 2022.

    Calcule principalement la Prestation canadienne de la relance économique (PCRE)
    """

    def __init__(self):
        add_params_as_attr(self, module_dir + "/covid/params/measures_2022.csv")