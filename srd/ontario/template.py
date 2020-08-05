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
        Fonction qui permet de calculer les impôts.

        Cette fonction est celle qui calcule les déductions,
        les crédits non-remboursables et remboursables et les impôts nets.

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
            # self.calc_div_tax_credit(p)
            # self.calc_contributions(p, hh)
            p.prov_return['net_tax_liability'] = max(0, 
                p.prov_return['gross_tax_liability']
                + p.prov_return['contributions']
                - p.prov_return['non_refund_credits'])
                #  - p.on_div_tax_credit)
            self.calc_refundable_tax_credits(p, hh)
            p.prov_return['net_tax_liability'] -= p.prov_return['refund_credits']

    def copy_fed_return(self, p):
        """
        Fonction qui copie le revenu brut, les déductions,
        ainsi que les revenus nets et imposables du fédéral.

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
        Fonction qui calcule les crédits d'impôt non-remboursables.

        Cette fonction fait la somme de tous les crédits d'impôt modélisés.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        p.on_age_cred = self.get_age_cred(p)
        p.on_spouse_cred = self.get_spouse_cred(p, hh)
        p.on_pension_cred = self.get_pension_cred(p, hh)
        p.on_disabled_cred = self.get_disabled_cred(p)

        p.prov_return['non_refund_credits'] = (
            self.nrtc_rate * (self.nrtc_base + p.on_age_cred + p.on_spouse_cred
                              + p.on_pension_cred + p.on_disabled_cred))

    def get_age_cred(self, p):
        """
        Crédit d'impôt selon l'âge.

        Ce crédit est non-remboursable.

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
        Montant pour époux ou conjoint de fait.

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
            Montant du crédit
        """
        if not hh.couple:
            return 0

        other_p = hh.sp[1 - hh.sp.index(p)]
        amount = self.nrtc_spouse_cutoff - other_p.prov_return['net_income']

        return min(self.ntrc_spouse_max, amount) if amount > 0 else 0

    def get_pension_cred(self, p, hh):
        """
        Crédit d'impôt pour revenu de retraite.

        Ce crédit est non-remboursable.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
            Montant du crédit
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
        Crédit d'impôt pour invalidité.

        Ce crédit est non-remboursable.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
            Montant du crédit
        """
        return self.disability_cred_amount if p.disabled else 0
        # we assume that age >= 18
        # disabled dependent not taken into account (see lines 316 and 318)

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
        p.prov_return['refund_credits'] = p.on_ocb

    def ocb(self, p, hh):
        """
        Prestation ontarienne pour enfants OCB.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant de l'ACE (CCB)
        """
        if hh.nkids_0_17 == 0:
            return 0
        if hh.couple and p.male and hh.sp[0].male != hh.sp[1].male:
            return 0  # heterosexual couple: mother receives benefit

        amount = hh.nkids_0_17 * self.ocb_amount
        adj_fam_net_inc = sum([p.prov_return['net_income'] for p in hh.sp])
        clawback = self.ocb_claw_rate * max(0, adj_fam_net_inc - self.ocb_cutoff)

        if hh.couple and hh.sp[0].male == hh.sp[1].male:
            return max(0, amount - clawback) / 2  # same sex couples get 1/2 each
        else:
            return max(0, amount - clawback)
