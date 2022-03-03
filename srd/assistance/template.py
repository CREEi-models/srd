import os
module_dir = os.path.dirname(os.path.dirname(__file__))


class template:
    """
    Classe qui contient un gabarit du programme d'aide sociale (tel qu'il existait en 2016).

    """

    def file(self, hh):
        """
        Fonction pour faire une demande au programme et recevoir une prestation.

        Cette fonction calcule une prestation intégrée d'aide sociale.

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
            return self.calc_sa_qc(hh)
        else:
            return self.calc_sa_on(hh)

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

    def calc_sa_qc(self, hh):
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
        self.eligibility_qc(hh)
        if not [hh.sa_elig_asset]:  # eliminate non-eligible hholds
            return

        nb_temp_constraints = 0
        if hh.sp[0].sa_elig=='temporary constraints':
            nb_temp_constraints += 1
        if hh.couple:
            if hh.sp[1].sa_elig=='temporary constraints':
                nb_temp_constraints += 1

        # determine ei, cpp and qpip contributions
        contributions = sum([sum(p.payroll.values()) for p in hh.sp])
        # get top off if ccb reduced
        ccb_real = sum([self.fed.ccb(s, hh, iclaw=True) for s in hh.sp])
        ccb_max = sum([self.fed.ccb(s, hh, iclaw=False) for s in hh.sp])
        #basic amount
        basic_amount = max(0, ccb_max - ccb_real) + self.child_ajustments(hh)

        temp_amount = 0
        if hh.couple:
            basic_amount += self.socass_qc_base_couple

            if nb_temp_constraints==2:
                temp_amount = self.socass_qc_temp_couple
            elif  nb_temp_constraints==1:
                temp_amount = self.socass_qc_temp_single

            clawback = max(0, max(0, hh.fam_inc_tot - self.socass_qc_exemption_couple) - contributions)
        else:
            basic_amount += self.socass_qc_base_single
            if hh.sp[0].sa_elig=='temporary constraints':
                temp_amount = self.socass_qc_temp_single
            else:
                if not hh.dep:
                    basic_amount += self.socass_qc_ajust_single

            clawback = max(0, max(0, hh.fam_inc_tot - self.socass_qc_exemption_single) - contributions)

        amount = max(0, basic_amount + temp_amount - clawback) / (1 + hh.couple)

        for p in hh.sp:
            p.inc_sa = amount


    def child_ajustments(self, hh):
        """
        Fonction qui calcule l'ajustement des prestations d'aide sociale selon les caractéristiques des enfants du ménage.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        ccap,ccb = 0,0
        for p in hh.sp:
            ccap += p.qc_ccap
            ccb += p.fed_ccb


        if not hh.nkids_0_17 > 0:
            return 0
        #ajustement article 68 et 69
        amount_68_69 = hh.nkids_0_17 * self.socass_qc_ajust_kid
        if not hh.couple:
            amount_68_69 += hh.nkids_0_17 * self.socass_qc_ajust_single_kid
        base = max(0,amount_68_69 - ccap)

        #ajustement article 70
        amount_70 = self.socass_qc_ajust_kid1
        if hh.nkids_0_17 > 1:
            amount_70 += self.socass_qc_ajust_kid2

        if hh.nkids_0_17 > 2:
            amount_70 += (hh.nkids_0_17 - 2) * self.socass_qc_ajust_kid3
        base += max(0,amount_70 - ccb)

        #ajustement article 73
        nkids_12p = len([d for d in hh.dep if 12<= d.age < 18])
        if 0 < nkids_12p <=2 :
            base += nkids_12p * self.socass_qc_ajust_kid12_12yp

        return base


    def eligibility_qc(self, hh):
        """
        Fonction qui évalue l'admissibilité de la personne à chacun des 4 volets du programme.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        assets = sum([s.asset for s in hh.sp])
        cutoff = self.socass_qc_assets_couple if hh.couple else self.socass_qc_assets_single

        hh.sa_elig_asset = True

        if assets > cutoff:
            hh.sa_elig_asset = False

        dep = len([s for s in hh.dep if s.age <= self.socass_qc_temp_child_age])

        for p in hh.sp:

            if hh.sa_elig_asset and p.emp_temp_constraints:
                p.sa_elig = 'temporary constraints'
            elif hh.sa_elig_asset and p.age>=self.socass_qc_temp_elder_age:
                p.sa_elig = 'temporary constraints'
            elif hh.sa_elig_asset and hh.couple==False and dep>0:
                p.sa_elig = 'temporary constraints'
            elif hh.sa_elig_asset:
                p.sa_elig = 'basic'
            else:
                p.sa_elig = False

    def calc_sa_on(self, hh):
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
        assets = sum([s.asset for s in hh.sp])
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
            s.inc_sa = amount
