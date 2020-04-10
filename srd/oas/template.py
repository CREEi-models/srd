from srd import add_params_as_attr
import os
module_dir = os.path.dirname(os.path.dirname(__file__))

class template:
    """
    Classe qui contient un template du programme OAS et GIS (tel que rencontré en 2016)

    """
    def __init__(self):
        add_params_as_attr(self,module_dir+'/oas/params/old_age_sec_2016.csv')
        return
    def file(self, hh):
        """
        Fonction pour appliquer au programme et recevoir une prestation.

        Ceci calcule les prestations pour la PSV et le SRG. 

        Parameters
        ----------
        hh: Hhold
            instance de la classe acteur Hhold
        """
        if self.non_elig_old_age(hh):
            return
        self.fileOAS(hh)
        self.compute_special_qualifying_factor(hh)
        self.compute_income_after_work_exemption(hh)
        if not hh.couple:
            p = hh.sp[0]
            if p.inc_oas > 0:
                p.inc_gis = self.gis(p, hh, p.net_inc_exempt)
            elif (self.min_age_allow <= p.age < self.min_age_oas) and p.widow:
                p.allow_surv = self.survivor_allowance(p, hh)
        else:
            p_old, p_young = hh.sp
            if p_old.age < p_young.age:
                p_old, p_young = p_young, p_old

            if p_old.inc_oas == 0:
                if p_young.inc_oas == 0:
                    return
                else: # p_young.inc_oas > 0
                    income = hh.net_inc_exempt - self.oas_full * p_young.sq_factor
                    p_young.inc_gis = self.gis(p_young, hh, income)
            else: # p_old.inc_oas > 0
                if p_young.inc_oas > 0:
                    income = hh.net_inc_exempt
                    for p in hh.sp:
                        p.inc_gis = self.gis(p, hh, income)
                elif 60 <= p_young.age < 65:
                    p_young.allow_couple = self.couple_allowance(p_young, hh)
                    income = hh.net_inc_exempt - self.rate_high_inc * self.oas_full * p_old.sq_factor
                    p_old.inc_gis = self.gis(p_old, hh, income)
                else: # p_young receives no pension or allowances
                    income = hh.net_inc_exempt - self.oas_full * p_old.sq_factor
                    p_old.inc_gis = self.gis(p_old, hh, income)

    def non_elig_old_age(self, hh):
        """
        Fonction pour retourner l'éligibilité à une prestation.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold. 
        Returns
        -------
        Boolean
            Vrai pour non-eligible et Faux pour éligible. 
        """
        if not hh.couple:
            return hh.sp[0].age < self.min_age_allow
        else:
            return max([p.age for p in hh.sp]) < self.min_age_oas

    def fileOAS(self, hh):
        """
        Fonction pour appliquer à la pension de vieillesse.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold. 
        """
        for p in hh.sp:
            if p.age < self.min_age_oas + p.oas_years_post:
                continue # go to next spouse
            if p.years_can is None: # always in Canada after 18
                p.inc_oas = self.oas_full
            elif p.years_can >= self.min_years_can:
                p.inc_oas = min(1, p.years_can/self.max_years_can) * self.oas_full
            p.inc_oas *= 1 + self.postpone_oas_bonus * p.oas_years_post
            self.oas_clawback(p)

    def oas_clawback(self, p):
        """
        Calcul la récupération de la PSV

        Basé sur le revenu net et incluant la PSV. 

        Parameters
        ----------
        p: Person
            instance de la classe acteur Person.
        """
        if p.net_inc + self.oas_full > self.oas_claw_cutoff:
            p.inc_oas = max(0, (self.oas_full - self.oas_claw_rate
            * (p.net_inc - self.oas_claw_cutoff)) / (1 + self.oas_claw_rate))

    def compute_special_qualifying_factor(self, hh):
        """
        Calcul le facteur de qualification.

        Pour les gens ayant vécu au Canada pour moins de 40 ans.
        
        Parameters
        ----------
        hh: Hhold
            instance de la classe acteur Hhold.
        """

        for p in hh.sp:
            p.sq_factor = 1
            if p.years_can:
                p.sq_factor = min(1, p.years_can / self.min_years_can)

    def compute_income_after_work_exemption(self, hh):
        """
        Calcul du revenu après exemption pour travail.
        
        Parameters
        ----------
        hh: Hhold
            instance de la classe acteur Hhold.
        """
        hh.net_inc_exempt = 0
        for p in hh.sp:
            p.inc_work_exempt = max(0, p.inc_work - self.work_exempt)
            p.net_inc_exempt = p.inc_work_exempt + p.inc_non_work
            hh.net_inc_exempt += p.net_inc_exempt

    def gis(self, p, hh, income):
        """
        Calcul du Supplément de revenu garanti.

        Parameters
        ----------
        p: Person
            instance de la classe acteur Person
        hh: Hhold
            instance de la classe acteur Hhold
        income: float
            revenu pour fin du calcul de la récupération du SRG
        
        Returns
        -------
        float
            Montant du SRG (après récupération)
        """
        if hh.couple:
            bonus_exempt = self.bonus_exempt_couple
            gis_full = self.gis_full_couple
            gis_bonus = self.gis_bonus_couple
        else:
            bonus_exempt = self.bonus_exempt_single
            gis_full = self.gis_full_single
            gis_bonus = self.gis_bonus_single

        gis = (gis_full + self.oas_full - p.inc_oas) * p.sq_factor
        claw_gis = self.gis_claw_rate * income / (1+hh.couple)
        bonus = gis_bonus * p.sq_factor
        claw_bonus = self.bonus_claw_rate * max(0, hh.net_inc_exempt - bonus_exempt) / (1+hh.couple)
        return max(0, gis - claw_gis) + max(0, bonus - claw_bonus)

    def survivor_allowance(self, p, hh):
        """
        Calcul de l'allocation du survivant incluant la récupération.

        Parameters
        ----------
        p: Person
            instance de la classe acteur Person
        hh: Hhold
            instance de la classe acteur Hhold
        Returns
        -------
        float
            Allocation du survivant, incluant bonus et récupération.
        """
        allow = self.compute_allowance(p, hh)
        claw_bonus = self.bonus_claw_rate * max(0, p.net_inc_exempt - self.bonus_exempt_single)
        return max(0, allow + self.allow_surv_bonus *p.sq_factor - claw_bonus)

    def compute_allowance(self, p, hh):
        """
        Calcul de base de l'allocation du survivant.

        Parameters
        ----------
        p: Person
            instance de la classe acteur Person
        hh: Hhold
            instance de la classe acteur Hhold
        Returns
        -------
        float
            Allocation du survivant de base.
        """
        cutoff = self.rate_high_inc * self.oas_full * p.sq_factor
        allow = self.gis_full_single * p.sq_factor
        if hh.net_inc_exempt <= cutoff:    
            allow += max(0, self.oas_full * p.sq_factor - self.rate_allow * hh.net_inc_exempt)
        else:
            allow -= self.rate_allow_high_inc * 1/(1+hh.couple) * (hh.net_inc_exempt - cutoff)
        return allow

    def couple_allowance(self, p, hh):
        """
        Calcul de l'allocation pour conjoint.

        Parameters
        ----------
        p: Person
            instance de la classe acteur Person
        hh: Hhold
            instance de la classe acteur Hhold
        Returns
        -------
        float
            Allocation du conjoint.
        """
        allow = self.compute_allowance(p, hh)
        claw_bonus = self.bonus_claw_rate * 1/(1+hh.couple) * \
            max(0, hh.net_inc_exempt - self.bonus_exempt_couple)
        return max(0, allow + self.allow_couple_bonus * p.sq_factor - claw_bonus)