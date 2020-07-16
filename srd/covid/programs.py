import os
import numpy as np
from srd import add_params_as_attr

module_dir = os.path.dirname(os.path.dirname(__file__))

def create_stub():
    lines = ['cerb', 'cesb', 'iprew']
    return dict(zip(lines, np.zeros(len(lines))))


class policy:
    """
    Mesures liées à la covid-19.

    Permet de choisir quelles mesures sont appliquées dans le simulateur.

    Parameters
    ----------
    icerb: boolean
        PCU est appliquée
    icesb: boolean
        PCUE est appliquée
    iiprew: boolean
        PIRTE est appliquée
    icovid_gst: boolean
        majoration du crédit pour la taxe sur les produits
        et services/taxe de vente harmonisée (TPS/TVH)
    icovid_ccb: boolean
        majoration de l'allocation canadienne pour enfants (ACE/CCB)
    iei: boolean
        Assurance emploi d'urgence
    """
    def __init__(self, icerb=True, icesb=True, iiprew=True, icovid_gst=True,
                 icovid_ccb=True, iei=False):
        self.icerb = icerb
        self.icesb = icesb
        self.iiprew = iiprew
        self.icovid_gst = icovid_gst
        self.icovid_ccb = icovid_ccb
        self.iei = iei

    def shut_all_measures(self):
        """
        Ne tient pas compte des mesures spéciales covid-19 dans la simulation.
        """
        for var in vars(self):
            setattr(self, var, False)

    @property
    def some_measures(self):
        """
        Au moins une mesure spéciale covid-19.

        Returns
        -------
        boolean
            True s'il y a au moins une mesure, False sinon.
        """
        return any(v is True for k, v in vars(self).items() if k != 'iei')


class programs:
    """
    Calcul des prestations d'urgence liées à la covid-19.

    Calcul de la prestation canadienne d'urgence (PCU), prestation canadienne
    d'urgence pour les étudiants (PCUE)
    et programme incitatif pour la rétention des travailleurs essentiels (PIRTE)

    Parameters
    ----------
    policy: policy
        instance de la classe policy
    """
    def __init__(self, policy):
        add_params_as_attr(self, module_dir + '/covid/covid.csv')
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
            if self.policy.icerb:
                p.inc_cerb = self.compute_cerb(p)
                p.covid['cerb'] = p.inc_cerb
            if self.policy.icesb:
                p.inc_cesb = self.compute_cesb(p, hh)
                p.covid['cesb'] = p.inc_cesb
            if self.policy.iiprew and hh.prov == 'qc':
                p.inc_iprew = self.compute_iprew(p)
                p.covid['iprew'] = p.inc_iprew

    def compute_cerb(self, p):
        """
        Fonction pour le calcul de la PCU.

        Calcule la PCU en fonction du nombre de blocs de 4 semaines (mois)
        durant laquelle la prestation est demandée.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Le montant de la PCU.
        """
        if p.months_cerb == 0 or p.prev_inc_work < self.cerb_min_inc_work:
            return 0
        else:
            l_cerb = [self.cerb_base for month
                      in range(self.begin_april, self.begin_april + p.months_cerb)
                      if p.inc_work_month[month] <= self.cerb_max_earn]
            return sum(l_cerb)

    def compute_cesb(self, p, hh):
        """
        Fonction pour le calcul de la PCUE.

        Calcule la PCUE en fonction de la prestation mensuelle à laquelle l'individu
        a droit et du nombre de blocs de 4 semaines (mois) durant lequel la prestation est demandée.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Le montant de la PCUE.
        """
        if p.months_cesb == 0:
            return 0
        else:
            monthly_cesb = self.compute_monthly_cesb(p, hh)
            l_cesb = [monthly_cesb for month
                      in range(self.begin_april, self.begin_april + p.months_cesb)
                      if p.inc_work_month[month] <= self.cesb_max_earn]
            return sum(l_cesb)

    def compute_monthly_cesb(self, p, hh):
        """
        Calcule le montant mensuelle de la PCUE en fonction du statut (invalidité, dépendents)

        Parameters
        ----------

        Returns
        -------
        float
            La prestation mensuelle
        """

        dep = len(hh.dep) > 0
        if p.disabled:
            return self.cesb_base + self.cesb_supp
        if not p.disabled and not dep:
            return self.cesb_base
        if dep:
            if hh.couple:
                spouse = hh.sp[1 - hh.sp.index(p)]
                if spouse.disabled:
                    return self.cesb_base + self.cesb_supp
                else:
                    return self.cesb_base + self.cesb_supp / 2
            else:
                return self.cesb_base + self.cesb_supp

    def compute_iprew(self, p):
        """
        Fonction pour le calcul de la PIRTE.

        Calcule la PIRTE pour la période de 16 semaines (4 mois) si le travailleur est éligible.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Le montant de la PIRTE pour les 16 semaines.
        """
        if (not p.essential_worker or p.inc_work < self.iprew_min_inc_work or
            p.inc_tot > self.iprew_max_inc_tot):
            return 0
        else:
            l_iprew = [self.iprew_monthly_amount for month
                       in range(self.begin_april, self.begin_april + self.iprew_max_months)
                       if 0 < p.inc_work_month[month] <= self.iprew_max_earn]
            return sum(l_iprew)
