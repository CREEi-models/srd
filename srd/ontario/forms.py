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
        add_schedule_as_attr(self, module_dir + '/ontario/params/chcare_2016.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/health_contrib_2016.csv')


class form_2017(form_2016):
    """
    Rapport d'impôt de 2017.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ontario/params/measures_2017.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/schedule_2017.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/chcare_2017.csv')


class form_2018(form_2017):
    """
    Rapport d'impôt de 2018.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ontario/params/measures_2018.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/schedule_2018.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/chcare_2018.csv')


class form_2019(form_2018):
    """
    Rapport d'impôt de 2019.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ontario/params/measures_2019.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/schedule_2019.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/chcare_2019.csv')

class form_2020(form_2019):
    """
    Rapport d'impôt de 2020.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ontario/params/measures_2020.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/schedule_2020.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/chcare_2020.csv')
