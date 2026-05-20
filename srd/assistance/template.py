import os
import numpy as np
module_dir = os.path.dirname(os.path.dirname(__file__))

def create_return_qc():
    lines = ['social assistance', 'social solidarity', 'basic income']
    return dict(zip(lines, np.zeros(len(lines))))

def create_return_roc():
    lines = ['social assistance']
    return dict(zip(lines, np.zeros(len(lines))))

class template:
    """
    Classe qui contient un gabarit du programme d'aide sociale.

    Pour le Québec, cela inclut les prestations d'aide sociale, de solidarité sociale et de revenu de base.

    """

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

            if any(p.disabled for p in hh.sp):
                self.calc_solidarity(hh)
            else:
                return self.calc_assistance_qc(hh)
        else:
            for p in hh.sp:
                p.inc_sa = create_return_roc()
            return self.calc_assitance_on(hh)

    def shelter(self, hh):
        """
        Composante logement.

        N'est pas mise en œuvre pour l'instant.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant de la composante logement.
        """
        return 0

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
        
        # test if any of the spouses is eligible, if not, the SA amount is 0
        if not any(p.sa_elig for p in hh.sp):
            return 0

        nb_temp_constraints = 0
        if hh.sp[0].sa_elig=='temporary constraints':
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
            basic_amount += self.socass_qc_base_couple

            if nb_temp_constraints == 2: # both parents have temporary constraints.
                temp_amount +=  self.socass_qc_temp_couple

            clawback = max(0, max(0, hh.fam_inc_tot - self.socass_qc_exemption_couple) - contributions + add_alimony)
        else:
            basic_amount += self.socass_qc_base_single
            if not hh.dep:
                    basic_amount += self.socass_qc_ajust_single

            clawback = max(0, max(0, hh.fam_inc_tot - self.socass_qc_exemption_single) - contributions + add_alimony)

        if nb_temp_constraints == 1:
            temp_amount +=  self.socass_qc_temp_single

        amount =  max(0, basic_amount + ajustments_kid + temp_amount - clawback) / (1 + hh.couple)

        for p in hh.sp:
            p.inc_sa['social assistance'] = amount
    
    def calc_solidarity(self, hh):
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

        # 1. Montant de base.
        kids_adjustments = self.child_ajustments(hh)
        basic_amount = kids_adjustments

        if nb_sev_constraints== 1:
            basic_amount +=  self.socsol_qc_base_single

            clawback = max(0, max(0, hh.fam_inc_tot - self.socsol_qc_exemption_single))

        elif nb_sev_constraints== 2 :
            basic_amount += self.socsol_qc_base_couple

            clawback = max(0, max(0, hh.fam_inc_tot - self.socsol_qc_exemption_couple))

        amount =  max(0, basic_amount - clawback)/ (1 + hh.couple)

        for p in hh.sp:
           p.inc_sa['social solidarity'] = amount

    def child_ajustments(self,hh):
        """
        Fonction qui calcule l'ajustement des prestations de solidarité sociale selon les caractéristiques des enfants du ménage.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """

        ccap,ccb = 0,0
        for p in hh.sp:
            p.prov_return = {'net_income': 0}
            p.fed_return = {'net_income': 0}
        for p in hh.sp:
            ccap += self.qc.ccap(p, hh)
            ccb += self.fed.ccb(p, hh, iclaw=False)
        for p in hh.sp:
            p.fed_return = None
            p.prov_return = None

        if not hh.nkids_0_17 > 0:
            return 0
        
        #article 68 et 69
        amount_68_69 = hh.nkids_0_17 * self.socass_qc_ajust_kid
        if not hh.couple:
            amount_68_69 += hh.nkids_0_17 * self.socass_qc_ajust_single_kid
        base = max(0,amount_68_69 - ccap)

        #article 70
        amount_70 = self.socass_qc_ajust_kid1
        if hh.nkids_0_17 > 1:
            amount_70 += self.socass_qc_ajust_kid2

        if hh.nkids_0_17 > 2:
            amount_70 += (hh.nkids_0_17 - 2) * self.socass_qc_ajust_kid3
        base += max(0,amount_70 - ccb)

        #article 73
        nkids_12_18 = len([d for d in hh.dep if 12<= d.age < 18])
        if 0 < nkids_12_18 <=2 :
            base += nkids_12_18 * self.socass_qc_ajust_kid12_12yp

        #article 74
        nadult_post_sec = len([s for s in hh.dep if s.age > 18 and s.educ_level == 'Vocational'])
        nadult_post_sec += len([s for s in hh.dep if s.age > 18 and s.educ_level == 'College'])
        nadult_post_sec += len([s for s in hh.dep if s.age > 18 and s.educ_level == 'University'])       
        
        if hh.couple:
         if nadult_post_sec > 0:
            if any(p.disabled for p in hh.sp):
                base += self.socsol_qc_couple_adult_kid1
            else:
                base += self.socass_qc_couple_adult_kid1
         if nadult_post_sec > 1:
            if any(p.disabled for p in hh.sp):
                base += self.socsol_qc_couple_adult_kid2
            else:
                base += self.socass_qc_couple_adult_kid2
        else:
            if nadult_post_sec > 0:
                base += self.socass_qc_mono_adult_kid1
            if nadult_post_sec > 1:
                base += self.socass_qc_mono_adult_kid2

        # article 75
        nadult_sec = len([s for s in hh.dep if s.age > 18 and s.educ_level == 'Secondary'])

        if  nadult_sec > 0:
            base += self.socass_qc_ajust_adult_sec_kid1
        if nadult_sec > 1:
            base += self.socass_qc_ajust_adult_sec_kid2
        if  nadult_sec > 2:
            base += (nadult_sec - 2)*self.socass_qc_ajust_adult_sec_kid3

        # article 75 (disabled)
        nadult_sec_disabled = len([s for s in hh.dep if s.age > 18 and s.educ_level == 'Secondary' and s.disabled])

        if nadult_sec_disabled > 0:
            base += nadult_sec_disabled * self.socass_qc_ajust_adult_dis_kid

        #article 78
        nkids_post_sec = len([s for s in hh.dep if s.educ_level == 'Vocational'])
        nkids_post_sec += len([s for s in hh.dep if s.educ_level == 'College'])
        nkids_post_sec += len([s for s in hh.dep if s.educ_level == 'University'])
        if nkids_post_sec > 0:
           base += nkids_post_sec * self.socass_qc_ajust_post_sec

        # article 196 and article 76 not implemented.

        return base

    def eligibility_assistance_qc(self, hh):
        """
        Fonction qui évalue l'admissibilité de la personne à chacun des 4 volets du programme.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        assets = sum([s.assets for s in hh.sp])
        cutoff = self.socass_qc_assets_couple if hh.couple else self.socass_qc_assets_single

        hh.sa_elig_assets = True

        if assets > cutoff:
            hh.sa_elig_assets = False

        dep = len([s for s in hh.dep if s.age <= self.socass_qc_temp_child_age])

        for p in hh.sp:
          if p.disabled== False:
             if hh.sa_elig_assets and p.emp_temp_constraints :
                p.sa_elig = 'temporary constraints'
             elif hh.sa_elig_assets and p.age>=self.socass_qc_temp_elder_age :
                p.sa_elig = 'temporary constraints'
             elif hh.sa_elig_assets and hh.couple== False and dep>0 :
                p.sa_elig = 'temporary constraints'
             elif hh.sa_elig_assets:   # no temporary nor severe constraints
                p.sa_elig = 'basic'
             else:
                p.sa_elig = False
          else :
             p.sa_elig = False

    def eligibility_solidarity(self, hh):
        """
        Fonction qui évalue l'admissibilité de la personne selon la limite d'actifs.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        assets = sum([s.assets for s in hh.sp])
        cutoff = self.socsol_qc_assets_couple if hh.couple else self.socsol_qc_assets_single

        hh.ss_elig_assets = True

        if assets > cutoff:
            hh.ss_elig_assets = False

        return
    
    def calc_bip(self, p, hh) :
        """
        Montant de base et ajustement pour personne seule (sans conjoint). Prestation calculée par individu.
        """
        pass

    def child_adjustments_bip(self, hh):
        """"
        Parameters: hh: instance de la classe Hhold
        ------
            Returns: Ajustements pour enfants du revenu de base.
        """
        pass
    
    def eligibility_bip(self, p, hh):
        """
        Fonction qui évalue l'admissibilité au revenu de base du ménage selon la limite d'actifs.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        pass

    def calc_assitance_on(self, hh):
        """
        Composante de base et supplément pour enfant pour l'Ontario.

                Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant combiné de la composante de base et du supplément pour enfant pour l'Ontario.
        """
        # assets test
        assets = sum([s.assets for s in hh.sp])
        cutoff = (self.socass_on_assets_couple if hh.couple
                  else self.socass_on_assets_single)
        cutoff += hh.nkids_0_17 * self.socass_on_assets_kid  # check kids age
        if assets > cutoff:
            return 0
        # determine clawback
        exempt = 0
        for p in hh.sp:
            net_earnings = p.inc_earn + p.inc_self_earn - sum(p.payroll.values())
            exempt += min(self.socass_on_exempt, net_earnings)
            if net_earnings > self.socass_on_exempt:
                extra_earnings = net_earnings - self.socass_on_exempt
                exempt += self.socass_on_exempt_rate * extra_earnings
        clawback = max(0, hh.fam_net_inc_prov - exempt)

        ndep_18 = len(hh.dep) - hh.nkids_0_17
        if hh.couple:
            if ndep_18 == 0:
                amount = self.socass_on_couple_no_dep18
            elif ndep_18 == 1:
                amount = self.socass_on_couple_1dep18
            else:
                amount = (self.socass_on_couple_2dep18
                          + (ndep_18 - 2) * self.socass_on_add_dep18)
        else:
            if ndep_18 == 0:
                amount = (self.socass_on_single_no_dep18_kid if hh.nkids_0_17 > 0
                          else self.socass_on_single_no_dep18)
            elif ndep_18 == 1:
                amount = self.socass_on_single_1dep18
            else:
                amount = (self.socass_on_single_2dep18
                          + (ndep_18 - 2) * self.socass_on_add_dep18)

        amount = max(0, amount - clawback) / (1 + hh.couple)

        for s in hh.sp:
            s.inc_sa['social assistance'] = amount
