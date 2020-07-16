from srd import add_params_as_attr
import os
module_dir = os.path.dirname(os.path.dirname(__file__))

class template:
    """
    Programme québécois d'assurance parentale.

    Ce gabarit sert pour l'instant à calculer les cotisations au programme québécois d'assurance parentale.

    """
    def __init__(self):
        add_params_as_attr(self,module_dir+'/qpip/params/parameters_2016.csv')
        return
    def contrib(self, p, hh):
        """
        Fonction pour calculer les contributions à l'assurance parentale.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant de la cotisation à l'assurance parentale (annuelle)
        """
        if p.inc_work <= self.qualifying_threshold_QPIP:
            p.contrib_qpip = p.contrib_qpip_self = 0
            return 0
        elif p.inc_earn <= self.max_QPIP_earn:
            p.contrib_qpip = self.rate_QPIP_earn * p.inc_earn
            p.contrib_qpip_self = self.rate_QPIP_self_earn * min(p.inc_self_earn,
                                                                 self.max_QPIP_earn - p.inc_earn)
        else:
            p.contrib_qpip = self.rate_QPIP_earn * self.max_QPIP_earn
            p.contrib_qpip_self = 0
        return p.contrib_qpip + p.contrib_qpip_self


