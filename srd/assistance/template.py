from srd import add_params_as_attr, federal
import os
module_dir = os.path.dirname(os.path.dirname(__file__))

class template:
    """
    Classe qui contient un template du programme d'aide sociale (tel que rencontré en 2016)

    """
    def __init__(self):
        add_params_as_attr(self,module_dir+'/assistance/params/assistance_2016.csv',delimiter=';')
        self.fed = federal.form(2016)
        return
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
        hh.count()
        amount = 0.0
        amount += self.shelter(hh)
        amount += self.basic(hh)
        return amount
    def shelter(self,hh):
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
        return 0.0
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
        # determine assets
        assets = sum([s.asset for s in hh.sp])
        # determine ei, cpp and qpip contributions
        ei_contr = sum([s.payroll['ei'] for s in hh.sp])
        cpp_contr = sum([s.payroll['cpp']+s.payroll['cpp_supp'] for s in hh.sp])
        rap_contr = sum([s.payroll['qpip'] for s in hh.sp])
        # determine numbers of kids
        hh.count()
        # income measure (total from all sources, excludes refundable tax credits)
        tot_inc = sum([s.inc_tot for s in hh.sp])
        # get top off if ccb reduced
        ccb_real = sum([self.fed.ccb(s,hh,iclaw=True) for s in hh.sp])
        ccb_max = sum([self.fed.ccb(s,hh,iclaw=False) for s in hh.sp])
        top_off = max(ccb_max - ccb_real,0.0)
        amount = top_off
        sabc = self.socass_base_couple
        sabs = self.socass_base_single
        sarr = self.socass_reductionrate
        saec = self.socass_exemption_couple
        saes = self.socass_exemption_single
        if hh.couple:
            amount += sabc
            clawback = max(sarr * max(0.0,tot_inc - saec) - ei_contr - cpp_contr - rap_contr,0.0)
        else :
            amount += sabs
            clawback = max(sarr * max(0.0,tot_inc - saes) - ei_contr - cpp_contr - rap_contr,0.0)
        amount = max(amount - clawback, 0.0)
        return amount