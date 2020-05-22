from srd import add_params_as_attr, add_schedule_as_attr, covid
import os
from srd.federal import template
module_dir = os.path.dirname(os.path.dirname(__file__))

# wrapper to pick correct year
def form(year, policy=covid.policy()):
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
        p = form_2020(policy)
    return p

class form_2016(template):
    """
    Rapport d'impôt de 2016.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/federal/params/federal_2016.csv')
        add_params_as_attr(self, module_dir + '/federal/params/fed_witb_qc_2016.csv')
        add_schedule_as_attr(self, module_dir + '/federal/params/schedule_2016.csv')

class form_2017(template):
    """
    Rapport d'impôt de 2017.
    """
    def __init__(self):
        add_params_as_attr(self,module_dir+'/federal/params/federal_2017.csv')
        add_params_as_attr(self, module_dir + '/federal/params/fed_witb_qc_2017.csv')
        add_schedule_as_attr(self, module_dir + '/federal/params/schedule_2017.csv')
        return

class form_2018(template):
    """
    Rapport d'impôt de 2018.
    """
    def __init__(self):
        add_params_as_attr(self,module_dir+'/federal/params/federal_2018.csv')
        add_params_as_attr(self, module_dir + '/federal/params/fed_witb_qc_2018.csv')
        add_schedule_as_attr(self, module_dir + '/federal/params/schedule_2018.csv')
        return

class form_2019(template):
    """
    Rapport d'impôt de 2019.
    """
    def __init__(self):
        add_params_as_attr(self,module_dir+'/federal/params/federal_2019.csv')
        add_params_as_attr(self, module_dir + '/federal/params/fed_witb_qc_2019.csv')
        add_schedule_as_attr(self, module_dir + '/federal/params/schedule_2019.csv')
        return

class form_2020(template):
    """
    Rapport d'impôt de 2020.
    """
    def __init__(self, policy):
        add_params_as_attr(self,module_dir+'/federal/params/federal_2020.csv')
        add_params_as_attr(self, module_dir + '/federal/params/fed_witb_qc_2020.csv')
        add_schedule_as_attr(self, module_dir + '/federal/params/schedule_2020.csv')

        self.policy = policy
        if policy.icovid_ccb:
            self.ccb_young += self.ccb_covid_supp
            self.ccb_old += self.ccb_covid_supp
        if policy.icovid_gst:
            self.gst_cred_base *= 2
            self.gst_cred_other *= 2
        # note: the measures to increase ccb and gst_credit are based on fiscal year 2019 in reality
        #       but on fiscal year 2020 in our simulator; the difference is small (<50$ in worst case)

    def calc_non_refundable_tax_credits(self, p):
        """
        Fonction qui calcule les crédits d'impôt non-remboursable.

        Cette fonction fait la somme de tous les crédits d'impôt modélisés.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        br_poor, br_rich = self.l_brackets[-2:]

        if p.fed_return['net_income'] <= br_poor:
            basic_amount = self.basic_amount_poor
        elif p.fed_return['net_income'] > br_rich:
            basic_amount = self.basic_amount_rich
        else:
            slope = (self.basic_amount_rich - self.basic_amount_poor) / (br_rich - br_poor)
            basic_amount = self.basic_amount_poor + (p.fed_return['net_income'] - br_poor) * slope
        p.fed_age_cred = self.get_age_cred(p)
        p.fed_pension_cred = self.get_pension_cred(p)
        p.fed_disabled_cred = self.get_disabled_cred(p)
        p.fed_return['non_refund_credits'] = self.rate_non_ref_tax_cred * (basic_amount
            + p.fed_age_cred + p.fed_pension_cred + p.fed_disabled_cred)
