from srd import add_params_as_attr, add_schedule_as_attr
import os
import numpy as np
module_dir = os.path.dirname(os.path.dirname(__file__))


def create_return():
    lines = ['gross_income', 'deductions_gross_inc', 'net_income',
             'deductions_net_inc', 'taxable_income', 'gross_tax_liability',
             'non_refund_credits', 'refund_credits',
             'net_tax_liability']
    return dict(zip(lines, np.zeros(len(lines))))
class template:
    """
    Gabarit pour l'impôt provincial québécois.
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
            self.calc_gross_income(p)
            self.calc_deduc_gross_income(p)
            self.calc_net_income(p)
            self.calc_deduc_net_income(p)
            self.calc_taxable_income(p)
        for p in hh.sp:
            self.calc_tax(p)
            self.calc_non_refundable_tax_credits(p, hh)
            self.div_tax_credit(p)
        for p in hh.sp:
            p.prov_return['net_tax_liability'] = max(0, p.prov_return['gross_tax_liability'] - p.prov_return['non_refund_credits']
                 + self.get_spouse_transfer(p, hh) - p.qc_div_tax_credit)
            self.calc_refundable_tax_credits(p, hh)
            p.prov_return['net_tax_liability'] -= p.prov_return['refund_credits']
            self.calc_contributions(p, hh)
            p.prov_return['net_tax_liability'] += sum(list(p.prov_contrib.values()))






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
        p.prov_return['gross_income'] = (p.inc_work + p.inc_ei + p.inc_oas
                                         + p.inc_gis + p.allow_couple
                                         + p.allow_surv + p.inc_cpp + p.inc_rpp
                                         + p.pension_split_qc + p.taxable_div
                                         + p.taxable_cap_gains
                                         + p.inc_othtax + p.inc_rrsp)

    def calc_net_income(self, p):
        """
        Fonction qui calcule le revenu net au sens de l'impôt.

        Cette fonction correspond au revenu net d'une personne aux fins de l'impôt. On y soustrait les déductions.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.prov_return['net_income'] = max(0, p.prov_return['gross_income']
                                            - p.prov_return['deductions_gross_inc'])

    def calc_taxable_income(self, p):
        """
        Fonction qui calcule le revenu imposable au sens de l'impôt.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.prov_return['taxable_income'] = max(0, p.prov_return['net_income']
                                                - p.prov_return['deductions_net_inc'])

    def calc_deduc_gross_income(self, p):
        """
        Fonction qui calcule les déductions.

        Cette fonction fait la somme des différentes déductions du contribuable.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.qc_work_deduc = self.work_deduc(p)
        p.qc_cpp_qpip_deduction = self.cpp_qpip_deduction(p)
        p.prov_return['deductions_gross_inc'] = (p.con_rrsp + p.con_rpp
                                                 + p.qc_work_deduc
                                                 + p.pension_deduction_qc
                                                 + p.qc_cpp_qpip_deduction)

    def work_deduc(self, p):
        """
        Fonction qui calcule la déduction pour travailleur.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant de la déduction.
        """
        work_earn = p.inc_work
        if p.inc_work > 0:
            return min(work_earn * self.work_deduc_rate, self.work_deduc_max)
        else:
           return 0

    def cpp_qpip_deduction(self, p):
        """
        Déduction pour les cotisations RRQ/RPC et au RQAP pour le travail autonome.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant de la déduction.
        """
        p.qc_cpp_deduction = p.contrib_cpp_self / 2

        p.qc_qpip_deduction = self.qpip_deduc_rate * p.contrib_qpip_self
        return p.qc_cpp_deduction + p.qc_qpip_deduction

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
        if hh.sp.index(p)==0:
            for d in hh.sp:
                d.qc_age_cred = self.get_pension_cred(d)
                d.qc_age_cred = self.get_age_cred(d)
                d.qc_living_alone_cred = self.get_living_alone_cred(p, hh)

        if hh.couple==True and p.prov_return['net_income']>(0.5*hh.fam_net_inc_prov):
            cred_amount = hh.sp[0].qc_age_cred + hh.sp[1].qc_age_cred + hh.sp[0].qc_pension_cred + hh.sp[1].qc_pension_cred
            p.qc_age_alone_pension = max(0, cred_amount - self.get_nrtcred_clawback(p, hh))
        elif hh.couple==True and p.prov_return['net_income']<(0.5*hh.fam_net_inc_prov):
            p.qc_age_alone_pension = 0
        elif hh.couple==True and p.prov_return['net_income']==(0.5*hh.fam_net_inc_prov):
            cred_amount = hh.sp[0].qc_age_cred + hh.sp[1].qc_age_cred + hh.sp[0].qc_pension_cred + hh.sp[1].qc_pension_cred
            hh.sp[0].qc_age_alone_pension = max(0, cred_amount - self.get_nrtcred_clawback(p, hh))
            hh.sp[1].qc_age_alone_pension = 0
        elif hh.couple==False:
            cred_amount = p.qc_age_cred + p.qc_pension_cred + p.qc_living_alone_cred
            p.qc_age_alone_pension = max(0, cred_amount - self.get_nrtcred_clawback(p, hh))

        p.qc_disabled_cred = self.get_disabled_cred(p)
        p.qc_med_exp_nr_cred = self.get_med_exp_cred(p, hh)
        p.qc_exp_worker_cred = self.get_exp_worker_cred(p)
        p.qc_donations_cred = self.get_donations_cred(p)
        p.qc_union_dues_cred = self.get_union_dues_cred(p)

        p.prov_return['non_refund_credits'] = (
            self.nrtc_rate * (self.nrtc_base + p.qc_age_alone_pension
                              + p.qc_disabled_cred + p.qc_med_exp_nr_cred)
                              + p.qc_exp_worker_cred + p.qc_union_dues_cred)

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
        return self.nrtc_age_max if p.age >= self.nrtc_age else 0

    def get_living_alone_cred(self, p, hh):
        """
        Fonction qui calcule le crédit d'impôt non-remboursable pour personne vivant seule.

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
        return self.nrtc_living_alone if hh.n_adults_in_hh == 1 else 0

    def get_pension_cred(self, p):
        """
        Fonction qui calcule le crédit d'impôt non-remboursable pour revenu de retraite.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant du crédit.
        """
        pension_split_cred = (p.inc_rpp + p.inc_rrsp - p.pension_deduction_qc
                              + p.pension_split_qc)

        p.qc_pension_cred = min(self.nrtc_pension_max, pension_split_cred * self.nrtc_pension_factor)
        return p.qc_pension_cred

    def get_nrtcred_clawback(self, p, hh):
        """
        Fonction qui calcule la récupération de la somme des crédits non-remboursables 1. en raison de l'âge; 2. pour personne vivant seule; et 3. pour revenu de retraite.

        Cette fonction utilise le revenu net du ménage.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant de la récupération.
        """
        return max(0, self.nrtc_claw_rate*(hh.fam_net_inc_prov - self.nrtc_claw_cutoff))

    def get_exp_worker_cred(self, p):
        """
        Fonction qui calcule le crédit d'impôt non-remboursable pour les travailleurs d'expérience. Depuis 2019, renommé crédit d'impôt pour la prolongation de carrière.

        On fait l'hypothèse que les travailleurs de 65 ans sont nés le 1er janvier de l'année en cours. (En réalité, les revenus gagnés avant et après le 65e anniversaire sont soumis à des traitements différents, ce qui complique beaucoup le modèle mais change peu les résultats.)

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant du crédit.
        """
        if p.age < self.exp_work_min_age:
            return 0

        clawback = self.exp_work_claw_rate * max(0, p.inc_work - self.exp_work_cut_inc)
        adj_tax_liability = max(0, p.prov_return['gross_tax_liability']  # l. 39 TP-1.D
                                  - self.nrtc_rate * (self.nrtc_base + p.qc_age_alone_pension))

        def calc_amount(max_work_inc, min_amount=0):
            """
            Calcule le montant du crédit d'impôt pour les travailleurs d'expérience.

            Parameters
            ----------
            max_work_inc: float
                montant maximal de revenu de travail admissible
            min_amount: float
                montant minimal du crédit d'impôt (en 2016, environ 15% de 4 000 $ pour les individus nés avant 1951)

            Returns
            -------
            float
                Montant du crédit.
            """
            base = max(0, self.exp_work_rate * min(max_work_inc,
                                                   p.inc_work - self.exp_work_min_inc))
            if base <= min_amount:
                return min(base, adj_tax_liability)
            else:
                base_claw_adj = max(min_amount, base - clawback)
                return min(base_claw_adj, adj_tax_liability)

        if p.age == 60:
            return calc_amount(self.exp_work_max_work_inc_60)
        elif p.age == 61:
            return calc_amount(self.exp_work_max_work_inc_61)
        elif p.age == 62:
            return calc_amount(self.exp_work_max_work_inc_62)
        elif p.age == 63:
            return calc_amount(self.exp_work_max_work_inc_63)
        elif p.age == 64:
            return calc_amount(self.exp_work_max_work_inc_64)
        elif p.age >= 65:
            if p.age >= self.exp_work_age_born_bef51:
                min_amount = self.exp_work_min_amount_born_51
            else:
                min_amount = 0
            return calc_amount(self.exp_work_max_work_inc_65,
                               min_amount=min_amount)

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
        tot_donation = p.donation + p.gift

        if tot_donation <= self.nrtc_donation_low_cut:
            return tot_donation * self.nrtc_donation_low_rate
        else:
            return (self.nrtc_donation_low_cut * self.nrtc_donation_low_rate
                    + (tot_donation - self.nrtc_donation_low_cut) * self.nrtc_donation_med_rate)

    def get_union_dues_cred(self, p):
        """
        Fonction qui calcule le crédit d’impôt non-remboursable pour cotisations syndicales et professionnelles.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant du crédit.
        """
        return self.nrtc_union_dues_rate * p.union_dues

    def get_disabled_cred(self, p):
        """
        Fonction qui calcule le crédit d'impôt pour invalidité.

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
        if p is not max(hh.sp, key=lambda p: p.prov_return['taxable_income']):
            return 0

        med_exp = sum([p.med_exp for p in hh.sp] + [d.med_exp for d in hh.dep])
        return max(0, med_exp - self.nrtc_med_exp_rate * hh.fam_net_inc_prov)

    def div_tax_credit(self, p):
        """
        Fonction qui calcule le crédit d'impôt pour dividendes.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.qc_div_tax_credit = (self.div_elig_cred_net_rate * p.div_elig
                               + self.div_other_can_cred_net_rate * p.div_other_can)

    def get_spouse_transfer(self, p, hh):
        """
        Fonction qui récupère le surplus des crédits non rembousables tranferables au conjoint (s'il y lieu).

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        if not hh.couple:
            return 0

        spouse = hh.sp[1 - hh.sp.index(p)]
        transfer = spouse.prov_return['gross_tax_liability'] - spouse.prov_return['non_refund_credits'] - spouse.qc_div_tax_credit
        if transfer < 0:
            return transfer
        else:
            return 0

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

        p.qc_chcare = self.chcare(p, hh)
        p.qc_witb = self.witb(p, hh)
        p.qc_home_support = self.home_support(p, hh)
        p.qc_senior_assist = self.senior_assist(p, hh)
        p.qc_med_exp = self.med_exp(p, hh)

        p.qc_ccap = self.ccap(p, hh)
        p.qc_solidarity = self.solidarity(p, hh)
        p.qc_cost_of_living = self.cost_of_living(p, hh)
        p.qc_tax_shield = self.tax_shield(p, hh)


        l_all_creds = [p.qc_chcare, p.qc_tax_shield, p.qc_witb, p.qc_home_support,
                       p.qc_senior_assist, p.qc_med_exp, p.qc_ccap,
                       p.qc_solidarity, p.qc_cost_of_living]
        l_existing_creds = [cred for cred in l_all_creds if cred]  # removes credits not implemented

        p.prov_return['refund_credits'] = sum(l_existing_creds)

    def chcare(self, p, hh):
        """
        Fonction qui calcule le crédit d'impôt remboursable pour frais de garde.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant du crédit pour frais de garde.

            Cette fonction calcule le montant reçu en fonction du nombre d'enfants,
            de la situation familiale (couple/monoparental) et du revenu.
        """
        if hh.child_care_exp == 0:
            return 0

        if hh.couple and p.male and hh.sp[0].male != hh.sp[1].male:
            return 0 # heterosexual couple: mother receives benefit

        amount = min(hh.child_care_exp,
                     hh.nkids_0_6 * self.chcare_young + hh.nkids_7_16 * self.chcare_old)
        ind = np.searchsorted(self.chcare_brack, hh.fam_net_inc_prov, 'right') - 1
        net_amount = self.chcare_rate[ind] * amount

        if hh.couple and p.male and hh.sp[0].male != hh.sp[1].male:
            return 0 # heterosexual couple: mother receives benefit

        if hh.couple and hh.sp[0].male == hh.sp[1].male:
            return net_amount / 2 # same sex couples get 1/2 each
        else:
            return net_amount

    def witb(self, p, hh):
        """
        Fonction qui calcule la prime au travail.

        Le calcul est fait en tenant compte du revenu de travail,
        du revenu du ménage et de la présence d'un enfant à charge.
        Pour les couples, la prime est partagée au prorata des revenus de travail.

        Notes: le supplément à la prime au travail et la prime au travail adaptée ne sont pas calculés.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        Returns
        -------
        float
            Montant de la prime au travail par individu.
        """
        if hh.fam_inc_work < self.witb_cut_inc_low_single:
            return 0

        def calc_witb(rate, cut_inc_low, cut_inc_high):
            """
            Calcul de la prime au travail.

            Cette fonction calcule la prime au travail pour les couples et les individus seuls.

            Parameters
            ----------
            rate: float
                taux qui multiplie le revenu de travail
            cut_inc_low: float
                revenu de travail minimal requis pour bénéficier de la prime
            cut_inc_high: float
                revenu maximal pris en compte dans le calcul de la prime
            Returns
            -------
            float
                Montant de la prime au travail par ménage.
            """
            amount = rate * max(0, min(cut_inc_high, hh.fam_inc_work) - cut_inc_low)
            clawback = self.witb_claw_rate * max(0, hh.fam_net_inc_prov - cut_inc_high)
            return max(0, amount - clawback)

        if hh.couple:
            rate = self.witb_rate_couple_dep if hh.nkids_0_18 > 0 else self.witb_rate
            fam_witb = calc_witb(rate, self.witb_cut_inc_low_couple,
                             self.witb_cut_inc_high_couple)
            return p.inc_work / hh.fam_inc_work * fam_witb
        else:
            rate = self.witb_rate_single_dep if hh.nkids_0_18 > 0 else self.witb_rate
            return calc_witb(rate, self.witb_cut_inc_low_single,
                             self.witb_cut_inc_high_single)

    def home_support(self, p, hh):
        """
        Fonction qui calcule le crédit d’impôt pour maintien à domicile des aînés.

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
        if p.age < 70:
            return 0

        sp_70 = [p for p in hh.sp if p.age >= self.home_supp_min_age]

        if (len(sp_70) == 2) and (hh.sp.index(p) == 1):
            return 0  # give the credit to first spouse if both 70+

        expenses = sum([p.home_support_cost for p in sp_70])
        max_expenses = sum([self.home_supp_max_dep if p.dep_senior
                            else self.home_supp_max_non_dep for p in sp_70])
        admissible_expenses = min(expenses, max_expenses)
        clawback = self.home_supp_claw_rate * max(0, hh.fam_net_inc_prov - self.home_supp_cutoff)
        no_dep = len([p for p in hh.sp if p.dep_senior]) == 0
        return max(0, self.home_supp_rate * admissible_expenses - no_dep * clawback)

    def senior_assist(self, p, hh):
        """
        Fonction qui calcule le crédit remboursable pour soutien aux ainés.

        En vigueur à partir de 2018.

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
        if p is not max(hh.sp, key=lambda p: p.fed_return['taxable_income']):
            return 0
        if p.inc_work < self.med_exp_min_work_inc:
            return 0
        if hh.fam_net_inc_prov>self.med_exp_max_fam_inc:
            return 0

        base = min(self.med_exp_max, self.med_exp_rate * p.qc_med_exp_nr_cred)
        clawback = self.med_exp_claw_rate * max(0, hh.fam_net_inc_prov - self.med_exp_claw_cutoff)
        return max(0, base - clawback)

    def ccap(self, p, hh):
        """
        Fonction qui calcule le crédit d’impôt remboursable accordant une allocation aux familles (CIRAAF) (qui s'appelait le Soutien aux enfants avant 2019).

        Cette fonction calcule le montant reçu selon le nombre d'enfants, la situation familiale (couple/monoparental) et le revenu.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        Returns
        -------
        float
            Montant de l'Allocation famille.
        """
        if hh.couple and p.male and hh.sp[0].male != hh.sp[1].male:
            return 0 # heterosexual couple: mother receives benefit


        if hh.nkids_0_17 == 0:
            return 0

        fam_netinc = sum([s.prov_return['net_income'] for s in hh.sp])

        if hh.couple:
            clawback = max(0, self.ccap_claw_rate * (fam_netinc - self.ccap_claw_cutoff_couple))
            add_amount_min = 0
            add_amount_max = 0
        else:
            clawback = max(0, 0.04 * (fam_netinc - self.ccap_claw_cutoff_single))
            add_amount_min = self.ccap_amount_single_min
            add_amount_max = self.ccap_amount_single_max

        if hh.nkids_0_17 == 1:
            amount = max(add_amount_min + self.ccap_kid1_min,
                         add_amount_max + self.ccap_kid1_max - clawback)
        elif hh.nkids_0_17 < 4:
            amount = max(add_amount_min + self.ccap_kid1_min + (hh.nkids_0_17 - 1) * self.ccap_kid23_min,
                         add_amount_max + self.ccap_kid1_max
                         + (hh.nkids_0_17 - 1) * self.ccap_kid23_max - clawback)
        else:
            amount = max(add_amount_min + self.ccap_kid1_min + 2 * self.ccap_kid23_min
                         + (hh.nkids_0_17 - 3) * self.ccap_kid4p_min,
                         add_amount_max + self.ccap_kid1_max + 2 * self.ccap_kid23_max
                         + (hh.nkids_0_17 - 3) * self.ccap_kid4p_max - clawback)

        if hh.couple and hh.sp[0].male == hh.sp[1].male:
            return amount / 2  # same sex couples get 1/2 each
        else:
            return amount

    def calc_contributions(self, p, hh):
        """
        Fonction fait la somme des contributions du contribuable. La contribution santé a été abolie en 2017; la contribution additionnelle pour les services de garde éducatifs à l'enfance subventionnés a été abolie en 2019.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
                
        def create_contribution():
            lines = ['drug_insurance_contrib', 'contrib_hsf','add_contrib_subsid_chcare','health_contrib']
            return dict(zip(lines, np.zeros(len(lines))))

        p.prov_contrib = create_contribution()
        p.prov_contrib['add_contrib_subsid_chcare'] = self.add_contrib_subsid_chcare(p, hh)
        p.prov_contrib['health_contrib'] = self.health_contrib(p, hh)
        p.prov_contrib['contrib_hsf'] = self.contrib_hsf(p)

        if p.pub_drug_insurance:
            p.prov_contrib['drug_insurance_contrib'] = self.drug_insurance_contrib(hh)


    def health_contrib(self, p, hh):
        """
        Fonction qui calcule la contribution santé.

        Cette fonction calcule le montant dû en fonction du revenu net. La contribution santé a été abolie en 2017.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        if hh.couple:
            age_spouse = hh.sp[1-hh.sp.index(p)].age

        if p.prov_return['net_income'] <= self.health_cutoff_10:
            return 0
        if not hh.couple:
            cond12 = hh.nkids_0_17 == 1 and hh.fam_net_inc_prov <= self.health_cutoff_12
            cond14 = hh.nkids_0_17 == 2 and hh.fam_net_inc_prov <= self.health_cutoff_14
            if cond12 or cond14:
                return 0
        if hh.couple:
            cond16 = hh.fam_net_inc_prov <= self.health_cutoff_16
            cond18 = hh.nkids_0_17 == 1 and hh.fam_net_inc_prov <= self.health_cutoff_18
            cond20 = hh.nkids_0_17 == 2 and hh.fam_net_inc_prov <= self.health_cutoff_20
            if cond16 or cond18 or cond20:
                return 0

        if not hh.couple and p.age >= self.health_age_high and p.inc_gis > self.health_cutoff_27:
            return 0
        if hh.couple and p.age >= self.health_age_high:
            cond28 = age_spouse >= self.health_age_high and p.inc_gis > self.health_cutoff_28
            cond29 = self.health_age_low <= age_spouse < self.health_age_high and p.inc_gis > self.health_cutoff_29
            cond31 = age_spouse < self.health_age_low and p.inc_gis > self.health_cutoff_31
            if cond28 or cond29 or cond31:
                return 0
        # not sure about conditions 33 and 35 (very uncommon cases)

        ind = np.searchsorted(self.l_health_brackets, p.prov_return['net_income'], 'right') - 1
        return min(self.l_health_max[ind], self.l_health_constant[ind] + \
            self.l_health_rates[ind] * (p.prov_return['net_income'] - self.l_health_brackets[ind]))

    def add_contrib_subsid_chcare(self, p, hh):
        """
        Contribution additionnelle pour les services de garde éducatifs à l'enfance subventionnés.

        Cette fonction calcule le montant dû en fonction du nombre de jours de garde et du revenu familial. Chaque conjoint paie en fonction du nombre de jours de garde sur son relevé 30. La contribution a été abolie en 2019.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        ndays_chcare = sum([p.ndays_chcare_k1 + p.ndays_chcare_k2 for p in hh.sp])

        if hh.fam_net_inc_prov <= self.add_chcare_min_income or ndays_chcare == 0:
            return 0
        contrib_k1 = self.add_chcare_min_contrib
        if hh.fam_net_inc_prov > self.add_chcare_cutoff_income:
            contrib_k1 += min(self.add_chcare_max_extra_contrib,
                              (hh.fam_net_inc_prov - self.add_chcare_cutoff_income)
                              * self.add_chcare_rate / self.add_chcare_ndays_year)

        return p.ndays_chcare_k1 * contrib_k1 + p.ndays_chcare_k2 * contrib_k1 / 2

    def drug_insurance_contrib(self, hh):
        """
        Fonction qui sert à calculer la cotisation au régime d’assurance médicaments du Québec.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        for p in hh.sp:
            if p.age >= self.nrtc_age:
                if hh.couple:
                    if p.inc_gis >= (self.pdip_gis_rate_exempt * self.pdip_gis_max_low):
                        return 0
                else:
                    if p.inc_gis >= (self.pdip_gis_rate_exempt * self.pdip_gis_max_high):
                        return 0
                        
        net_inc_used = hh.fam_net_inc_prov

        if hh.couple:
            net_inc_used -= self.pdip_couple
            if hh.nkids_0_18==1:
                net_inc_used-= self.pdip_couple_kid1
            elif hh.nkids_0_18>1:
                net_inc_used -= self.pdip_couple_kid2p
        else:
            net_inc_used -= self.pdip_single
            if hh.nkids_0_18==1:
                net_inc_used -= self.pdip_single_kid1
            elif hh.nkids_0_18>1:
                net_inc_used -= self.pdip_single_kid2p

        if net_inc_used<=0:
            return 0

        ind = np.searchsorted(self.l_pdip_brackets, net_inc_used, 'right') - 1

        if net_inc_used <= self.l_pdip_brackets[ind]:
            if hh.couple:
                amount = net_inc_used * self.l_pdip_rates_couple[ind]
            else:
                amount = net_inc_used * self.l_pdip_rates_couple[ind]
        else:
            if hh.couple:
                amount = min(self.l_pdip_max[ind], self.l_pdip_constant_couple[ind] + \
                    self.l_pdip_rates_couple[ind] * (net_inc_used - self.l_pdip_brackets[ind]))
            else:
                amount = min(self.l_pdip_max[ind], self.l_pdip_constant_single[ind] + \
                    self.l_pdip_rates_single[ind] * (net_inc_used - self.l_pdip_brackets[ind]))
        amount = min(self.pdip_cutoff, amount)
        return amount


    def solidarity(self, p, hh):
        """
        Fonction qui calcule le crédit d'impôt pour solidarité.

        Cette fonction calcule le montant reçu par chacun des conjoints en fonction du revenu familial de l'année fiscale courante (en réalité, le calcul est basé sur le revenu de l'année précédente).

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
        amount_tvq = self.solidarity_tvq_base
        if hh.couple:
            amount_tvq += self.solidarity_tvq_couple
        elif hh.n_adults_in_hh == 1:
            amount_tvq += self.solidarity_tvq_single

        amount_housing = hh.nkids_0_17 * self.solidarity_housing_kid
        if hh.n_adults_in_hh == 1:
            amount_housing += self.solidarity_housing_alone
        else:
            amount = self.solidarity_housing_not_alone / hh.n_adults_in_hh
            amount_housing += 2 * amount if hh.couple else amount

        base_claw = max(0, hh.fam_net_inc_prov - self.solidarity_cutoff)
        net_amount_total = max(0, amount_tvq + amount_housing
                               - self.solidarity_rate_total * base_claw)
        net_amount_tvq = max(0, amount_tvq - self.solidarity_rate_tvq * base_claw)
        net_amount = max(net_amount_total, net_amount_tvq)
        return net_amount / (1 + hh.couple)

    def cost_of_living(self, p, hh):
        """
       Fonction qui calcule le crédit d'impôt remboursable attribuant une prestation exceptionnelle pour pallier la hausse du coût de la vie et le crédit d'impôt remboursable attribuant un montant ponctuel pour pallier la hausse du coût de la vie.

        En vigueur en 2021 seulement.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        """

        pass


    def contrib_hsf(self, p):
        """
        Fonction qui calcule la cotisation au Fonds des services de santé (FSS).

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        amount = p.inc_self_earn + p.inc_rpp + p.inc_cpp + p.pension_split_qc + p.taxable_cap_gains + p.inc_othtax + p.inc_rrsp - p.contrib_qpip_self
        if amount < self.hsf_high_inc:
            p.qc_contrib_hsf= min(self.hsf_low_cutoff, max(0,(amount - self.hsf_low_inc))*self.hsf_rate)
        else:
            p.qc_contrib_hsf = min(self.hsf_high_cutoff, max(0,(amount - self.hsf_high_inc))*self.hsf_rate + self.hsf_low_cutoff)
        return p.qc_contrib_hsf

    def tax_shield(self, p, hh):
        """
        Fonction qui calcule le crédit d'impôt Bouclier fiscal.

        La part de ce crédit liée à la prime au travail est partagée proportionnellement au revenu des conjoints par rapport au revenu famillial.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        if not p.tax_shield:
            return 0
        if p.prev_inc_work==None:
            return 0
        if hh.prev_fam_net_inc_prov == None:
            return 0

        var_fam_net_inc = max(0,hh.fam_net_inc_prov - hh.prev_fam_net_inc_prov) # 60
        if var_fam_net_inc == 0:
            # VOUS N'AVEZ PAS DROIT AU CREDIT D'IMPOT BOUCLIER FISCAL
            return 0
        modified_fam_inc = hh.fam_net_inc_prov - self.tax_shield_rate * min(sum([(min(max(0,p.inc_work - p.prev_inc_work), self.tax_shield_max_inc_variation)) for p in hh.sp]), var_fam_net_inc) # 70

        # prime au travail
        if p.qc_witb > 0:
            if hh.couple:
                rate = self.witb_rate_couple_dep if hh.nkids_0_18 > 0 else self.witb_rate
                fam_witb = rate * max(0, min(self.witb_cut_inc_high_couple, hh.fam_inc_work) - self.witb_cut_inc_low_couple)
                amount_witb = max(0,fam_witb - (self.witb_claw_rate * max(0, modified_fam_inc - self.witb_cut_inc_high_couple))) # 77
                witb = min(self.tax_shield_max_couple, amount_witb - (p.qc_witb*hh.fam_inc_work /p.inc_work ))# 81
            else:
                rate = self.witb_rate_single_dep if hh.nkids_0_18 > 0 else self.witb_rate
                fam_witb = rate * max(0, min(self.witb_cut_inc_high_single, hh.fam_inc_work) - self.witb_cut_inc_low_single)
                amount_witb = max(0,fam_witb - (self.witb_claw_rate * max(0, modified_fam_inc - self.witb_cut_inc_high_single))) # 77
                witb = min(self.tax_shield_max_single, amount_witb - p.qc_witb) # 81
        else:
            witb = 0
        # frais de garde d'enfants
        if p.qc_chcare > 0:
            if hh.child_care_exp == 0:
                chcare = 0 # heterosexual couple: mother receives benefit
            else:
                amount_care = min(hh.child_care_exp, hh.nkids_0_6 * self.chcare_young + hh.nkids_7_16 * self.chcare_old) # 82
                ind = np.searchsorted(self.chcare_brack, modified_fam_inc, 'right') - 1
                net_amount = self.chcare_rate[ind] * amount_care # 84

                chcare = net_amount - p.qc_chcare # 90
        else:
            chcare = 0

        # crédit d'impot bouclier fiscal
        return (witb + chcare)/(1+hh.couple)  # 96
