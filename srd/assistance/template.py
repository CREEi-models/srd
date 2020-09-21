import os
module_dir = os.path.dirname(os.path.dirname(__file__))


class template:
    """
    Classe qui contient un gabarit du programme d'aide sociale (tel qu'il existait en 2016).

    """

    def apply(self, hh):
        """
        Fonction pour faire une demande au programme et recevoir une prestation.

        Ceci calcule une prestation intégrée d'aide sociale.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant de l'aide sociale
        """
        if hh.prov == 'qc':
            return self.basic_qc(hh)
        else:
            return self.basic_on(hh)

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

    def basic_qc(self, hh):
        """
        Composante de base et supplément pour enfant (en cas de prestation d'ACE réduite) pour le Québec.

        À noter que seul un test d'actifs simplifié est appliqué, à un volet; les actifs liquides (argent comptant et comptes courants) ne sont pas considérés.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant combiné de la composante de base et du supplément pour enfant.
        """
        # assets test: test de ressources? voir docstring
        assets = sum([s.asset for s in hh.sp])
        cutoff = self.socass_qc_assets_couple if hh.couple else self.socass_qc_assets_single
        if assets > cutoff:
            return 0
        # determine ei, cpp and qpip contributions
        contributions = sum([sum(p.payroll.values()) for p in hh.sp])
        # get top off if ccb reduced
        ccb_real = sum([self.fed.ccb(s, hh, iclaw=True) for s in hh.sp])
        ccb_max = sum([self.fed.ccb(s, hh, iclaw=False) for s in hh.sp])
        amount = max(0, ccb_max - ccb_real)

        if hh.couple:
            amount += self.socass_qc_base_couple
            clawback = max(0, max(0, hh.fam_inc_tot - self.socass_qc_exemption_couple)
                           - contributions)
        else:
            amount += self.socass_qc_base_single
            clawback = max(0, max(0, hh.fam_inc_tot - self.socass_qc_exemption_single)
                           - contributions)
        return max(0, amount - clawback) / (1 + hh.couple)

    def basic_on(self, hh):
        """
        Composante de base et supplément pour enfant pour l'Ontario.

        À noter que seul un test d'actifs simplifié est appliqué, à un volet; les actifs liquides (argent comptant et comptes courants) ne sont pas considérés.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant combiné de la composante de base et du supplément pour enfant.
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

        return max(0, amount - clawback) / (1 + hh.couple)
