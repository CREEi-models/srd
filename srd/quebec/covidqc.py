import os
import numpy as np
from srd import add_params_as_attr

module_dir = os.path.dirname(os.path.dirname(__file__))

def create_stub():
    lines = ['iprew']
    return dict(zip(lines, np.zeros(len(lines))))


class policyqc:
    """
    Mesures liées à la COVID-19.

    Parameters
    ----------
    iiprew: boolean
        le PIRTE est appliqué au Québec
    """
    def __init__(self, iiprew=True):
        self.iiprew = iiprew

    def shut_all_measures(self):
        """
        Ne tient pas compte des mesures spéciales COVID-19 dans la simulation.
        """
        for var in vars(self):
            setattr(self, var, False)

    @property
    def some_measures(self):
        """
        Indique qu'au moins une mesure spéciale COVID-19 est incluse.

        Returns
        -------
        boolean
            True s'il y a au moins une mesure d'incluse, False sinon.
        """
        return any(v is True for k, v in vars(self).items() if k != 'iei')


class programs:
    """
    Calcul des prestations d'urgence liées à la COVID-19: le Programme incitatif pour la rétention des travailleurs essentiels (PIRTE).

    Parameters
    ----------
    policy: policy
        instance de la classe policy
    """
    def __init__(self, policy):
        add_params_as_attr(self, module_dir + '/quebec/params/covid.csv')
        self.policy = policy

    def compute(self, hh):
        """
        Fonction qui fait le calcul et crée le rapport de cotisations.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        for p in hh.sp:
            p.covid = create_stub()
            if self.policy.iiprew and hh.prov == 'qc':
                p.inc_iprew = self.compute_iprew(p)
                p.covid['iprew'] = p.inc_iprew

    def compute_iprew(self, p):
        """
        Fonction pour le calcul du PIRTE.

        Calcule la PIRTE pour la période de 16 semaines (4 mois) si le travailleur est admissible.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant de PIRTE pour les 16 semaines.
        """
        if (not p.essential_worker or p.inc_work < self.iprew_min_inc_work or
            p.inc_tot > self.iprew_max_inc_tot):
            return 0
        else:
            l_iprew = [self.iprew_monthly_amount for month
                       in range(self.begin_april, self.begin_april + self.iprew_max_months)
                       if 0 < p.inc_work_month[month] <= self.iprew_max_earn]
            return sum(l_iprew)
