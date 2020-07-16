from srd import add_params_as_attr
import os
from srd.ei import template
module_dir = os.path.dirname(os.path.dirname(__file__))


# wrapper to pick correct year
def program(year):
    """
    Fonction qui permet de sélectionner le programme par année.

    Parameters
    ----------
    year: int
        année (présentement entre 2016 et 2020)
    Returns
    -------
    class instance
        Une instance de la classe de l'année sélectionnée.
    """
    if year == 2016:
        p = program_2016()
    if year == 2017:
        p = program_2017()
    if year == 2018:
        p = program_2018()
    if year == 2019:
        p = program_2019()
    if year == 2020:
        p = program_2020()
    return p


# program for 2016, derived from template, only requires modify
# functions that change
class program_2016(template):
    """
    Version du programme de 2016.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ei/params/parameters_2016.csv')


# program for 2017, derived from template, only requires modify
# functions that change
class program_2017(template):
    """
    Version du programme de 2017.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ei/params/parameters_2017.csv')


# program for 2018, derived from template, only requires modify
# functions that change
class program_2018(template):
    """
    Version du programme de 2018.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ei/params/parameters_2018.csv')


# program for 2019, derived from template, only requires modify
# functions that change
class program_2019(template):
    """
    Version du programme de 2019.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ei/params/parameters_2019.csv')


# program for 2020, derived from template, only requires modify
# functions that change
class program_2020(template):
    """
    Version du programme de 2020.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ei/params/parameters_2020.csv')

    def compute_benefits_covid(self, p, hh):
        """
        Fonction pour calculer les prestations de l'assurance emploi
        qui remplaceraient la PCU (contrefactuel).

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            montant de la prestation
        """
        months_ei = max(p.months_cerb, p.months_cesb)
        if months_ei == 0 or p.prev_inc_work < self.min_inc_work:
            return
        else:
            inc_work_ei = min(self.max_earn_EI, p.prev_inc_work) / self.months_per_year

            for month in range(self.begin_april, self.begin_april + months_ei):
                if p.hours_month is None or p.hours_month[month] < self.max_hours_month:
                    clawback = self.claw_rate_low * p.inc_work_month[month]
                    add_amount = max(0, p.inc_work_month[month]
                                       - self.perc_cutoff_high * inc_work_ei)
                    clawback += self.claw_rate_high * add_amount
                    p.inc_ei += max(0, self.rate_benefits * inc_work_ei - clawback)
