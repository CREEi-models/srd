from srd import add_params_as_attr, add_schedule_as_attr
import os
import numpy as np
module_dir = os.path.dirname(os.path.dirname(__file__))

def create_return():
        lines = ['gross_income','deductions','net_income','taxable_income','gross_tax_liability',
                 'contributions', 'non_refund_credits','refund_credits','net_tax_liability']
        return dict(zip(lines,np.zeros(len(lines))))

class template:
    """
    Gabarit pour impôt provincial Québec.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/quebec/params/measures_2016.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/quebec/params/schedule_2016.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/quebec/params/chcare_2016.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/quebec/params/health_contrib_2016.csv',delimiter=';')
        return
    def file(self, hh):
        """
        Fonction qui permet de calculer les impôts.

        Cette fonction est celle qui éxécute le calcul des impôts.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        for p in hh.sp:
            p.prov_return = create_return()
            self.calc_gross_income(p)
            self.calc_deductions(p)
            self.calc_net_income(p)
            self.calc_taxable_income(p)
        for p in hh.sp:
            self.calc_tax(p)
            self.calc_non_refundable_tax_credits(p, hh)
            self.calc_contributions(p, hh)
            p.prov_return['net_tax_liability'] = max(0, p.prov_return['gross_tax_liability']
                 + p.prov_return['contributions'] - p.prov_return['non_refund_credits'])
            self.calc_refundable_tax_credits(p, hh)
            p.prov_return['net_tax_liability'] -= p.prov_return['refund_credits']

    def calc_gross_income(self, p):
        """
        Fonction qui calcule le revenu total (brut).

        Cette fonction correspond au revenu total d'une personne au fin de l'impôt.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.prov_return['gross_income'] = p.inc_earn + p.inc_self_earn + p.inc_oas \
                                        + p.inc_gis + p.inc_cpp + p.inc_rpp + p.inc_othtax + p.inc_rrsp

    def calc_net_income(self, p):
        """
        Fonction qui calcule le revenu net au sens de l'impôt.

        Cette fonction correspond au revenu net d'une personne au fin de l'impôt. On y soustrait les déductions.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.prov_return['net_income'] =  p.prov_return['gross_income'] - p.prov_return['deductions']
        return
    def calc_taxable_income(self, p):
        """
        Fonction qui calcule le revenu imposable au sens de l'impôt.

        Cette fonction correspond au revenu imposable d'une personne au fin de l'impôt.
        On y soustrait une portion des gains en capitaux.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.prov_return['taxable_income'] = p.prov_return['net_income']

    def calc_deductions(self, p):
        """
        Fonction qui calcule les déductions.

        Cette fonction fait la somme des différentes déductions du contribuable.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.prov_return['deductions'] = p.con_rrsp
        p.prov_return['deductions'] += p.inc_gis
        p.prov_return['deductions'] += self.work_deduc(p)

    def work_deduc(self, p):
        """
        Fonction qui calcule la déduction pour travailleur.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        work_earn = p.inc_earn + p.inc_self_earn
        if work_earn>0.0:
            deduc = min(work_earn*self.work_deduc_rate,self.work_deduc_max)
        else :
            deduc = 0.0
        return deduc

    def calc_non_refundable_tax_credits(self, p, hh):
        """
        Fonction qui calcule les crédits d'impôt non-remboursable.

        Cette fonction fait la somme de tous les crédits d'impôt modélisés.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        cred_amount = self.get_age_cred(p) + self.get_single_cred(p,hh) \
                      + self.get_pension_cred(p) + self.get_exp_worker_cred(p)
        cred_amount = max(0, cred_amount - self.get_nrtcred_clawback(p,hh))
        p.prov_return['non_refund_credits'] = self.nrtc_rate * (self.nrtc_base
                                              + cred_amount + self.get_disabled_cred(p))

    def get_nrtcred_clawback(self,p,hh):
        """
        Fonction qui calcule la récupération des montants en raison d'âge, vivant seule et revenu de retraite.

        Cette fonction utilise le revenu net du ménage.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        fam_netinc = sum([s.prov_return['net_income'] for s in hh.sp])
        return max(self.nrtc_claw_rate*(fam_netinc - self.nrtc_claw_cutoff),0.0)

    def get_age_cred(self, p):
        """
        Crédit d'impôt selon l'âge.

        Ce crédit est non-remboursable.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.age_cred = self.nrtc_age_max if p.age >= self.nrtc_age else 0
        return p.age_cred

    def get_single_cred(self,p,hh):
        """
        Crédit pour personne seule

        Ce crédit est non-remboursable.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        amount = 0
        if not hh.couple:
            amount += self.nrtc_single
        return amount

    def get_pension_cred(self, p):
        """
        Crédit d'impôt pour revenu de retraite.

        Ce crédit est non-remboursable.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        return min(p.inc_rpp * self.nrtc_pension_factor, self.nrtc_pension_max)

    def get_exp_worker_cred(self, p):
        """
        Crédit d'impôt pour travailleur d'expérience / pour la prolongation de carrière

        Ce crédit est non-remboursable. Nous avons fait l'hypothèse que les travailleurs
        de 65 ans sont nés le 1er janvier (dans l'année en cours, les revenus avant
        et après le 65ème anniversaire sont soumis à des traitments différents,
        ce qui complique beaucoup le modèle mais change peu les résultats.)

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        if p.age < self.exp_work_min_age:
            return 0

        work_inc = p.inc_earn + p.inc_self_earn
        clawback = self.exp_work_claw_rate * max(0, work_inc - self.exp_work_cut_inc)
        adj_tax_liability = max(0, p.prov_return['gross_tax_liability']
                                - self.nrtc_rate * (self.nrtc_base + p.age_cred))
        min_amount = 0

        def calc_amount(max_work_inc, min_amount):
            """
            Calcule le crédit.

            Parameters
            ----------
            max_work_inc: float
                montant maximal de revenu de travail admissible
            min_amount: float
                montant minimal du crédit d'impôt (env. 15% de 4000 pour les individus nés avant 1951)
            """
            base = self.exp_work_rate * min(max_work_inc,
                                            work_inc - self.exp_work_min_inc)
            base_claw_adj = max(min_amount, base - clawback)
            return min(base_claw_adj, adj_tax_liability)

        if p.age == 60:
            return calc_amount(self.exp_work_max_work_inc_60, min_amount)
        elif p.age == 61:
            return calc_amount(self.exp_work_max_work_inc_61, min_amount)
        elif p.age == 62:
            return calc_amount(self.exp_work_max_work_inc_62, min_amount)
        elif p.age == 63:
            return calc_amount(self.exp_work_max_work_inc_63, min_amount)
        elif p.age == 64:
            return calc_amount(self.exp_work_max_work_inc_64, min_amount)
        elif p.age >= 65:
            if p.age > self.exp_work_age_born_bef51:
                min_amount = self.exp_work_min_amount_born_51
            return calc_amount(self.exp_work_max_work_inc_65, min_amount)


    def get_disabled_cred(self, p):
        """
        Crédit d'impôt pour invalidité.

        Ce crédit est non-remboursable.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        amount = self.nrtc_disabled if p.disabled else 0
        return amount

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
        p.prov_return['refund_credits'] = self.witb(p, hh) + self.ccap(p, hh) \
                                          + self.chcare(p, hh) \
                                          + self.solidarity(p, hh)

    def witb(self,p,hh):
        """
        Prime au travail.

        Cette fonction calcule la prime au travail en tenant compte du revenu
        du travail, du revenu pour le ménage et de la présence d'un enfant à charge.
        Pour les couples, la prime est partagée au pro-rata des revenus du travail.
        Le supplément à la prime au travail et la prime au travail adaptée
        ne sont pas calculées.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        Returns
        -------
        float
            Montant de la Prime au travail par individu
        """
        fam_work_inc = sum([p.inc_earn + p.inc_self_earn for p in hh.sp])
        fam_net_inc = sum([p.prov_return['net_income'] for p in hh.sp])
        dependent = len([d for d in hh.dep if d.age <= self.witb_max_age]) > 0

        if fam_work_inc < self.witb_cut_inc_low_single:
            return 0

        def calc_witb(rate, cut_inc_low, cut_inc_high):
            """
            Calcul de la prime au travail.

            Cette fonction calcule la prime au travail pour les couples et les
            individus seuls.

            Parameters
            ----------
            rate: float
                taux qui multiplie le revenu du travail
            cut_inc_low: float
                revenu minimal du travail pour bénéficier de la prime
            cut_inc_high: float
                revenu maximal pris en compte dans le calcul de la prime
            Returns
            -------
            float
                Montant de la Prime au travail par ménage
            """
            amount = rate * max(0, min(cut_inc_high, fam_work_inc) - cut_inc_low)
            clawback = self.witb_claw_rate * max(0, fam_net_inc - cut_inc_high)
            return max(0, amount - clawback)

        if hh.couple:
            rate = self.witb_rate_couple_dep if dependent else self.witb_rate
            fam_witb = calc_witb(rate, self.witb_cut_inc_low_couple,
                             self.witb_cut_inc_high_couple)
            return (p.inc_earn + p.inc_self_earn) / fam_work_inc * fam_witb
        else:
            rate = self.witb_rate_single_dep if dependent else self.witb_rate
            return calc_witb(rate, self.witb_cut_inc_low_single,
                             self.witb_cut_inc_high_single)

    def ccap(self, p, hh):
        """
        Allocation familiale.

        Cette fonction calcule le montant reçu en fonction du nombre d'enfants,
        de la situation familiale (couple/monoparental) et du revenu.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        Returns
        -------
        float
            Montant de l'allocation familiale
        """
        if hh.couple and p.male and hh.sp[0].male != hh.sp[1].male:
            return 0 # heterosexual couple: mother receives benefit

        nkids = len([d for d in hh.dep if d.age < self.ccap_max_age])
        if nkids == 0:
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

        if nkids == 1:
            amount = max(add_amount_min + self.ccap_kid1_min,
                         add_amount_max + self.ccap_kid1_max - clawback)
        elif nkids < 4:
            amount = max(add_amount_min + self.ccap_kid1_min + (nkids - 1) * self.ccap_kid23_min,
                         add_amount_max + self.ccap_kid1_max
                         + (nkids - 1) * self.ccap_kid23_max - clawback)
        else:
            amount = max(add_amount_min + self.ccap_kid1_min + 2 * self.ccap_kid23_min
                         + (nkids - 3) * self.ccap_kid4p_min,
                         add_amount_max + self.ccap_kid1_max + 2 * self.ccap_kid23_max
                         + (nkids - 3) * self.ccap_kid4p_max - clawback)

        if hh.couple and hh.sp[0].male == hh.sp[1].male:
            return amount / 2 # same sex couples get 1/2 each
        else:
            return amount

    def chcare(self ,p, hh):
        """
        Crédit pour frais de garde.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        Returns
        -------
        float
            Montant du crédit pour frais de garde

            Cette fonction calcule le montant reçu en fonction du nombre d'enfants,
            de la situation familiale (couple/monoparental) et du revenu.
        """
        if hh.child_care_exp == 0:
            return 0

        if hh.couple and p.male and hh.sp[0].male != hh.sp[1].male:
            return 0 # heterosexual couple: mother receives benefit

        nkids_0_6 = len([d for d in hh.dep if d.age <= self.chcare_max_age_young])
        nkids_7_16 = len([d for d in hh.dep
                          if self.chcare_max_age_young < d.age <= self.chcare_max_age_old])

        amount = min(hh.child_care_exp,
                     nkids_0_6 * self.chcare_young + nkids_7_16 * self.chcare_old)
        fam_net_inc = sum([s.prov_return['net_income'] for s in hh.sp])
        ind = np.searchsorted(self.chcare_brack, fam_net_inc, 'right') - 1
        net_amount = self.chcare_rate[ind] * amount

        if hh.couple and p.male and hh.sp[0].male != hh.sp[1].male:
            return 0 # heterosexual couple: mother receives benefit

        if hh.couple and hh.sp[0].male == hh.sp[1].male:
            return net_amount / 2 # same sex couples get 1/2 each
        else:
            return net_amount

    def calc_tax(self, p):
        """
        Fonction qui calcule l'impôt à payer selon la table d'impôt.

        Cette fonction utilise la table d'impôt de l'année cours.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        ind = np.searchsorted(self.l_brackets, p.prov_return['taxable_income'], 'right') - 1
        p.prov_return['gross_tax_liability'] = self.l_constant[ind] + \
            self.l_rates[ind] * (p.prov_return['taxable_income'] - self.l_brackets[ind])

    def calc_contributions(self, p, hh):
        """
        Fonction qui calcule l'impôt à payer selon la table d'impôt.

        Cette fonction utilise la table d'impôt de l'année cours.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        p.prov_return['contributions'] += self.add_contrib_subsid_chcare(p, hh)

    def add_contrib_subsid_chcare(self, p, hh):
        """
        Contribution additionnelle pour service de garde éducatifs
        à l'enfance subventionnés.

        Cette fonction calcule le montant dû en fonction
        du nombre de jours de garde et du revenu familial.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        fam_net_inc = sum([p.prov_return['net_income'] for p in hh.sp])
        ndays_chcare = sum([p.ndays_chcare_k1 + p.ndays_chcare_k2 for p in hh.sp])

        if fam_net_inc <= self.add_chcare_min_income or ndays_chcare == 0:
            return 0
        contrib_k1 = self.add_chcare_min_contrib
        if fam_net_inc > self.add_chcare_cutoff_income:
            contrib_k1 += min(self.add_chcare_max_extra_contrib,
                              (fam_net_inc - self.add_chcare_cutoff_income)
                              * self.add_chcare_rate / self.add_chcare_ndays_year)

        return p.ndays_chcare_k1 * contrib_k1 + p.ndays_chcare_k2 * contrib_k1 / 2

    def solidarity(self, p, hh):
        """
        Fonction qui calcule le crédit d'impôt pour solidarité.

        Cette fonction calcule le montant reçu par chacun des conjoints en fonction
        du revenu familial de l'année fiscale courante (cela devrait être l'année précédente).

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        fam_net_inc = sum([p.prov_return['net_income'] for p in hh.sp])
        nkids = len([d for d in hh.dep if d.age < self.solidarity_max_age_kid])
        amount_tvq = self.solidarity_tvq_base
        amount_housing = nkids * self.solidarity_housing_kid
        if hh.couple:
            amount_tvq += self.solidarity_tvq_couple
            amount_housing += self.solidarity_housing_couple
        else:
            amount_tvq += self.solidarity_tvq_single
            amount_housing += self.solidarity_housing_single

        base_claw = max(0, fam_net_inc - self.solidarity_cutoff)
        net_amount_total = max(0, amount_tvq + amount_housing
                               - self.solidarity_rate_total * base_claw)
        net_amount_tvq = max(0, amount_tvq - self.solidarity_rate_tvq * base_claw)
        net_amount = max(net_amount_total, net_amount_tvq)
        return net_amount / (1 + hh.couple)