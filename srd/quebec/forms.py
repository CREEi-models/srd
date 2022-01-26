import os
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
        année (présentement entre 2016 et 2021)
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
    return p


class form_2016(template):
    """
    Formulaire d'impôt de 2016.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/quebec/params/measures_2016.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/schedule_2016.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/chcare_2016.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/health_contrib_2016.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/drug_insurance_contrib_2016.csv')


class form_2017(form_2016):
    """
    Formulaire d'impôt de 2017.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/quebec/params/measures_2017.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/schedule_2017.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/chcare_2017.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/drug_insurance_contrib_2017.csv')

    def calc_contributions(self, p, hh):
        """
        Fonction qui remplace dans le gabarit (classe *srd.quebec.template*) la fonction du même nom, et calcule les contributions.

        Cette fonction fait la somme des contributions du contribuable. La contribution santé est abolie en 2017.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        p.prov_return['contributions'] = self.add_contrib_subsid_chcare(p, hh) + self.contrib_hsf(p)

        if p.pub_drug_insurance:
            p.prov_return['contributions'] += self.drug_insurance_contrib(hh)

    def get_donations_cred(self, p):
        """
        Fonction qui remplace dans le gabarit (classe *srd.quebec.template*) la fonction du même nom, et calcule le crédit d'impôt non-remboursable pour dons.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant du crédit
        """
        tot_donation = p.donation + p.gift

        if tot_donation <= self.nrtc_donation_low_cut:
            return tot_donation * self.nrtc_donation_low_rate
        else:
            extra_donation = tot_donation - self.nrtc_donation_low_cut
            high_inc = max(0, p.fed_return['taxable_income']
                             - self.nrtc_donation_high_cut)
            donation_high_inc = min(extra_donation, high_inc)
            donation_low_inc = extra_donation - donation_high_inc
            return (self.nrtc_donation_low_cut * self.nrtc_donation_low_rate
                    + donation_high_inc * self.nrtc_donation_high_rate
                    + donation_low_inc * self.nrtc_donation_med_rate)

    def ccap(self, p, hh):
        """
        Fonction qui calcule le crédit d’impôt remboursable accordant une allocation aux familles (CIRAAF) (qui s'appelait le Soutien aux enfants avant 2019). Seules les composantes suivantes sont modélisées : l'allocation famille et le supplément pour l'achat de fournitures scolaires.
   
        Cette fonction calcule le montant reçu selon le nombre d'enfants, la situation familiale (couple/monoparental) et le revenu.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        Returns
        -------
        float
            Montant du crédit d’impôt remboursable accordant une allocation aux familles (CIRAAF).
        """
        if hh.couple and p.male and hh.sp[0].male != hh.sp[1].male:
            return 0 # heterosexual couple: mother receives benefit


        if hh.nkids_0_17 == 0:
            return 0

        fam_netinc = sum([s.prov_return['net_income'] for s in hh.sp])

        if hh.couple:
            clawback = max(0, self.ccap_claw_rate * (fam_netinc - self.ccap_claw_cutoff_couple))
            add_amount_min = 0
            add_amount_max = 0
        else:
            clawback = max(0, 0.04 * (fam_netinc - self.ccap_claw_cutoff_single))
            add_amount_min = self.ccap_amount_single_min
            add_amount_max = self.ccap_amount_single_max

        if hh.nkids_0_17 == 1:
            amount_family = max(add_amount_min + self.ccap_kid1_min,
                         add_amount_max + self.ccap_kid1_max - clawback)
        elif hh.nkids_0_17 < 4:
            amount_family = max(add_amount_min + self.ccap_kid1_min + (hh.nkids_0_17 - 1) * self.ccap_kid23_min,
                         add_amount_max + self.ccap_kid1_max
                         + (hh.nkids_0_17 - 1) * self.ccap_kid23_max - clawback)
        else:
            amount_family = max(add_amount_min + self.ccap_kid1_min + 2 * self.ccap_kid23_min
                         + (hh.nkids_0_17 - 3) * self.ccap_kid4p_min,
                         add_amount_max + self.ccap_kid1_max + 2 * self.ccap_kid23_max
                         + (hh.nkids_0_17 - 3) * self.ccap_kid4p_max - clawback)

        kid_eligible = 0
        for d in hh.dep:
            if (d.age >=4 and d.age<=16) or (d.disa==True and (d.age >=4 and d.age<=17)):
                kid_eligible += 1 

        amount_furnitures = max(0, kid_eligible*self.supp_furnitures)

        if hh.couple and hh.sp[0].male == hh.sp[1].male:
            return (amount_furnitures + amount_family) / 2  # same sex couples get 1/2 each
        else:
            return amount_furnitures + amount_family

class form_2018(form_2017):
    """
    Formulaire d'impôt de 2018.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/quebec/params/measures_2018.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/schedule_2018.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/chcare_2018.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/drug_insurance_contrib_2018.csv')

    def senior_assist(self, p, hh):
        """
        Fonction qui remplace dans le gabarit (classe *srd.quebec.template*) la fonction du même nom, et calcule le crédit remboursable pour support aux ainés. En vigueur à partir de 2018.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant du crédit
        """
        if max([p.age for p in hh.sp]) < self.senior_assist_min_age:
            return 0

        n_elderly = len([p.age for p in hh.sp
                         if p.age >= self.senior_assist_min_age])
        amount = self.senior_assist_amount * n_elderly

        if hh.couple:
            cutoff = self.senior_assist_cutoff_couple
        else:
            cutoff = self.senior_assist_cutoff_single

        clawback = self.senior_assist_claw_rate * max(0, hh.fam_net_inc_prov - cutoff)

        return max(0, amount - clawback) / (1 + hh.couple)


