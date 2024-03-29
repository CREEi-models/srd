import os
import numpy as np
module_dir = os.path.dirname(os.path.dirname(__file__))


def create_return():
    lines = ['gross_income', 'deductions_gross_inc', 'net_income',
             'deductions_net_inc', 'taxable_income', 'gross_tax_liability',
             'non_refund_credits', 'refund_credits', 'net_tax_liability']
    return dict(zip(lines, np.zeros(len(lines))))


class template:
    """
    Gabarit pour l'impôt fédéral.
    """

    def file(self, hh):
        """
        Fonction qui permet de calculer l'impôt.

        Cette fonction est celle qui calcule les déductions,les crédits non-remboursables et remboursables et l'impôt net.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        for p in hh.sp:
            p.fed_return = create_return()
            self.calc_gross_income(p)
            self.calc_deduc_gross_income(p, hh)
            self.calc_net_income(p)
            self.calc_deduc_net_income(p)
            self.calc_taxable_income(p)
        for p in hh.sp:
            self.calc_tax(p)
            self.calc_non_refundable_tax_credits(p, hh)
            self.div_tax_credit(p)
        for p in hh.sp:
            p.fed_return['net_tax_liability'] = max(0, p.fed_return['gross_tax_liability'] - p.fed_return['non_refund_credits']
                 - self.get_spouse_transfer(p, hh) - p.fed_div_tax_credit)
            self.calc_refundable_tax_credits(p, hh)
            p.fed_return['net_tax_liability'] -= p.fed_return['refund_credits']

    def calc_gross_income(self, p):
        """
        Fonction qui calcule le revenu total (brut).

        Cette fonction correspond au revenu total d'une personne aux fins de l'impôt.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.taxable_div = (self.div_elig_factor * p.div_elig
                         + self.div_other_can_factor * p.div_other_can)
        p.taxable_cap_gains = self.cap_gains_rate * max(0, p.net_cap_gains)
        p.fed_return['gross_income'] = (p.inc_work + p.inc_ei + p.inc_oas
                                        + p.inc_gis + p.allow_couple
                                        + p.allow_surv
                                        + p.inc_cpp + p.inc_rpp
                                        + p.pension_split + p.taxable_div
                                        + p.taxable_cap_gains
                                        + p.inc_othtax + p.inc_rrsp)

    def calc_net_income(self, p):
        """
        Fonction qui calcule le revenu net au sens de l'impôt.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.fed_return['net_income'] = max(0, p.fed_return['gross_income']
                                           - p.fed_return['deductions_gross_inc'])

    def calc_taxable_income(self, p):
        """
        Fonction qui calcule le revenu imposable au sens de l'impôt.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.fed_return['taxable_income'] = max(0, p.fed_return['net_income']
                                             - p.fed_return['deductions_net_inc'])

    def calc_deduc_gross_income(self, p, hh):
        """
        Fonction qui calcule les déductions.

        Cette fonction fait la somme des différentes déductions du contribuable.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        p.fed_chcare = self.chcare(p, hh)
        p.fed_cpp_deduction = self.cpp_deduction(p)
        p.fed_qpip_deduction = self.qpip_deduction(p)
        p.fed_return['deductions_gross_inc'] = (p.con_rrsp + p.con_rpp
                                                + p.fed_chcare
                                                + p.pension_deduction
                                                + p.union_dues
                                                + p.fed_cpp_deduction
                                                + p.fed_qpip_deduction)

    def chcare(self, p, hh):
        """
        Fonction qui calcule la déduction fédérale pour frais de garde.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        Returns
        -------
        float
            Montant de la déduction pour frais de garde.

            Cette fonction calcule le montant reçu en fonction des frais de garde, de l'âge des enfants et du revenu le moins élevé du couple. Le montant est reçu par le conjoint qui a le revenu le moins élevé.
        """

        if hh.child_care_exp == 0:
            return 0

        p_low_inc = min(hh.sp, key=lambda p: p.inc_work)
        if p != p_low_inc:
            return 0

        max_chcare = hh.nkids_0_6 * self.chcare_young + hh.nkids_7_16 * self.chcare_old
        return min(max_chcare, hh.child_care_exp, self.chcare_rate_inc * p.inc_work)

    def cpp_deduction(self, p):
        """
        Fonction qui calcule la déduction pour les cotisations au RRQ/RPC pour les travailleurs autonomes.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant de la déduction.
        """
        try:
            p.contrib_cpp_deduc = p.contrib_cpp_self / 2
            return p.contrib_cpp_deduc
        except AttributeError as e:
            msg = 'le ménage doit être passé dans payroll pour obtenir les contributions cpp/rrq et rqap'
            raise Exception(msg) from e

    def qpip_deduction(self, p):
        """
        Fonction qui calcule la déduction pour les cotisations au RQAP pour les travailleurs autonomes.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant de la déduction.
        """
        return self.qpip_deduc_rate * p.contrib_qpip_self

    def calc_deduc_net_income(self, p):
        """
        Fonction qui calcule les déductions suivantes:
        1. Pertes en capital nettes d'autres années;
        2. Déduction pour gain en capital exonéré.

        Permet une déduction maximale égale aux gains en capital taxables nets.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.fed_return['deductions_net_inc'] = min(
            p.taxable_cap_gains,
            p.inc_gis + p.allow_couple + p.allow_surv
            + p.prev_cap_losses + self.cap_gains_rate * p.cap_gains_exempt)

    def calc_tax(self, p):
        """
        Fonction qui calcule l'impôt à payer selon la table d'impôt.

        Cette fonction utilise la table d'impôt de l'année en cours.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        ind = np.searchsorted(self.l_brackets, p.fed_return['taxable_income'], 'right') - 1
        p.fed_return['gross_tax_liability'] = self.l_constant[ind] + \
            self.l_rates[ind] * (p.fed_return['taxable_income'] - self.l_brackets[ind])

    def calc_non_refundable_tax_credits(self, p, hh):
        """
        Fonction qui calcule les crédits d'impôt non-remboursables.

        Cette fonction fait la somme de tous les crédits modélisés
        en appelant les fonctions définies ci-après.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        p.fed_age_cred = self.get_age_cred(p)
        p.fed_cpp_contrib_cred = self.get_cpp_contrib_cred(p)
        p.fed_ei_contrib_cred = self.get_ei_contrib_cred(p)
        p.fed_qpip_cred = self.get_qpip_cred(p)
        p.fed_qpip_self_cred = self.get_qpip_self_cred(p)
        p.fed_empl_cred = self.get_empl_cred(p)
        p.fed_pension_cred = self.get_pension_cred(p, hh)
        p.fed_disabled_cred = self.get_disabled_cred(p)
        p.fed_med_exp_nr_cred = self.get_med_exp_nr_cred(p, hh)
        p.donation_cred = self.get_donations_cred(p)
        p.fed_dep_cred = self.get_dep_cred(p, hh)
        p.fed_spouse_cred = self.get_spouses_cred(p, hh)


        p.fed_return['non_refund_credits'] = (self.rate_non_ref_tax_cred
            * (self.compute_basic_amount(p)+ p.fed_dep_cred + p.fed_spouse_cred + p.fed_age_cred
               + p.fed_cpp_contrib_cred + p.fed_ei_contrib_cred + p.fed_qpip_cred +
               + p.fed_qpip_self_cred + p.fed_empl_cred  + p.fed_pension_cred
               + p.fed_disabled_cred + p.fed_med_exp_nr_cred)
               + p.donation_cred)

    def compute_basic_amount(self, p):
        """
        Fonction qui calcule le montant personnel de base.

        Le calcul de ce montant change en 2020.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant personnel de base
        """
        return self.basic_amount

    def get_age_cred(self, p):
        """
        Fonction qui calcule le crédit d'impôt non-remboursable en raison de l'âge.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant du crédit.
        """
        if p.age < self.min_age_cred:
            return 0

        clawback = self.age_cred_claw_rate * max(0, p.fed_return['net_income'] - self.age_cred_exempt)
        return max(0, self.age_cred_amount - clawback)

    def get_ei_contrib_cred(self, p):
        """
        Fonction qui calcule le crédit d'impôt non-remboursable pour cotisations à l'assurance emploi.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant du crédit.
        """
        return p.contrib_ei

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

    def get_qpip_cred(self, p):
        """
        Fonction qui calcule le crédit d'impôt non-remboursable pour cotisations
        au RQAP de travailleur salarié.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant du crédit.
        """
        return p.contrib_qpip

    def get_qpip_self_cred(self, p):
        """
        Fonction qui calcule le crédit d'impôt non-remboursable
        pour cotisations au RQAP de travailleur autonome.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant du crédit.
        """
        return p.contrib_qpip_self - p.fed_qpip_deduction

    def get_empl_cred(self, p):
        """
        Fonction qui calcule le montant canadien pour emploi.

        Ce crédit est non-remboursable.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant du crédit.
        """
        return min(self.empl_cred_max, p.inc_earn)

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

        return min(self.pension_cred_amount,
                   p.inc_rpp - p.pension_deduction + pension_split_cred)

    def get_disabled_cred(self, p):
        """
        Fonction qui calcule le crédit d'impôt non-remboursable pour invalidité.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant du crédit.
        """
        return self.disability_cred_amount if p.disabled else 0
        # disabled dependent not taken into account (see lines 316 and 318)

    def get_med_exp_nr_cred(self, p, hh):
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
        if p is not min(hh.sp, key=lambda p: p.fed_return['net_income']):
            return 0

        med_exp = sum([p.med_exp for p in hh.sp]
                       + [d.med_exp for d in hh.dep
                          if d.age < self.med_exp_nr_cred_max_age])
        clawback = min(self.med_exp_nr_cred_max_claw,
                       self.med_exp_nr_cred_rate * p.fed_return['net_income'])
        med_exp_other_dep = sum([d.med_exp for d in hh.dep
                                 if d.age >= self.med_exp_nr_cred_max_age])
        # rem: we assume that dependents 18 and over have zero net income (otherwise there would be a clawback)
        return max(0, max(0, med_exp - clawback) + med_exp_other_dep)

    def get_donations_cred(self, p):
        """
        Fonction qui calcule le crédit d'impôt non-remboursable pour dons.

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
            min(self.donation_frac_net * p.fed_return['net_income'],
            p.donation) + p.gift)

        if tot_donation <= self.donation_low_cut:
            return tot_donation * self.donation_low_rate
        else:
            extra_donation = tot_donation - self.donation_low_cut
            high_inc = max(0, p.fed_return['taxable_income']
                             - self.donation_high_cut)
            donation_high_inc = min(extra_donation, high_inc)
            donation_low_inc = extra_donation - donation_high_inc
            return (self.donation_low_cut * self.donation_low_rate
                    + donation_high_inc * self.donation_high_rate
                    + donation_low_inc * self.donation_med_rate)

    def get_spouse_transfer(self, p, hh):
        """
        Fonction qui récupère le surplus des crédits non-remboursables transférables au conjoint (s'il y lieu).

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        if not hh.couple:
            return 0

        spouse = hh.sp[1 - hh.sp.index(p)]
        first_cred = spouse.fed_age_cred + spouse.fed_pension_cred
        if spouse.fed_return['taxable_income'] <= self.l_brackets[1]:
            taxable_inc = spouse.fed_return['taxable_income']
        else:
            taxable_inc = spouse.fed_return['gross_tax_liability']/ self.l_rates[0]

        income_deduction = self.compute_basic_amount(spouse) + spouse.contrib_cpp + spouse.contrib_cpp_self + spouse.contrib_qpip \
        + spouse.contrib_qpip_self + spouse.contrib_ei + spouse.fed_empl_cred

        net_inc = max(0, taxable_inc - income_deduction)
        transfer = max(0, first_cred - net_inc)

        return self.l_rates[0] * transfer


    def div_tax_credit(self, p):
        """
        Fonction qui calcule le crédit d'impôt pour dividendes.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.fed_div_tax_credit = (
            self.div_elig_cred_rate * self.div_elig_factor * p.div_elig
            + self.div_other_can_cred_rate * self.div_other_can_factor * p.div_other_can)

    def calc_refundable_tax_credits(self, p, hh):
        """
        Fonction qui fait la somme des crédits remboursables, en appelant les fonctions suivantes, décrites ailleurs dans cette page: *abatment*, *ccb*, *get_witb*, *get_witbds*, *med_exp*, *gst_hst_credit*.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        p.fed_abatment_qc = self.abatment(p, hh)
        p.fed_ccb = self.ccb(p, hh)
        p.fed_witb = self.get_witb(p, hh)
        p.fed_witbds = self.get_witbds(p, hh)
        p.fed_med_exp = self.med_exp(p, hh)
        p.fed_gst_hst_credit = self.gst_hst_credit(p, hh)

        p.fed_return['refund_credits'] = (
            p.fed_abatment_qc + p.fed_ccb + p.fed_witb + p.fed_witbds
            + p.fed_med_exp + p.fed_gst_hst_credit)

    def abatment(self, p, hh):
        """
        Fonction qui calcule l'abattement du Québec à l'impôt fédéral.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        Returns
        -------
        float
            Montant de l'abattement.
        """
        if hh.prov == 'qc':
            return p.fed_return['net_tax_liability'] * self.rate_abatment_qc
        else:
            return 0

    def ccb(self, p, hh, iclaw=True):
        """
        Fonction qui calcule l'Allocation canadienne pour enfants (ACE).

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        iclaw: boolean
            récupération des prestations si True; pas de récupération si False

        Returns
        -------
        float
            Montant de l'ACE.
        """
        if hh.nkids_0_17 == 0:
            return 0
        if hh.couple and p.male and hh.sp[0].male != hh.sp[1].male:
            return 0  # heterosexual couple: mother receives benefit
        else:
            amount = hh.nkids_0_5 * self.ccb_young + hh.nkids_6_17 * self.ccb_old
            claw_num_ch = min(hh.nkids_0_5 + hh.nkids_6_17, self.ccb_max_num_ch)
            adj_fam_net_inc = sum([p.fed_return['net_income'] for p in hh.sp])

            l_rates_1 = [self.ccb_rate_1_1ch, self.ccb_rate_1_2ch,
                         self.ccb_rate_1_3ch, self.ccb_rate_1_4ch]
            d_rates_1 = {k+1: v for k, v in enumerate(l_rates_1)}
            l_rates_2 = [self.ccb_rate_2_1ch, self.ccb_rate_2_2ch,
                         self.ccb_rate_2_3ch, self.ccb_rate_2_4ch]
            d_rates_2 = {k+1: v for k, v in enumerate(l_rates_2)}
            if iclaw:
                if adj_fam_net_inc > self.ccb_cutoff_2:
                    clawback = (d_rates_2[claw_num_ch] * (adj_fam_net_inc - self.ccb_cutoff_2) +
                                d_rates_1[claw_num_ch] * (self.ccb_cutoff_2 - self.ccb_cutoff_1))
                elif adj_fam_net_inc > self.ccb_cutoff_1:
                    clawback = d_rates_1[claw_num_ch] * (adj_fam_net_inc - self.ccb_cutoff_1)
                else:
                    clawback = 0
            else:
                clawback = 0
            if hh.couple and hh.sp[0].male == hh.sp[1].male:
                return max(0, amount - clawback) / 2  # same sex couples get 1/2 each
            else:
                return max(0, amount - clawback)

    def get_witb(self, p, hh):
        """
        Fonction qui calcule l'Allocation canadienne pour les travailleurs (ACT).

        Avant 2019, celle-ci était appelée la Prestation fiscale pour le revenu de travail (PFRT).

        Dans le cas d'un couple, la prestation est répartie au prorata des revenus de travail.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        Returns
        -------
        float
            Montant de l'ACT.
        """
        self.witb = self.witb_params['qc'] if hh.prov == 'qc' else self.witb_params['on']

        if not hh.couple:
            base = self.witb['base_single']
            rate = self.witb['rate_single_dep'] if hh.nkids_0_18 else self.witb['rate']
            witb_max = self.witb['max_single_dep'] if hh.nkids_0_18 else self.witb['max_single']
            exemption = self.witb['exempt_single_dep'] if hh.nkids_0_18 else self.witb['exempt_single']
            factor = 1
        else:
            base = self.witb['base_couple']
            rate = self.witb['rate_couple_dep'] if hh.nkids_0_18 else self.witb['rate']
            witb_max = self.witb['max_couple_dep'] if hh.nkids_0_18 else self.witb['max_couple']
            exemption = self.witb['exempt_couple_dep'] if hh.nkids_0_18 else self.witb['exempt_couple']
            if hh.fam_inc_work > 0:
                factor = p.inc_work / hh.fam_inc_work
            else:
                factor = 1/2

        return factor * self.compute_witb_witbds(p, hh, rate, base, witb_max,
                                                 self.witb['claw_rate'], exemption)

    def get_witbds(self, p, hh):
        """
        Fonction qui calcule le supplément pour invalidité à la Prestation fiscale pour le revenu de travail (SIPFRT).

        À partir de 2019, le SIPFRT devient le supplément pour invalidité à l'Allocation canadienne pour les travailleurs (ACT).

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant du supplépment pour invalidité.
        """
        if not p.disabled:
            return 0

        couple_dis = sum([p.disabled for p in hh.sp]) == 2
        claw_rate = self.witb['dis_claw_rate']
        if not hh.couple:
            rate = self.witb['dis_rate_single']
            exemption = self.witb['dis_exempt_single_dep'] if hh.nkids_0_18 else self.witb['dis_exempt_single']
        else:
            rate = self.witb['dis_rate_couple']
            exemption = self.witb['dis_exempt_couple_dep'] if hh.nkids_0_18 else self.witb['dis_exempt_couple']
            if couple_dis:
                claw_rate = self.witb['dis_couple_claw_rate']
                exemption = self.witb['dis_exempt_couple_dep'] if hh.nkids_0_18 else self.witb['dis_exempt_couple']

        return self.compute_witb_witbds(p, hh, rate, self.witb['dis_base'],
                                        self.witb['dis_max'], claw_rate, exemption)

    def compute_witb_witbds(self, p, hh, rate, base, witb_max, claw_rate,
                            exemption):
        """
        Fonction appelée par *get_witb* et *get_witbds* pour calculer
        le montant de la PFRT / l'ACT et de son supplément.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        rate: float
            taux appliqué au revenu du travail
        base: float
            montant de base de la PFRT / l'ACT
        witb_max: float
            montant maximal de la PFRT / l'ACT
        claw_rate:
            taux de réduction
        exemption: float
            exemption

        Returns
        -------
        float
            Montant de la PFRT / l'ACT ou du supplément.
        """
        amount = rate * max(0, hh.fam_inc_work - base)
        adj_amount = min(witb_max, amount)
        clawback = claw_rate * max(0, hh.fam_net_inc_fed - exemption)
        return max(0, adj_amount - clawback)

    def med_exp(self, p, hh):
        """
        Fonction qui calcule le crédit remboursable pour frais médicaux.

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
        if p is not min(hh.sp, key=lambda p: p.fed_return['net_income']):
            return 0
        if p.inc_work < self.med_exp_min_work_inc:
            return 0

        base = min(self.med_exp_max, self.med_exp_rate * p.fed_med_exp_nr_cred)  # note line 215 could be added (0 at the moment)
        clawback = self.med_exp_claw_rate * max(0, hh.fam_net_inc_fed - self.med_exp_claw_cutoff)
        return max(0, base - clawback)

    def gst_hst_credit(self, p, hh):
        """
        Fonction qui calcule le crédit pour la taxe sur les produits et services/taxe de vente harmonisée (TPS/TVH).

        Le montant du crédit est reçu par le conjoint au revenu imposable le plus élevé.

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
        if p is not max(hh.sp, key=lambda p: p.fed_return['taxable_income']):
            return 0

        clawback = self.gst_cred_claw_rate * max(0, hh.fam_net_inc_fed - self.gst_cred_claw_cutoff)

        amount = self.gst_cred_base
        if hh.couple or hh.nkids_0_18 >= 1:
            amount += self.gst_cred_base + hh.nkids_0_18 * self.gst_cred_other  # single with kids works same as couple
        else:
            amount += min(self.gst_cred_other,
                          self.gst_cred_rate * max(0, hh.fam_net_inc_fed - self.gst_cred_base_amount))

        return max(0, amount - clawback)

    def get_dep_cred(self, p , hh):
        """
        Fonction qui calcule le montant pour personne à charge admissible.

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
        if hh.couple:
            return 0

        amount = amount_dis = nchild_dis = nchild = 0
        nchild += len(hh.dep)
        if nchild == 0:
            return 0
        else:
            amount += self.compute_basic_amount(p)
            for d in hh.dep:
                if d.disa:
                    nchild_dis +=1
            if nchild_dis >= 1:
                amount_dis += self.dep_disa_amount
            return amount + amount_dis

    def get_spouses_cred(self, p, hh):
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
        if hh.couple:
            higher_inc, equal_inc = 0,0
            if hh.sp[0].fed_return['net_income'] > hh.sp[1].fed_return['net_income']:
                higher_inc = hh.sp[0].fed_return['net_income']
            elif hh.sp[1].fed_return['net_income'] > hh.sp[0].fed_return['net_income']:
                higher_inc = hh.sp[1].fed_return['net_income']
            else:
                equal_inc = hh.sp[1].fed_return['net_income']
        elif not hh.couple or (p.fed_dep_cred != 0):
            return 0

        amount = 0
        if p.fed_return['net_income'] == higher_inc :
            amount += self.compute_basic_amount(p)
            spouse = hh.sp[1 - hh.sp.index(p)]
            if spouse.disabled:
                amount += self.nrtc_spouse_dis
            amount-= spouse.fed_return['net_income']
            return max(0, amount)
        elif p.fed_return['net_income'] == equal_inc:
            amount += self.compute_basic_amount(p)
            spouse = hh.sp[1 - hh.sp.index(p)]
            if spouse.disabled:
                amount += self.nrtc_spouse_dis
            amount-= spouse.fed_return['net_income']
            spouse.fed_spouse_cred = 0
            return max(0, amount)
        else:
            return max(0, amount)
