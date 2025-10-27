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
    if year == 2023:
        p = form_2023()
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
        def create_contribution():
            lines = ['drug_insurance_contrib', 'contrib_hsf','add_contrib_subsid_chcare']
            return dict(zip(lines, np.zeros(len(lines))))
            
        p.prov_contrib = create_contribution()
        p.prov_contrib['add_contrib_subsid_chcare'] = self.add_contrib_subsid_chcare(p, hh)
        p.prov_contrib['contrib_hsf'] = self.contrib_hsf(p)

        if p.pub_drug_insurance:
            p.prov_contrib['drug_insurance_contrib'] = self.drug_insurance_contrib(hh)

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
            if (d.age >=4 and d.age<=16) or (d.disabled==True and (d.age >=4 and d.age<=17)):
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
        Fonction qui remplace dans le gabarit (classe *srd.quebec.template*) la fonction du même nom, et calcule le crédit remboursable pour soutien aux ainés. En vigueur à partir de 2018.

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
        Déduction pour les cotisations RRQ/RPC et au RQAP pour le travail autonome.

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
        def create_contribution():
            lines = ['drug_insurance_contrib', 'contrib_hsf']
            return dict(zip(lines, np.zeros(len(lines))))

        p.prov_contrib = create_contribution()
        p.prov_contrib['contrib_hsf'] = self.contrib_hsf(p)

        if p.pub_drug_insurance:
            p.prov_contrib['drug_insurance_contrib'] = self.drug_insurance_contrib(hh)


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

    def get_caregivers(self, p, hh):
        """
        Fonction qui calcule le crédit d'impôt pour personne aidante.

        Seule la composante pour personne aidante cohabitant avec une personne majeure atteinte d'une déficience est incluse,
        puisque seules les personnes vivant dans le ménage sont modélisées.
        
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
        amount = 0
        recipient = 0

        if (hh.couple) & (p.disabled==False):
            spouse = hh.sp[1 - hh.sp.index(p)]
            if spouse.disabled:
                amount = 2*self.caregiver_base
                clawback = min(self.caregiver_base, (spouse.prov_return['net_income']- self.caregiver_cutoff)*self.caregiver_rate)
                amount = amount - max(0,clawback)
            recipient +=1

        if p.disabled==False:
            ndep_dis = min(len([ch for ch in hh.dep if ch.age >= 18 and ch.disabled]),2-recipient)
            if ndep_dis >= 1:
                amount += 2*self.caregiver_base * ndep_dis
        return max(0, amount)

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
        Fonction qui calcule les crédits d'impôt remboursables attribuant une prestation exceptionnelle et un montant ponctuel pour pallier la hausse du coût de la vie.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        """

        # punctual amount
        if p.prov_return['net_income'] <= self.cost_of_living_cutoff:
            amount_punctual = self.cost_of_living_punctual
        else:
            amount_punctual =  max(0,self.cost_of_living_punctual - (self.cost_of_living_claw_rate * (p.prov_return['net_income'] - self.cost_of_living_cutoff)))

        # exceptional amount
        if p.qc_solidarity == 0:
            amount_exceptional = 0
        if p.qc_solidarity>0 and hh.couple :
            amount_exceptional = self.cost_of_living_not_alone
        if p.qc_solidarity>0 and hh.couple==False :
            amount_exceptional = self.cost_of_living_alone

        return amount_punctual + (amount_exceptional / (1 + hh.couple))

class form_2022(form_2021):
    """
    Formulaire d'impôt de 2022.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/quebec/params/measures_2022.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/schedule_2022.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/chcare_2022.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/drug_insurance_contrib_2022.csv')

    def cost_of_living(self, p, hh):
        """
        Fonction qui calcule le crédit d'impôt remboursable conférant un nouveau montant ponctuel pour le coût de la vie.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        """
        if p.prov_return['net_income'] <= self.cost_of_living_cutoff1:
            amount_punctual = self.cost_of_living_punctual1
        elif p.prov_return['net_income'] > self.cost_of_living_cutoff1 and p.prov_return['net_income'] <= self.cost_of_living_cutoff2:
            amount_punctual =  max(0,self.cost_of_living_punctual1 - (self.cost_of_living_claw_rate1 * (p.prov_return['net_income'] - self.cost_of_living_cutoff1)))
        elif p.prov_return['net_income'] > self.cost_of_living_cutoff2 and p.prov_return['net_income'] <= self.cost_of_living_cutoff3:
            amount_punctual = self.cost_of_living_punctual2
        else:
            amount_punctual =  max(0,self.cost_of_living_punctual2 - (self.cost_of_living_claw_rate2 * (p.prov_return['net_income'] - self.cost_of_living_cutoff3)))
        return amount_punctual

class form_2023(form_2022):
    """
    Formulaire d'impôt de 2023.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/quebec/params/measures_2023.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/schedule_2023.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/chcare_2023.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/drug_insurance_contrib_2023.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/shelter_2023.csv')

    def cost_of_living(self, p, hh):
        """
        Fonction qui calcule le crédit d'impôt remboursable conférant un nouveau montant ponctuel pour le coût de la vie.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        """
        pass

    def allow_shelter(self, hh):
        """
        Fonction qui calcule le montant de l'allocation-logement.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        hh.shelter_elig = True
        ndep = len(hh.dep)

        if not hh.couple:
          if ndep == 0 and  hh.sp[0].age< self.min_age_shelter_elig:
             hh.shelter_elig = False
          elif ndep == 0 and hh.fam_net_inc_prov > self.max_earn_alone:
             hh.shelter_elig = False
          elif 1<= ndep < 3 and hh.fam_inc_work> self.max_earn_mono_1or2kid:
             hh.shelter_elig = False
          elif ndep >= 3 and hh.fam_net_inc_prov > self.max_earn_mono_more_3kid:
             hh.shelter_elig = False
        else:
          np_elig_age = len([p for p in hh.sp if p.age < self.min_age_shelter_elig])

          if ndep == np_elig_age== 0 :
             hh.shelter_elig = False
          elif ndep == 0 and hh.fam_net_inc_prov > self.max_earn_couple_0kid:
            hh.shelter_elig = False
          elif  ndep == 1 and hh.fam_net_inc_prov > self.max_earn_couple_1kid:
            hh.shelter_elig = False
          elif ndep > 1 and hh.fam_net_inc_prov > self.max_earn_couple_more_2kid:
            hh.shelter_elig = False

        prop_rent = 0
        if hh.fam_net_inc_prov>0:
         prop_rent = hh.rent/ hh.fam_net_inc_prov

        amount = 0
        if hh.shelter_elig:
            if float(self.shelter_percent1) <= prop_rent < float(self.shelter_percent2):
                amount += self.amount_30_to_49
            elif float(self.shelter_percent3) <= prop_rent < float(self.shelter_percent4):
                amount += self.amount_50_79
            elif prop_rent>= float(self.shelter_percent5):
                amount += self.amount_more_80

        for p in hh.sp:
            p.allow_shelter = amount/(1+ hh.couple)