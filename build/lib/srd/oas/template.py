from srd import add_params_as_attr
import os
module_dir = os.path.dirname(os.path.dirname(__file__))

class template:
    """
    Classe qui contient un template du programme SV (OAS) et SRG (GIS) (tel que rencontré en 2016)

    """

    def file(self, hh):
        """
        Fonction pour appliquer au programme et recevoir une prestation.

        Ceci calcule les prestations pour la SV (OAS) et le SRG (GIS).

        Parameters
        ----------
        hh: Hhold
            instance de la classe acteur Hhold
        """
        for p in hh.sp:
            self.eligibility(p, hh)
        if not [p for p in hh.sp if p.elig_oas]: # eliminate non-eligible hholds
            return

        for p in hh.sp:
            self.compute_net_income(p, hh)
        hh.net_inc_exempt = self.compute_net_inc_exemption(hh)
        for p in hh.sp:
            if not p.elig_oas:
                continue
            p.sq_factor = min(1, p.years_can / self.min_years_can)
            # < 1 if less than 10 years in CAN; seems relevant only in very uncommon cases
            if not hh.couple:
                if p.elig_oas == 'pension':
                    p.inc_oas = self.compute_pension(p, hh)
                    p.inc_gis = self.gis(p, hh, hh.net_inc_exempt, 'high')
                elif p.elig_oas == 'allowance':
                    p.allow_surv = self.survivor_allowance(p, hh)
            else:
                spouse = hh.sp[1-hh.sp.index(p)]
                if p.elig_oas == 'pension':
                    p.inc_oas = self.compute_pension(p, hh)
                    if spouse.elig_oas == 'pension':
                        p.inc_gis = self.gis(p, hh, hh.net_inc_exempt, 'low')
                    elif spouse.elig_oas == 'allowance':
                        income = hh.net_inc_exempt - self.rate_high_inc * self.oas_full * p.sq_factor
                        p.inc_gis = self.gis(p, hh, income, 'low')
                    else:
                        income = hh.net_inc_exempt - self.oas_full * p.sq_factor
                        p.inc_gis = self.gis(p, hh, income, 'high')
                elif p.elig_oas == 'allowance' and spouse.elig_oas == 'pension':
                    p.allow_couple = self.couple_allowance(p, hh)

    def eligibility(self, p, hh):
        """
        Evalue l'éligibilité de la personne pour la SV, le SRG et les allocations
        de couple et de survivant.

        Parameters
        ----------
        p: Person
            instance de la classe acteur Person
        """
        if p.age < self.min_age_allow or p.years_can < self.min_years_can:
            p.elig_oas = False
        elif p.age >= self.min_age_oas + p.oas_years_post:
            p.elig_oas = 'pension'
        elif p.age < self.min_age_oas and (hh.couple or p.widow is True):
            p.elig_oas = 'allowance'
        else:
            p.elig_oas = False

    def compute_net_income(self, p, hh):
        """
        Calcule le revenu net (sans la pension SV).

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        p.fed_return = {k: 0 for k in ['gross_income','deductions_gross_inc','net_income']}
        self.federal.calc_gross_income(p)
        self.federal.calc_deduc_gross_income(p, hh)
        self.federal.calc_net_income(p)

    def compute_net_inc_exemption(self, hh):
        """
        Calcule le revenu net incluant l'exemption sur les revenus du travail salarié

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Revenu net de l'exemption sur les revenus du travail
        """
        net_inc_exempt = 0
        for p in hh.sp:
            exempted_inc = min(p.inc_earn, self.work_exempt)
            payroll = p.payroll['cpp'] + p.payroll['cpp_supp'] + p.payroll['ei']
            net_inc_exempt += max(0, p.fed_return['net_income'] - exempted_inc
                                    - payroll)
        return net_inc_exempt

    def compute_pension(self, p, hh):
        """
        Calcule la pension SV.

        Parameters
        ----------

        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            récupération de la pension SV
        """
        p.oas_65 = min(1, p.years_can / self.max_years_can) * self.oas_full
        p.oas = p.oas_65 * (1 + self.postpone_oas_bonus * p.oas_years_post)
        return self.pension_clawback(p, hh)

    def pension_clawback(self, p, hh):
        """
        Calcul la récupération de la pension SV

        Basé sur le revenu net et incluant la pension SV.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        if p.fed_return['net_income'] + self.oas_full <= self.oas_claw_cutoff:
            return p.oas
        else:
            return max(0, (p.oas - self.oas_claw_rate
            * (p.fed_return['net_income'] - self.oas_claw_cutoff)) / (1 + self.oas_claw_rate))

    def gis(self, p, hh, income, low_high):
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
        low_high: string
            'low'/'high' pour prime et bonus bas/élevé

        Returns
        -------
        float
            Montant du SRG (après récupération)
        """
        if low_high == 'low':
            gis_full, gis_bonus = self.gis_full_low, self.gis_bonus_low
        else:
            gis_full, gis_bonus = self.gis_full_high, self.gis_bonus_high

        if hh.couple:
            bonus_exempt = self.bonus_exempt_couple
        else:
            bonus_exempt = self.bonus_exempt_single

        gis = (gis_full + self.oas_full - p.oas_65) * p.sq_factor
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
        allow = self.compute_allowance(p, hh, self.gis_full_high)
        claw_bonus = self.bonus_claw_rate * max(0, hh.net_inc_exempt - self.bonus_exempt_single)
        return max(0, allow + self.allow_surv_bonus *p.sq_factor - claw_bonus)

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
        allow = self.compute_allowance(p, hh, self.gis_full_low)
        claw_bonus = self.bonus_claw_rate * 1/2 * max(0, hh.net_inc_exempt - self.bonus_exempt_couple)
        return max(0, allow + self.allow_couple_bonus * p.sq_factor - claw_bonus)

    def compute_allowance(self, p, hh, supp_max):
        """
        Calcul de base de l'allocation du survivant ou de couple.

        Parameters
        ----------
        p: Person
            instance de la classe acteur Person
        hh: Hhold
            instance de la classe acteur Hhold
        Returns
        -------
        float
            Allocation du survivant ou de couple de base.
        """
        cutoff = self.rate_high_inc * self.oas_full * p.sq_factor
        allow = supp_max * p.sq_factor
        if hh.net_inc_exempt <= cutoff:
            allow += max(0, self.oas_full * p.sq_factor - self.rate_allow * hh.net_inc_exempt)
        else:
            allow -= self.rate_allow_high_inc * 1/(1+hh.couple) * (hh.net_inc_exempt - cutoff)
        return allow