from srd import add_params_as_attr, get_params, add_schedule_as_attr, covid
import os
from srd.federal import template
from srd import ei
module_dir = os.path.dirname(os.path.dirname(__file__))

# wrapper to pick correct year
def form(year, policy=covid.policy()):
    """
    Fonction qui permet de sélectionner le formulaire d'impôt fédéral par année.

    Parameters
    ----------
    year: int
        année (présentement entre 2016 et 2020)
    policy: policy
        instance de la classe policy
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
    Formulaire d'impôt de 2016.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/federal/params/federal_2016.csv')
        add_schedule_as_attr(self, module_dir + '/federal/params/schedule_2016.csv')
        self.witb_params = {}
        for prov in ['on', 'qc']:
            self.witb_params[prov] = get_params(
                module_dir + f'/federal/params/fed_witb_{prov}_2016.csv')

class form_2017(form_2016):
    """
    Formulaire d'impôt de 2017.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir+'/federal/params/federal_2017.csv')
        add_params_as_attr(self, module_dir + '/federal/params/fed_witb_qc_2017.csv')
        add_schedule_as_attr(self, module_dir + '/federal/params/schedule_2017.csv')
        self.witb_params = {}
        for prov in ['on', 'qc']:
            self.witb_params[prov] = get_params(
                module_dir + f'/federal/params/fed_witb_{prov}_2017.csv')

class form_2018(form_2017):
    """
    Formulaire d'impôt de 2018.
    """
    def __init__(self):
        add_params_as_attr(self,module_dir+'/federal/params/federal_2018.csv')
        add_params_as_attr(self, module_dir + '/federal/params/fed_witb_qc_2018.csv')
        add_schedule_as_attr(self, module_dir + '/federal/params/schedule_2018.csv')
        self.witb_params = {}
        for prov in ['on', 'qc']:
            self.witb_params[prov] = get_params(
                module_dir + f'/federal/params/fed_witb_{prov}_2018.csv')

class form_2019(form_2018):
    """
    Formulaire d'impôt de 2019.
    """
    def __init__(self):
        add_params_as_attr(self,module_dir+'/federal/params/federal_2019.csv')
        add_params_as_attr(self, module_dir + '/federal/params/fed_witb_qc_2019.csv')
        add_schedule_as_attr(self, module_dir + '/federal/params/schedule_2019.csv')
        self.witb_params = {}
        for prov in ['on', 'qc']:
            self.witb_params[prov] = get_params(
                module_dir + f'/federal/params/fed_witb_{prov}_2019.csv')

class form_2020(form_2019):
    """
    Formulaire d'impôt de 2020.
    
    Parameters
    ----------
    policy: policy
        instance de la classe policy
    """
    def __init__(self, policy):
        add_params_as_attr(self,module_dir+'/federal/params/federal_2020.csv')
        add_params_as_attr(self, module_dir + '/federal/params/fed_witb_qc_2020.csv')
        add_schedule_as_attr(self, module_dir + '/federal/params/schedule_2020.csv')
        self.witb_params = {}
        for prov in ['on', 'qc']:
            self.witb_params[prov] = get_params(
                module_dir + f'/federal/params/fed_witb_{prov}_2020.csv')

        self.policy = policy
        if policy.icovid_ccb:
            self.ccb_young += self.ccb_covid_supp
            self.ccb_old += self.ccb_covid_supp
        if policy.icovid_gst:
            self.gst_cred_base *= 2
            self.gst_cred_other *= 2
        # note: the measures to increase ccb and gst_credit are based on fiscal year 2019 in reality
        #       but on fiscal year 2020 in our simulator; the difference is small (<50$ in worst case)

    def compute_basic_amount(self, p):
        """
        Fonction qui calcule le montant personnel de base.

        Le calcul de ce montant change en 2020.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant personnel de base.
        """
        br_poor, br_rich = self.l_brackets[-2:]

        if p.fed_return['net_income'] <= br_poor:
            basic_amount = self.basic_amount_poor
        elif p.fed_return['net_income'] > br_rich:
            basic_amount = self.basic_amount_rich
        else:
            slope = (self.basic_amount_rich - self.basic_amount_poor) / (br_rich - br_poor)
            basic_amount = self.basic_amount_poor + (p.fed_return['net_income'] - br_poor) * slope

        return basic_amount

    def calc_net_income(self, p):
        """
        Fonction qui calcule le revenu net au sens de l'impôt.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.fed_return['net_income'] =  max(0, p.fed_return['gross_income']
                                          - p.fed_return['deductions_gross_inc'])
        self.repayments_ei(p)

    def repayments_ei(self, p):
        """
        Fonction qui calcule le montant du remboursement d'assurance-emploi et qui
        ajuste le montant des bénéfices, le revenu net et le revenu brut.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            montant du remboursement
        """
        excess_net_inc = max(0, p.fed_return['net_income'] - self.ei_max_net_inc)
        if excess_net_inc > 0:
            repayment = self.ei_rate_repay * min(p.inc_ei, excess_net_inc)
            p.inc_ei -= repayment
            p.fed_return['net_income'] -= repayment
            p.fed_return['gross_income'] -= repayment
