from srd import add_params_as_attr, federal
import os
module_dir = os.path.dirname(os.path.dirname(__file__))


class template:
    """
    Classe qui contient un template du programme d'aide sociale
    (tel que rencontré en 2016)

    """

    def apply(self, hh):
        """
        Fonction pour appliquer au programme et recevoir une prestation.

        Ceci calcule une prestation intégrée d'aide sociale.

        Parameters
        ----------
        hh: Hhold
            instance de la classe acteur Hhold

        Returns
        -------
        float
            Montant de l'aide sociale.
        """
        amount = 0
        amount += self.shelter(hh)
        amount += self.basic(hh)
        return amount

    def shelter(self, hh):
        """
        Composante logement.

        N'est pas implémentée pour l'instant.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant de la composante logement
        """
        return 0

    def basic(self, hh):
        """
        Composante de base et supplément enfant (dénuement ACE).

        À noter que le test de ressources n'est pas appliqué.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant de la composante de base et supplément enfant.
        """
        # assets test
        assets = sum([s.asset for s in hh.sp])
        cutoff = self.socass_assets_couple if hh.couple else self.socass_assets_single
        if assets > cutoff:
            return 0
        # determine ei, cpp and qpip contributions
        contributions = sum([sum(p.payroll.values()) for p in hh.sp])
        # get top off if ccb reduced
        ccb_real = sum([self.fed.ccb(s, hh, iclaw=True) for s in hh.sp])
        ccb_max = sum([self.fed.ccb(s, hh, iclaw=False) for s in hh.sp])
        amount = max(0, ccb_max - ccb_real)

        if hh.couple:
            amount += self.socass_base_couple
            clawback = max(0, max(0, hh.fam_tot_inc - self.socass_exemption_couple)
                              - contributions)
        else:
            amount += self.socass_base_single
            clawback = max(0, max(0, hh.fam_tot_inc - self.socass_exemption_single)
                             - contributions)
        return max(0, amount - clawback) / (1 + hh.couple)
