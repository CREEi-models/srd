from srd import add_params_as_attr
import os
module_dir = os.path.dirname(os.path.dirname(__file__))

class template:
    """
    Régime québécois d'assurance parentale (RQAP).

    Ce gabarit sert pour l'instant à calculer les cotisations au RQAP.

    """
    def contrib(self, p, hh):
        """
        Fonction pour calculer les cotisations à l'assurance parentale.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant de la cotisation à l'assurance parentale (annuelle).
        """
        if p.inc_work <= self.qualifying_threshold_QPIP or hh.prov != 'qc':
            p.contrib_qpip = p.contrib_qpip_self = 0
        elif p.inc_earn <= self.max_QPIP_earn:
            p.contrib_qpip = self.rate_QPIP_earn * p.inc_earn
            p.contrib_qpip_self = self.rate_QPIP_self_earn * min(p.inc_self_earn,
                                                                 self.max_QPIP_earn - p.inc_earn)
        else:
            p.contrib_qpip = self.rate_QPIP_earn * self.max_QPIP_earn
            p.contrib_qpip_self = 0
        return p.contrib_qpip + p.contrib_qpip_self
