from matplotlib import lines

from srd import add_params_as_attr, federal, quebec
import os
import numpy as np
from srd.assistance import template
from srd.assistance.template import create_return_qc
module_dir = os.path.dirname(os.path.dirname(__file__))


# wrapper to pick correct year
def program(year):
    """
    Fonction qui permet de sélectionner le programme par année.

    Parameters
    ----------
    year: int
        année (présentement entre 2016 et 2022)

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
    if year == 2021:
        p = program_2021()
    if year == 2022:
        p = program_2022()
    if year == 2023:
        p = program_2023()
    return p


# program for 2016, derived from template, only requires modify
# functions that change
class program_2016(template):
    """
    Version du programme de 2016.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/assistance/params/assistance_2016.csv')
        self.fed = federal.form(2016)
        self.qc = quebec.form(2016)

# program for 2017, derived from template, only requires modify
# functions that change
class program_2017(template):
    """
    Version du programme de 2017.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/assistance/params/assistance_2017.csv')
        self.fed = federal.form(2017)
        self.qc = quebec.form(2017)
        return

# program for 2018, derived from template, only requires modify
# functions that change
class program_2018(template):
    """
    Version du programme de 2018.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/assistance/params/assistance_2018.csv')
        self.fed = federal.form(2018)
        self.qc = quebec.form(2018)
        return


# program for 2019, derived from template, only requires modify
# functions that change
class program_2019(template):
    """
    Version du programme de 2019.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/assistance/params/assistance_2019.csv')
        self.fed = federal.form(2019)
        self.qc = quebec.form(2019)
        return
    
    def calc_solidarity_qc(self, hh):
        """
        Composante de base et supplément pour enfant (Québec).

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant combiné de la composante de base et du supplément pour enfant.
        """

        # eligibility : assets test
        self.eligibility_solidarity_qc(hh)
        if hh.ss_elig_asset==False:  # eliminate non-eligible hholds
            return 0
        
        nb_sev_constraints = 0 #severe constraints.

        if hh.sp[0].disabled:
            nb_sev_constraints += 1

        if hh.couple and hh.sp[1].disabled:
            nb_sev_constraints += 1

        if nb_sev_constraints == 0:
          return 0

        kids_adjustments = self.child_ajustments(hh)
        basic_amount = kids_adjustments

        if nb_sev_constraints== 1:
            if (hh.sp[0].long_term_ss or hh.sp[1].long_term_ss):
                basic_amount +=  self.socsol_qc_ltss_single
            else:
                basic_amount +=  self.socsol_qc_base_single

            clawback = max(0, max(0, hh.fam_inc_tot - self.socsol_qc_exemption_single))

        elif nb_sev_constraints== 2 :
            if (hh.sp[0].long_term_ss or hh.sp[1].long_term_ss):
                basic_amount +=  self.socsol_qc_ltss_couple
            else:
                basic_amount += self.socsol_qc_base_couple

            clawback = max(0, max(0, hh.fam_inc_tot - self.socsol_qc_exemption_couple))

        amount =  max(0, basic_amount - clawback)/ (1 + hh.couple)

        for p in hh.sp:
           p.inc_ss['amount']= amount
           p.inc_ss['basic amount'] = basic_amount/ (1+ hh.couple)
           p.inc_ss['kids_adjustments'] = kids_adjustments/ (1+ hh.couple)


# program for 2020, derived from template, only requires modify
# functions that change
class program_2020(template):
    """
    Version du programme de 2020.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/assistance/params/assistance_2020.csv')
        self.fed = federal.form(2020)
        self.qc = quebec.form(2020)
        return


# program for 2021, derived from template, only requires modify
# functions that change
class program_2021(template):
    """
    Version du programme de 2021.
    """

    def __init__(self):
        add_params_as_attr(self, module_dir + "/assistance/params/assistance_2021.csv")
        self.fed = federal.form(2021)
        self.qc = quebec.form(2021)
        return

class program_2022(template):
    """
    Version du programme de 2022.
    """

    def __init__(self):
        add_params_as_attr(self, module_dir + "/assistance/params/assistance_2022.csv")
        self.fed = federal.form(2022)
        self.qc = quebec.form(2022)
        return

