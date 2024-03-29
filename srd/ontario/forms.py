import os
import numpy as np
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
        année (présentement entre 2016 et 2022)
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
    if year == 2021:
        p = form_2021()
    if year == 2022:
        p = form_2022()
    return p


class form_2016(template):
    """
    Formulaire d'impôt de 2016.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ontario/params/measures_2016.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/schedule_2016.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/health_contrib_2016.csv')

class form_2017(form_2016):
    """
    Formulaire d'impôt de 2017.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ontario/params/measures_2017.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/schedule_2017.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/health_contrib_2017.csv')

class form_2018(form_2017):
    """
    Formulaire d'impôt de 2018.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ontario/params/measures_2018.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/schedule_2018.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/health_contrib_2018.csv')

class form_2019(form_2018):
    """
    Formulaire d'impôt de 2019.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ontario/params/measures_2019.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/schedule_2019.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/health_contrib_2019.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/chcare_2019.csv')

    def lift_credit(self, p, hh):
        """
        Crédit d’impôt pour les personnes et les familles à faible revenu (Low-income individuals and families tax credit: LIFT).

        Ce crédit entre en vigueur en 2019. Il est non-remboursable.

        Parameters
        ----------
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

    def chcare(self,p, hh):
        """
        Fonction qui calcule le Crédit d'impôt de l'Ontario pour l'accès aux services de garde d'enfants et l'allègement des dépenses (ASGE)
                
        Ce crédit est remboursable.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant du crédit.
        """

        if hh.child_care_exp == 0:
            return 0

        chcare_deduc = sum([p.fed_chcare for p in hh.sp])

        adj_fam_net_inc = max(0,hh.fam_net_inc_fed + chcare_deduc)
        ind = np.searchsorted(self.chcare_brack, adj_fam_net_inc, 'right') - 1
        if adj_fam_net_inc != 0:
            amount = chcare_deduc * self.chcare_rate[ind]
        else:
            amount = chcare_deduc * self.chcare_rate[0]

        if hh.couple:
            hh.sp[0].on_chcare = 0
        
        return amount
            

    
    def caip(self,p ,hh):
        """
        Fonction qui calcule le crédit de l’incitatif à agir pour le climat (IAC) ou encore le Paiement de l’incitatif à agir pour le climat (PIAC)

        Ce crédit est remboursable.
        
        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant du crédit.
        """
        amount = self.caip_single

        if hh.couple:
            amount += self.caip_couple
            if hh.nkids_0_17 > 0:
                amount += hh.nkids_0_17 * self.caip_kid12
        else :
            if hh.nkids_0_17 > 0:
                amount += (self.caip_kid1 + ((hh.nkids_0_17 - 1)*self.caip_kid12))
        
        if hh.couple:
            hh.sp[1].on_caip = 0
        return amount

    def calc_refundable_tax_credits(self, p, hh):
        """
        Fonction qui fait la somme des crédits remboursables.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        p.on_chcare = self.chcare(p, hh)
        p.on_ocb = self.ocb(p, hh)
        p.on_ostc = self.ostc(p, hh)
        p.on_caip = self.caip(p, hh)
        p.on_oeptc = self.oeptc(p,hh)
        p.prov_return['refund_credits'] = p.on_ocb + p.on_ostc + p.on_chcare + p.on_caip + p.on_oeptc

class form_2020(form_2019):
    """
    Formulaire d'impôt de 2020.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ontario/params/measures_2020.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/schedule_2020.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/health_contrib_2020.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/chcare_2020.csv')

class form_2021(form_2020):
    """
    Formulaire d'impôt de 2021.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ontario/params/measures_2021.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/schedule_2021.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/health_contrib_2021.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/chcare_2021.csv')

    def chcare(self,p, hh):
        """
        Fonction qui calcule le Crédit d'impôt de l'Ontario pour l'accès aux services de garde d'enfants et l'allègement des dépenses (ASGE)
                
        Ce crédit est remboursable.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant du crédit.
        """

        if hh.child_care_exp == 0:
            return 0

        chcare_deduc = sum([p.fed_chcare for p in hh.sp])

        adj_fam_net_inc = max(0,hh.fam_net_inc_fed + chcare_deduc)
        ind = np.searchsorted(self.chcare_brack, adj_fam_net_inc, 'right') - 1

        if adj_fam_net_inc != 0:
            amount =  (chcare_deduc * self.chcare_rate[ind]) * (1 + self.chcare_rate_bonus)
        else:
            amount =  (chcare_deduc * self.chcare_rate[0]) * (1 + self.chcare_rate_bonus)

        if hh.couple:
            hh.sp[0].on_chcare = 0
        
        return amount
class form_2022(form_2021):
    """
    Formulaire d'impôt de 2022.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ontario/params/measures_2022.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/schedule_2022.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/health_contrib_2022.csv')
        add_schedule_as_attr(self, module_dir + '/ontario/params/chcare_2022.csv')
