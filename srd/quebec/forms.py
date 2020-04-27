import os
import numpy as np
from srd import add_params_as_attr, add_schedule_as_attr
from srd.quebec import template

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
        add_params_as_attr(self, module_dir + '/quebec/params/measures_2016.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/quebec/params/schedule_2016.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/quebec/params/chcare_2016.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/quebec/params/health_contrib_2016.csv',delimiter=';')
        return

    def calc_contributions(self, p, hh):
        """
        Fonction qui calcule l'impôt à payer selon la table d'impôt.

        Cette fonction utilise la table d'impôt de l'année cours.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        p.prov_return['contributions'] = self.add_contrib_subsid_chcare(p, hh) \
                                         + self.health_contrib(p, hh)

    def health_contrib(self, p, hh):
        """
        Contribution  santé.

        Cette fonction calcule le montant dû en fonction du revenu net.
        Abolie en 2017.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        fam_net_inc = sum([p.prov_return['net_income'] for p in hh.sp])
        if hh.couple:
            age_spouse = hh.sp[1-hh.sp.index(p)].age
        nkids = len([d for d in hh.dep if d.age < self.health_max_age_kid])

        if p.prov_return['net_income'] <= self.health_cutoff_10:
            return 0
        if not hh.couple:
            cond12 = nkids == 1 and fam_net_inc <= self.health_cutoff_12
            cond14 = nkids == 2 and fam_net_inc <= self.health_cutoff_14
            if cond12 or cond14:
                return 0
        if hh.couple:
            cond16 = fam_net_inc <= self.health_cutoff_16
            cond18 = nkids == 1 and fam_net_inc <= self.health_cutoff_18
            cond20 = nkids == 2 and fam_net_inc <= self.health_cutoff_20
            if cond16 or cond18 or cond20:
                return 0

        if not hh.couple and p.age >= self.health_age_high and p.inc_gis > self.health_cutoff_27:
            return 0
        if hh.couple and p.age >= self.health_age_high:
            cond28 = age_spouse >= self.health_age_high and p.inc_gis > self.health_cutoff_28
            cond29 = self.health_age_low <= age_spouse < self.health_age_high and p.inc_gis > self.health_cutoff_29
            cond31 = age_spouse < self.health_age_low and p.inc_gis > self.health_cutoff_31
            if cond28 or cond29 or cond31:
                return 0
        # not sure about conditions 33 and 35

        ind = np.searchsorted(self.l_health_brackets, p.prov_return['net_income'], 'right') - 1
        return min(self.l_health_max[ind], self.l_health_constant[ind] + \
            self.l_health_rates[ind] * (p.prov_return['net_income'] - self.l_health_brackets[ind]))

class form_2017(template):
    """
    Rapport d'impôt de 2017.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/quebec/params/measures_2017.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/quebec/params/schedule_2017.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/quebec/params/chcare_2017.csv',delimiter=';')

class form_2018(template):
    """
    Rapport d'impôt de 2018.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/quebec/params/measures_2018.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/quebec/params/schedule_2018.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/quebec/params/chcare_2018.csv',delimiter=';')

class form_2019(template):
    """
    Rapport d'impôt de 2019.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/quebec/params/measures_2019.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/quebec/params/schedule_2019.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/quebec/params/chcare_2019.csv',delimiter=';')

    def add_contrib_subsid_chcare(self, p, hh):
        """
        Fonction qui calcule la contribution additionnelle
        pour service de garde éducatifs à l'enfance subventionnés.

        Supprimé en 2019

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        pass

class form_2020(template):
    """
    Rapport d'impôt de 2020.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/quebec/params/measures_2020.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/quebec/params/schedule_2020.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/quebec/params/chcare_2020.csv',delimiter=';')

    def add_contrib_subsid_chcare(self, p, hh):
        """
        Fonction qui calcule la contribution additionnelle
        pour service de garde éducatifs à l'enfance subventionnés.

        Supprimé en 2019

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        pass
