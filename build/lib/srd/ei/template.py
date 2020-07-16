from srd import add_params_as_attr
import os
module_dir = os.path.dirname(os.path.dirname(__file__))


class template:
    """
    Programme d'assurance emploi.

    Ce gabarit sert pour l'instant à calculer les cotisations à l'assurance emploi.

    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/ei/params/parameters_2016.csv')

    def contrib(self, p, hh):
        """
        Fonction pour calculer les contributions à l'assurance emploi.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            montant de la cotisation à l'assurance emploi (annuelle)
        """
        rate = self.rate_EI_qc if hh.prov == 'qc' else self.rate_EI
        if p.inc_earn > self.min_earn_EI:
            return rate * min(p.inc_earn, self.max_earn_EI)
        else:
            return 0
