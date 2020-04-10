from srd import add_params_as_attr, add_schedule_as_attr
import os
from srd.federal import template
module_dir = os.path.dirname(os.path.dirname(__file__))

# wrapper to pick correct year
def form(year):
    """
    Fonction qui permet de sélectionner le formulaire d'impôt fédéral par année.

    Parameters
    ----------
    year: int 
        année (présentement entre 2016 et 2020)
    Returns
    -------
    class instance
        Une instance du formulaire pour l'année sélectionnée. 
    """
    if year==2016:
        p = form_2016()
    if year==2017:
        p = form_2017()
    if year==2018:
        p = form_2018()
    if year==2019:
        p = form_2019()
    if year==2020:
        p = form_2020()
    return p 

class form_2016(template):
    """
    Rapport d'impôt de 2016. 
    """
    def __init__(self):
        add_params_as_attr(self,module_dir+'/federal/params/federal_2016.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/federal/params/schedule_2016.csv')
        return

class form_2017(template):
    """
    Rapport d'impôt de 2017. 
    """
    def __init__(self):
        add_params_as_attr(self,module_dir+'/federal/params/federal_2017.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/federal/params/schedule_2017.csv')
        return

class form_2018(template):
    """
    Rapport d'impôt de 2018. 
    """
    def __init__(self):
        add_params_as_attr(self,module_dir+'/federal/params/federal_2018.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/federal/params/schedule_2018.csv')
        return

class form_2019(template):
    """
    Rapport d'impôt de 2019. 
    """
    def __init__(self):
        add_params_as_attr(self,module_dir+'/federal/params/federal_2019.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/federal/params/schedule_2019.csv')
        return

class form_2020(template):
    """
    Rapport d'impôt de 2020. 
    """
    def __init__(self):
        add_params_as_attr(self,module_dir+'/federal/params/federal_2020.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/federal/params/schedule_2020.csv')
        return
