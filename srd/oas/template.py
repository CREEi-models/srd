from srd import add_params_as_attr
import os
module_dir = os.path.dirname(os.path.dirname(__file__))

class template:
    """
    Classe qui contient un gabarit du programme de la Sécurité de la vieillesse (PSV, SRG, Allocation et Allocation au survivant), tel qu'il existait en 2016.

    """

    def file(self, hh):
        """
        Fonction pour faire une demande au programme et recevoir une prestation.

        Ceci calcule les prestations pour la PSV, le SRG, l'Allocation et l'Allocation au survivant.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
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
        Fonction qui évalue l'admissibilité de la personne à chacun des 4 volets du programme.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
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
        Fonction qui calcule le revenu net (sans la PSV).

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
        Fonction qui calcule le revenu en sus de l'exemption aux fins du SRG sur les revenus du travail salarié.

        À partir de 2020-2021, les revenus de travail autonome bénéficient également de l'exemption. Les revenus du travail entre 5 000 $ et 10 000 $ bénéficient d'une nouvelle exemption partielle de 50%.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Revenu en sus de l'exemption sur les revenus du travail aux fins du SRG.
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
        Fonction qui calcule la prestation de PSV.

        Parameters
        ----------

        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant de la PSV.
        """
        p.oas_65 = min(1, p.years_can / self.max_years_can) * self.oas_full
        p.oas = p.oas_65 * (1 + self.postpone_oas_bonus * p.oas_years_post)
        return self.pension_clawback(p, hh)

    def pension_clawback(self, p, hh):
        """
        Fonction qui calcule la récupération de la PSV, basée sur le revenu net qui inclut la PSV.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant de la récupération de la PSV.
        """
        if p.fed_return['net_income'] + self.oas_full <= self.oas_claw_cutoff:
            return p.oas
        else:
            return max(0, (p.oas - self.oas_claw_rate
            * (p.fed_return['net_income'] - self.oas_claw_cutoff)) / (1 + self.oas_claw_rate))

    def gis(self, p, hh, income, low_high):
        """
        Fonction qui calcule la prestation de Supplément de revenu garanti.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        income: float
            revenu aux fins du calcul de la récupération du SRG
        low_high: string
            'low'/'high' pour calcul du bonus de SRG pour très faible revenu

        Returns
        -------
        float
            Montant du SRG (après récupération).
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
    
    def compute_allowance(self, p, hh, supp_max):
        """
        Fonction qui calcule le montant maximal de l'Allocation au survivant ou de l'Allocation au conjoint.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        supp_max: float
            prestation maximale de SRG

        Returns
        -------
        float
            Montant maximal de l'Allocation.
        """
        cutoff = self.rate_high_inc * self.oas_full * p.sq_factor
        allow = supp_max * p.sq_factor
        if hh.net_inc_exempt <= cutoff:
            allow += max(0, self.oas_full * p.sq_factor - self.rate_allow * hh.net_inc_exempt)
        else:
            allow -= self.rate_allow_high_inc * 1/(1+hh.couple) * (hh.net_inc_exempt - cutoff)
        return allow

    def survivor_allowance(self, p, hh):
        """
        Fonction qui calcule l'Allocation au survivant, incluant la récupération.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Prestation d'Allocation au survivant, incluant bonus et récupération.
        """
        allow = self.compute_allowance(p, hh, self.gis_full_high)
        claw_bonus = self.bonus_claw_rate * max(0, hh.net_inc_exempt - self.bonus_exempt_single)
        return max(0, allow + self.allow_surv_bonus *p.sq_factor - claw_bonus)

    def couple_allowance(self, p, hh):
        """
        Fonction qui calcule l'Allocation au conjoint.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        Returns
        -------
        float
            Prestation d'Allocation au conjoint.
        """
        allow = self.compute_allowance(p, hh, self.gis_full_low)
        claw_bonus = self.bonus_claw_rate * 1/2 * max(0, hh.net_inc_exempt - self.bonus_exempt_couple)
        return max(0, allow + self.allow_couple_bonus * p.sq_factor - claw_bonus)

