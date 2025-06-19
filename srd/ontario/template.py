import os
import numpy as np
module_dir = os.path.dirname(os.path.dirname(__file__))


def create_return():
    lines = ['gross_income', 'deductions_gross_inc', 'net_income',
             'deductions_net_inc', 'taxable_income', 'gross_tax_liability',
             'contributions', 'non_refund_credits', 'refund_credits',
             'net_tax_liability']
    return dict(zip(lines, np.zeros(len(lines))))


class template:
    """
    Gabarit pour l'impôt provincial ontarien.
    """

    def file(self, hh):
        """
        Fonction qui permet de calculer l'impôt.

        Cette fonction est celle qui calcule les déductions, les crédits non-remboursables et remboursables et l'impôt net.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        for p in hh.sp:
            p.prov_return = create_return()
            self.copy_fed_return(p)

        for p in hh.sp:
            self.calc_tax(p)
            self.calc_non_refundable_tax_credits(p, hh)
            p.prov_return['net_tax_liability'] = max(0,
                p.prov_return['gross_tax_liability']
                - p.prov_return['non_refund_credits'])

            self.surtax(p)
            self.div_tax_credit(p)
            p.prov_return['net_tax_liability'] = max(0,
                p.prov_return['net_tax_liability'] + p.on_surtax - p.on_div_tax_credit)

            self.tax_reduction(p, hh)
            p.prov_return['net_tax_liability'] = max(0,
                p.prov_return['net_tax_liability'] - p.on_tax_reduction)

            self.lift_credit(p, hh)
            if hasattr(p, 'on_lift'):
                p.prov_return['net_tax_liability'] = max(0,
                    p.prov_return['net_tax_liability'] - p.on_lift)

            self.calc_contributions(p)
            p.prov_return['net_tax_liability'] += p.prov_return['contributions']
            self.calc_refundable_tax_credits(p, hh)
            p.prov_return['net_tax_liability'] -= p.prov_return['refund_credits']

    def copy_fed_return(self, p):
        """
        Fonction qui copie le revenu brut, les déductions, ainsi que les revenus net et imposable du formulaire fédéral.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        for line in ['gross_income', 'deductions_gross_inc', 'net_income',
                     'deductions_net_inc', 'taxable_income']:
            p.prov_return[line] = p.fed_return[line]

    def calc_tax(self, p):
        """
        Fonction qui calcule l'impôt à payer selon la table d'impôt.

        Cette fonction utilise la table d'impôt de l'année en cours.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        ind = np.searchsorted(self.l_brackets, p.prov_return['taxable_income'], 'right') - 1
        p.prov_return['gross_tax_liability'] = self.l_constant[ind] + \
            self.l_rates[ind] * (p.prov_return['taxable_income'] - self.l_brackets[ind])

    def calc_non_refundable_tax_credits(self, p, hh):
        """
        Fonction qui fait la somme de tous les crédits d'impôt non-remboursables modélisés.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        p.on_age_cred = self.get_age_cred(p)
        p.on_spouse_cred = self.get_spouse_cred(p, hh)
        p.on_cpp_contrib_cred = self.get_cpp_contrib_cred(p)
        p.on_pension_cred = self.get_pension_cred(p, hh)
        p.on_disabled_cred = self.get_disabled_cred(p)
        p.on_med_exp_nr_cred = self.get_med_exp_cred(p, hh)
        p.on_donation = self.get_donations_cred(p)

        p.prov_return['non_refund_credits'] = (
            self.nrtc_rate * (self.nrtc_base + p.on_age_cred + p.on_spouse_cred
            + p.on_cpp_contrib_cred + p.on_pension_cred + p.on_disabled_cred
            + p.on_med_exp_nr_cred) + p.on_donation)

    def get_age_cred(self, p):
        """
        Fonction qui calcule le crédit d'impôt non-remboursable provincial en raison de l'âge.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant du crédit
        """
        if p.age < self.nrtc_age:
            return 0

        clawback = (self.nrtc_age_claw_rate * max(0, p.prov_return['net_income']
                    - self.nrtc_age_claw_cutoff))
        return max(0, self.nrtc_age_amount - clawback)

    def get_spouse_cred(self, p, hh):
        """
        Fonction qui calcule le montant pour époux ou conjoint de fait.

        Ce crédit est non-remboursable.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant du crédit.
        """
        if not hh.couple:
            return 0

        other_p = hh.sp[1 - hh.sp.index(p)]
        amount = self.nrtc_spouse_cutoff - other_p.prov_return['net_income']

        return min(self.nrtc_spouse_max, amount) if amount > 0 else 0

    def get_cpp_contrib_cred(self, p):
        """
        Fonction qui calcule le crédit d'impôt non-remboursable pour cotisations au RRQ/RPC.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant du crédit.
        """
        return p.contrib_cpp + p.contrib_cpp_self / 2

    def get_pension_cred(self, p, hh):
        """
        Fonction qui calcule le crédit d'impôt non-remboursable pour revenu de retraite.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la class Hhold

        Returns
        -------
        float
            Montant du crédit.
        """
        if hh.elig_split and (p.age < self.pension_cred_min_age_split):
            other_p = hh.sp[1 - hh.sp.index(p)]
            pension_split_cred = min(p.pension_split, 0.5 * other_p.inc_rpp)
        else:
            pension_split_cred = p.pension_split

        return min(self.nrtc_pension_cred_amount,
                   p.inc_rpp - p.pension_deduction + pension_split_cred)

    def get_disabled_cred(self, p):
        """
        Fonction qui calcule le crédit d'impôt non-remboursable pour invalidité.

        Seule la portion pour le contribuable majeur lui-même est modélisée.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant du crédit.
        """
        return self.nrtc_disabled if p.disabled else 0
        # we assume that age >= 18
        # disabled dependent not taken into account (see lines 316 and 318)

    def get_med_exp_cred(self, p, hh):
        """
        Fonction qui calcule le crédit d'impôt non-remboursable pour frais médicaux.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant du crédit.
        """
        if p is not min(hh.sp, key=lambda p: p.prov_return['net_income']):
            return 0

        med_exp = sum([p.med_exp for p in hh.sp]
                       + [d.med_exp for d in hh.dep
                          if d.age < self.nrtc_med_exp_age])
        clawback = min(self.nrtc_med_exp_claw,
                       self.nrtc_med_exp_rate * p.prov_return['net_income'])
        med_exp_other_dep = sum([min(d.med_exp, self.nrtc_med_exp_max_dep) for d in hh.dep
                                 if d.age >= self.nrtc_med_exp_age])
        # rem: we assume that dependents 18 and over have zero net income (otherwise there would be a clawback)
        return max(0, max(0, med_exp - clawback) + med_exp_other_dep)

    def get_donations_cred(self, p):
        """
        Fonction qui calcule le crédit d'impôt non-remboursable pour dons de l'Ontario.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant du crédit.
        """
        tot_donation = (
            min(self.nrtc_donation_frac_net * p.prov_return['net_income'],
            p.donation) + p.gift)

        if tot_donation <= self.nrtc_donation_cutoff:
            return tot_donation * self.nrtc_donation_low_rate
        else:
            extra_donation = tot_donation - self.nrtc_donation_cutoff
            return (self.nrtc_donation_cutoff * self.nrtc_donation_low_rate
                    + extra_donation * self.nrtc_donation_high_rate)

    def surtax(self, p):
        """
        Fonction qui calcule la surtaxe de l'Ontario.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.on_surtax = (
            self.surtax_low_rate * max(0, p.prov_return['net_tax_liability'] - self.surtax_low_cutoff)
            + self.surtax_high_rate * max(0, p.prov_return['net_tax_liability'] - self.surtax_high_cutoff))

    def div_tax_credit(self, p):
        """
        Fonction qui calcule le crédit d'impôt pour dividendes de l'Ontario.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.on_div_tax_credit = (
            self.div_elig_cred_rate * self.div_elig_factor * p.div_elig
            + self.div_other_can_cred_rate * self.div_other_can_factor * p.div_other_can)

    def tax_reduction(self, p, hh):
        """
        Fonction qui calcule la réduction de l’impôt de l’Ontario.

        Ce montant est non-remboursable.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """

        if p is not max(hh.sp, key=lambda p: p.prov_return['net_income']):
            p.on_tax_reduction = 0
        else:
            amount = 2 * (self.reduction_base + hh.nkids_0_18 * self.reduction_kid)
            p.on_tax_reduction = max(0, amount - p.prov_return['net_tax_liability'])

    def lift_credit(self, p, hh):
        """
        Crédit d’impôt pour les personnes et les familles à faible revenu (Low-income individuals and families tax credit: LIFT).

        Ce crédit entre en vigueur en 2019. Il est non-remboursable.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        pass

    def calc_refundable_tax_credits(self, p, hh):
        """
        Fonction qui fait la somme des crédits remboursables.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        p.on_ocb = self.ocb(p, hh)
        p.on_ostc = self.ostc(p, hh)
        p.on_oeptc = self.oeptc(p,hh)
        p.prov_return['refund_credits'] = p.on_ocb + p.on_ostc + p.on_oeptc

    def ocb(self, p, hh):
        """
        Fonction qui calcule l'Allocation ontarienne pour enfants.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant de l'Allocation ontarienne pour enfants.
        """
        if hh.nkids_0_17 == 0:
            return 0
        if hh.couple and p.male and hh.sp[0].male != hh.sp[1].male:
            return 0  # heterosexual couple: mother receives benefit

        amount = hh.nkids_0_17 * self.ocb_amount
        clawback = self.ocb_claw_rate * max(0, hh.fam_net_inc_prov - self.ocb_cutoff)

        if hh.couple and hh.sp[0].male == hh.sp[1].male:
            return max(0, amount - clawback) / 2  # same sex couples get 1/2 each
        else:
            return max(0, amount - clawback)

    def ostc(self, p, hh):
        """
        Crédit de taxe de vente de l'Ontario.

        Ce crédit est remboursable.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant du crédit.
        """
        if hh.sp.index(p) == 1:
            return 0

        amount = (len(hh.sp) + hh.nkids_0_18) * self.ostc_amount
        if hh.couple or hh.nkids_0_18:
            cutoff = self.ostc_couple_dep_cutoff
        else:
            cutoff = self.ostc_single_cutoff
        clawback = self.ostc_claw_rate * max(0, hh.fam_net_inc_prov - cutoff)
        return max(0, amount - clawback)

    def chcare(self,p, hh):
        """
        Fonction qui calcule le Crédit d'impôt de l'Ontario pour l'accès aux services de garde d'enfants et l'allègement des dépenses (ASGE)
                
        Ce crédit est remboursable.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant du crédit.
        """
        
        pass

    def calc_contributions(self, p):
        """
        Fonction qui fait la somme des contributions du contribuable (actuellement, seule la contribution santé est incluse).

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.prov_return['contributions'] = self.health_contrib(p)

    def health_contrib(self, p):
        """
        Contribution santé de l'Ontario (Ontario health premium).

        Cette fonction calcule le montant dû en fonction du revenu imposable.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        tax_inc = p.prov_return['taxable_income']

        if tax_inc <= self.l_health_high_brackets[-1]:
            ind = np.searchsorted(self.l_health_high_brackets, tax_inc)
            return (self.l_health_base[ind]
                    + self.l_health_rates[ind]
                    * max(0, tax_inc - self.l_health_low_brackets[ind]))
        else:
            return self.l_health_base[-1]

    def caip(self,p ,hh):
        """
        Fonction qui calcule le crédit de l’incitatif à agir pour le climat (IAC) ou encore le Paiement de l’incitatif à agir pour le climat (PIAC)

        Ce crédit est remboursable.
        
        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant du crédit.
        """
        pass

    def oeptc(self,p ,hh):
        """
        Fonction qui calcule le Crédit d’impôt remboursable de l’Ontario pour les coûts d’énergie et les impôts fonciers (CIOCEIF)

        Ce crédit est remboursable.
        
        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant du crédit.
        """
        # energy
        on_energy = min(self.oeptc_energy_amount, self.oeptc_rent_rate*hh.rent + p.prop_tax)
        # property tax
        if p.age>=65:
            on_prop_tax = min(self.oeptc_prop_old,self.oeptc_prop_tax_rate*hh.rent) + self.oeptc_prop_amount_old
        # crédit
            amount = on_energy + on_prop_tax
            if hh.couple:
                amount_oeptc = max(0, amount - self.oeptc_rate*max(0, hh.fam_net_inc_fed - self.oeptc_cutoff_couple_old))
            elif not hh.couple and hh.nkids_0_17 != 0:
                amount_oeptc = max(0, amount - self.oeptc_rate*max(0, hh.fam_net_inc_fed - self.oeptc_cutoff_couple_old))
            else:
                amount_oeptc = max(0, amount - self.oeptc_rate*max(0, hh.fam_net_inc_fed - self.oeptc_cutoff_single_old))
        else:
            on_prop_tax = min(self.oeptc_prop,self.oeptc_prop_tax_rate*hh.rent) + self.oeptc_prop_amount
        # crédit
            amount = on_energy + on_prop_tax
            if hh.couple:
                amount_oeptc = max(0, amount - self.oeptc_rate*max(0, hh.fam_net_inc_fed - self.oeptc_cutoff_couple))
            elif not hh.couple and hh.nkids_0_17 != 0:
                amount_oeptc = max(0, amount - self.oeptc_rate*max(0, hh.fam_net_inc_fed - self.oeptc_cutoff_couple))
            else:
                amount_oeptc = max(0, amount - self.oeptc_rate*max(0, hh.fam_net_inc_fed - self.oeptc_cutoff_single))
        
        return amount_oeptc