from srd import add_params_as_attr
import os
import numpy as np
module_dir = os.path.dirname(os.path.dirname(__file__))

def create_stub():
    lines = ['cerb', 'cesb', 'iprew', 'crb']
    return dict(zip(lines, np.zeros(len(lines))))

class template:
    """
    Programme d'assurance emploi.

    Ce gabarit sert pour l'instant à calculer les cotisations à l'assurance emploi.

    """
    def compute(self, hh):
        """
        Fonction qui fait le calcul et crée le rapport de cotisations.
        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        for p in hh.sp:
            p.covid = create_stub()
            p.inc_cerb = self.compute_cerb(p)
            p.covid['cerb'] = p.inc_cerb
            p.inc_cesb = self.compute_cesb(p, hh)
            p.covid['cesb'] = p.inc_cesb  
            p.inc_crb = self.compute_crb(p)
            p.covid['crb'] = p.inc_crb
            if hh.prov == 'qc':
                p.inc_iprew = self.compute_iprew(p)
                p.covid['iprew'] = p.inc_iprew

    def compute_cerb(self, p):
        """
        Fonction pour le calcul de la PCU.

        Calcule la PCU en fonction du nombre de blocs de 4 semaines (mois) pour lesquels la prestation est demandée.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant de la PCU.
        """
        if p.months_cerb == 0 or p.prev_inc_work < self.cerb_min_inc_work:
            return 0
        else:
            l_cerb = [self.cerb_base for month
                      in range(self.begin_april, self.begin_april + min(p.months_cerb, self.cerb_max_months))
                      if p.inc_work_month[month] <= self.cerb_max_earn]
            return sum(l_cerb)

    def compute_cesb(self, p, hh):
        """
        Fonction pour le calcul de la PCUE.

        Calcule la PCUE en fonction de la prestation mensuelle à laquelle l'individu a droit et du nombre de blocs de 4 semaines (mois) pour lesquels la prestation est demandée.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant de la PCUE.
        """
        if p.months_cesb == 0:
            return 0
        else:
            monthly_cesb = self.compute_monthly_cesb(p, hh)
            l_cesb = [monthly_cesb for month
                      in range(self.begin_april, self.begin_april + min(p.months_cesb, self.cesb_max_months))
                      if p.inc_work_month[month] <= self.cesb_max_earn]
            return sum(l_cesb)

    def compute_monthly_cesb(self, p, hh):
        """
        Calcule le montant mensuel de la PCUE en fonction du statut (invalidité, dépendants).

        Parameters
        ----------

        Returns
        -------
        float
            Prestation mensuelle de PCUE.
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

    def compute_crb(self, p):
        """
        Fonction qui calcul la Prestation canadienne de la relance économique (PCRE)

        Calcule la PCRE pour la période de 50 semaines (13 mois) si le travailleur est admissible.
        Parameters
        ----------
        p: Person
            instance de la classe Person
        Returns
        -------
        float
            Montant de la PCRE.
        """
        if p.months_crb == 0 or p.prev_inc_work < self.crb_min_inc_work or p.months_ei > 0:
            return 0
        clawback = p.months_crb-self.crb_months_clawback
        
        if clawback >0:
            l_cerb = [self.crb_base_original for i in range(0,self.crb_months_clawback)]
            original_amount = sum(l_cerb)
            l_cerb = [self.crb_base_reduced for i in range(0,min(clawback, self.crb_max_months -self.crb_months_clawback))]
            reduced_amount = sum(l_cerb)
            amount = original_amount + reduced_amount
        else:           
            l_cerb = [self.crb_base_original for i in range(0,p.months_crb)]
            amount = sum(l_cerb)  
        if p.inc_work < self.crb_clawback:
            return amount
        else:
            return max(0,amount-(p.inc_work-self.crb_clawback)*self.crb_rate)