class form_2019(form_2018):
    """
    Formulaire d'impôt de 2019.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/quebec/params/measures_2019.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/schedule_2019.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/chcare_2019.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/drug_insurance_contrib_2019.csv')

    def cpp_qpip_deduction(self, p):
        """
        Déduction pour les cotisations RRQ / RPC et au RQAP pour le travail autonome.
        Parameters
        ----------
        p: Person
            instance de la classe Person
        Returns
        -------
        float
            Montant de la déduction.
        """
        p.qc_cpp_deduction = p.contrib_cpp_self / 2
        p.qc_cpp_deduction += p.payroll['cpp_supp']
        
        p.qc_qpip_deduction = self.qpip_deduc_rate * p.contrib_qpip_self
        return p.qc_cpp_deduction + p.qc_qpip_deduction
    
    def calc_contributions(self, p, hh):
        """
        Fonction qui remplace la fonction antérieure du même nom, et calcule les contributions.

        Cette fonction fait la somme des contributions du contribuable. La contribution additionnelle pour service de garde éducatifs à l'enfance subventionnés est abolie en 2019.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        p.prov_return['contributions'] = self.contrib_hsf(p)

        if p.pub_drug_insurance:
            p.prov_return['contributions'] += self.drug_insurance_contrib(hh)


class form_2020(form_2019):
    """
    Formulaire d'impôt de 2020.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/quebec/params/measures_2020.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/schedule_2020.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/chcare_2020.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/drug_insurance_contrib_2020.csv')

    def calc_deduc_gross_income(self, p):
        """
        Fonction qui calcule les déductions.

        Cette fonction fait la somme des différentes déductions du contribuable.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.qc_work_deduc = self.work_deduc(p)
        p.qc_cpp_qpip_deduction = self.cpp_qpip_deduction(p)
        p.prov_return['deductions_gross_inc'] = (p.con_rrsp + p.con_rpp
                                                 + p.qc_work_deduc
                                                 + p.pension_deduction_qc
                                                 + p.qc_cpp_qpip_deduction)
        if p.inc_oas>0:
            p.prov_return['deductions_gross_inc'] += self.oas_covid_bonus

class form_2021(form_2020):
    """
    Formulaire d'impôt de 2021.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/quebec/params/measures_2021.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/schedule_2021.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/chcare_2021.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/drug_insurance_contrib_2021.csv')

    def calc_deduc_gross_income(self, p):
        """
        Fonction qui calcule les déductions.

        Cette fonction fait la somme des différentes déductions du contribuable.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.qc_work_deduc = self.work_deduc(p)
        p.qc_cpp_qpip_deduction = self.cpp_qpip_deduction(p)
        p.prov_return['deductions_gross_inc'] = (p.con_rrsp + p.con_rpp
                                                 + p.qc_work_deduc
                                                 + p.pension_deduction_qc
                                                 + p.qc_cpp_qpip_deduction)
    
    
    
    def cost_of_living(self, p, hh):
        """
        Fonction qui calcule le crédit d'impôt remboursable attribuant une prestation exceptionnelle pour pallier la hausse du coût de la vie.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        """
        if p.qc_solidarity == 0:
            return 0
        
        if hh.couple :
            amount = self.cost_of_living_not_alone
        else:
            amount = self.cost_of_living_alone
        
        return amount / (1 + hh.couple)
        