class program_2023(template):
    """
    Version du programme de 2023.
    """

    def __init__(self):
        add_params_as_attr(self, module_dir + "/assistance/params/assistance_2023.csv")
        add_params_as_attr(self, module_dir + "/assistance/params/bip_2023.csv")
        self.fed = federal.form(2023)
        self.qc = quebec.form(2023)
        return
    
    def file(self, hh):
        """
        Fonction pour faire une demande au programme et recevoir une prestation.

        Cette fonction calcule une prestation intégrée d'aide sociale.

        Pour le Québec, cela inclut les prestations d'aide sociale, de solidarité sociale et de revenu de base.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant de l'aide sociale.
        """

        if hh.prov == 'qc':
            for p in hh.sp:
                p.inc_sa = create_return_qc()

            if any(p.disabled for p in hh.sp) and any(p.long_term_ss for p in hh.sp):
                self.calc_solidarity(hh)
                for p in hh.sp: 
                    self.calc_bip(p,hh)
                return 
            elif any(p.disabled for p in hh.sp) and not any(p.long_term_ss for p in hh.sp): 
                return self.calc_solidarity(hh)
            else:
                return self.calc_assistance_qc(hh)
        else:
            return self.calc_assitance_on(hh)
    
    def calc_assistance_qc(self, hh):
        """
        Composante de base et supplément pour enfant (en cas de prestation d'ACE réduite) pour le Québec.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant combiné de la composante de base et du supplément pour enfant.
        """

        # eligibility : assets test
        self.eligibility_assistance_qc(hh)
        if hh.sa_elig_assets==False:  # eliminate non-eligible hholds
            return 0

        if not any(p.sa_elig for p in hh.sp):
            return 0

        if hh.couple:
            if (hh.sp[0].sa_elig and hh.sp[1].disabled and not hh.sp[1].long_term_ss) or \
               (hh.sp[1].sa_elig and hh.sp[0].disabled and not hh.sp[0].long_term_ss):
                return 0

        nb_temp_constraints = 0
        if hh.sp[0].sa_elig== 'temporary constraints':
            nb_temp_constraints += 1
        if hh.couple and hh.sp[1].sa_elig=='temporary constraints':
            nb_temp_constraints += 1

        # determine ei, cpp and qpip contributions
        contributions = sum([sum(p.payroll.values()) for p in hh.sp])

        # reduction due to alimony
        ndep = len(hh.dep)
        kid_alimony = sum([k.alimony for k in hh.dep]) / ndep if hh.dep else 0 
        add_alimony = max(0, kid_alimony - self.socass_qc_alimony) * ndep 

        # kid adjustments
        ajustments_kid = self.child_ajustments(hh)

        #basic amount
        basic_amount,temp_amount = 0,0

        if hh.couple:
            neligible_bip = len([p for p in hh.sp if p.long_term_ss])

            if neligible_bip> 0:
                basic_amount += self.socass_qc_base_single
                
                clawback = max(0, max(0, hh.fam_inc_tot - self.socass_qc_exemption_single) - contributions + add_alimony)
            else:
                basic_amount += self.socass_qc_base_couple
                
                clawback = max(0, max(0, hh.fam_inc_tot - self.socass_qc_exemption_couple) - contributions + add_alimony)

            if nb_temp_constraints == 2:  #both parents have temporary constraints.
                temp_amount +=  self.socass_qc_temp_couple
        else:
            basic_amount += self.socass_qc_base_single
            if not hh.dep:
                basic_amount += self.socass_qc_ajust_single # single adjustment

            clawback = max(0, max(0, hh.fam_inc_tot - self.socass_qc_exemption_single) - contributions + add_alimony)


        if nb_temp_constraints == 1:
         temp_amount +=  self.socass_qc_temp_single

        amount =  max(0, basic_amount + ajustments_kid +  temp_amount - clawback) / (1 + hh.couple)

        for p in hh.sp:
            p.inc_sa['social assistance'] = amount

    def calc_solidarity(self, hh):
        """
        Composante de base et supplément. Le calcul de la prestation  de base est  modifié en 2023 avec
        l'arrivée du PRB. Le calcul des suppléments demeure inchangé.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        Returns
        -------
        float
            Montant combiné de la composante de base et du supplément pour enfant.
        """

        # eligibility : assets test
        self.eligibility_solidarity_qc(hh)
        if hh.ss_elig_asset==False:  # eliminate non-eligible hholds
            return 0

        nb_sev_constraints = 0
        if hh.sp[0].disabled== True:
            nb_sev_constraints += 1
        if hh.couple:
            if hh.sp[1].disabled == True:
                nb_sev_constraints += 1

        kids_adjustments = self.child_ajustments(hh)
        basic_amount = 0

        np_bip = len([p for p in hh.sp if p.long_term_ss])

        if nb_sev_constraints== 1:
          if np_bip > 0:
              return 0
          else:
            if not hh.couple:
                basic_amount += self.socsol_qc_base_single
                clawback = max(0, hh.fam_inc_tot - self.socsol_qc_exemption_single)
            else:
                basic_amount += self.socsol_qc_base_couple
                clawback = max(0, hh.fam_inc_tot - self.socsol_qc_exemption_couple)

        if nb_sev_constraints== 2:
            if np_bip== 0:
               basic_amount += self.socsol_qc_base_couple
               clawback = max(0, hh.fam_inc_tot - self.socsol_qc_exemption_couple)
            elif np_bip == 2:
              return 0
            elif np_bip == 1:      #at least 1 parent eligible for prb.
                basic_amount = self.socsol_qc_base_single
                clawback = max(0, hh.fam_inc_tot - self.socsol_qc_exemption_single)

        amount = max(0, basic_amount+ kids_adjustments- clawback) / (1 + hh.couple)

        for p in hh.sp:
           p.inc_ss['social solidarity']= amount

    def calc_bip(self, p, hh) :
        """
        Montant de base et ajustement pour personne seule (sans conjoint). Prestation calculée par individu.
        """

        self.eligibility_bip(p, hh)
        if hh.bip_elig_assets==False:  # eliminate non-eligible hholds
            return 0

        if not p.disabled:
          return 0

        if p.disabled and not p.long_term_ss:
          return 0

        basic_amount = 0

        basic_amount += self.bip_qc_adult_single

        if not hh.couple:
            basic_amount += self.bip_qc_ajust_single # single adjustment

        clawback = max(0, (p.inc_tot - self.bip_qc_exclusion_base)) * self.bip_qc_claw_rate
        basic_amount =  max(0, basic_amount - clawback)

        # Réduction conjoint non au prb.
        if hh.couple:
            spouse = hh.sp[1 - hh.sp.index(p)]

            if not spouse.long_term_ss:
               basic_amount = max(0, basic_amount - max(0, (spouse.inc_tot - self.bip_qc_spouse_nobip) * self.bip_qc_claw_rate_spouse_nobip))
               clawback += max(0, (spouse.inc_tot - self.bip_qc_spouse_nobip) * self.bip_qc_claw_rate_spouse_nobip)

        amount = basic_amount + self.child_adjustments_bip(hh)

        p.inc_sa['basic income'] = amount

    def child_adjustments_bip(self, hh):
        """"
        Parameters: hh: instance de la classe Hhold
        ------
            Returns: Ajustements pour enfants.
        """
        amount_sup = 0
        if hh.nkids_0_18> 0:
            amount_sup+= self.bip_qc_ajust_child* hh.nkids_0_18

        nadult_post_sec = len([s for s in hh.dep if s.age > 18 and s.educ_level == 'Vocational'])
        nadult_post_sec += len([s for s in hh.dep if s.age > 18 and s.educ_level == 'College'])
        nadult_post_sec += len([s for s in hh.dep if s.age > 18 and s.educ_level == 'University']) 

        if nadult_post_sec > 0:
            amount_sup += self.bip_qc_ajust_adult_postsec * nadult_post_sec
        return amount_sup
    
    def eligibility_bip(self, p, hh):
        """
        Fonction qui évalue l'admissibilité de la personne selon la limite d'actifs.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """

        spouse_cut_off = 1e6
        spouse = hh.sp[1 - hh.sp.index(p)]

        if not spouse.elig_assistance and not spouse.long_term_ss:
            spouse_cut_off = self.bip_qc_assets_spouse_nosa

        hh.bip_elig_assets = False

        if p.assets < self.bip_qc_assets and spouse.assets < spouse_cut_off:
            hh.bip_elig_assets = True

        return