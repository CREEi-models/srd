import os
from srd import add_params_as_attr, add_schedule_as_attr
from srd.ontario import template

module_dir = os.path.dirname(os.path.dirname(__file__))


# wrapper to pick correct year
def form(year):
    """
    Fonction qui permet de sélectionner le formulaire d'impôt provincial par année.

    Parameters
    ----------
    year: int
        année (présentement entre 2016 et 2020)
    Returns
    -------
    class instance
        Une instance du formulaire pour l'année sélectionnée.
    """
    if year == 2016:
        p = form_2016()
    if year == 2017:
        p = form_2017()
    if year == 2018:
        p = form_2018()
    if year == 2019:
        p = form_2019()
    if year == 2020:
        p = form_2020()
    return p


class form_2016(template):
    """
    Rapport d'impôt de 2016.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ontario/params/measures_2016.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/schedule_2016.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/health_contrib_2016.csv')

class form_2017(form_2016):
    """
    Rapport d'impôt de 2017.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ontario/params/measures_2017.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/schedule_2017.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/health_contrib_2017.csv')

class form_2018(form_2017):
    """
    Rapport d'impôt de 2018.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ontario/params/measures_2018.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/schedule_2018.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/health_contrib_2018.csv')

class form_2019(form_2018):
    """
    Rapport d'impôt de 2019.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ontario/params/measures_2019.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/schedule_2019.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/health_contrib_2019.csv')


    def calc_on_lift_credit(self, p, hh):
        """
        Crédit d’impôt pour les personnes et les familles à faible revenu (LIFT).

        Ce crédit est non-remboursable.

        Parameters
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        if p.inc_work == 0:
            p.on_lift = 0

        amount = min(self.lift_rate * p.inc_work, self.lift_max_amount)
        clawback = (self.lift_claw_rate 
                    * max(0, p.fed_return['net_income'] - self.lift_cutoff_single))
        if hh.couple:
            couple_clawback = (self.lift_claw_rate 
                               * max(0, hh.fam_net_inc_fed - self.lift_cutoff_couple))
            clawback = max(clawback, couple_clawback)

        p.on_lift = max(0, amount - clawback)

class form_2020(form_2019):
    """
    Rapport d'impôt de 2020.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ontario/params/measures_2020.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/schedule_2020.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/health_contrib_2020.csv')
