from srd import add_params_as_attr
import os
from srd.qpip import template
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
        add_params_as_attr(self, module_dir + '/qpip/params/parameters_2016.csv')


# program for 2017, derived from template, only requires modify
# functions that change
class program_2017(template):
    """
    Version du programme de 2017.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/qpip/params/parameters_2017.csv')


# program for 2018, derived from template, only requires modify
# functions that change
class program_2018(template):
    """
    Version du programme de 2018.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/qpip/params/parameters_2018.csv')


# program for 2019, derived from template, only requires modify
# functions that change
class program_2019(template):
    """
    Version du programme de 2019.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/qpip/params/parameters_2019.csv')


# program for 2020, derived from template, only requires modify
# functions that change
class program_2020(template):
    """
    Version du programme de 2020.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/qpip/params/parameters_2020.csv')
