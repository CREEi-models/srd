from srd import add_params_as_attr
import os
module_dir = os.path.dirname(os.path.dirname(__file__))


class template:
    """
    Programme d'assurance emploi.

    Ce gabarit sert pour l'instant à calculer les cotisations à l'assurance emploi.

    """

    def contrib(self, p, hh):
        """
        Fonction pour calculer les cotisations à l'assurance emploi.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant de la cotisation à l'assurance emploi (annuelle).
        """
        rate = self.rate_EI_qc if hh.prov == 'qc' else self.rate_EI
        p.contrib_ei = 0
        if p.inc_earn > self.min_earn_EI:
            p.contrib_ei = rate * min(p.inc_earn, self.max_earn_EI)
            return p.contrib_ei
        else:
            return 0
