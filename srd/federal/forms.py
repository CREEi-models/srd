from srd import add_params_as_attr, get_params, add_schedule_as_attr, covid
import os
from srd.federal import template
from srd import ei
module_dir = os.path.dirname(os.path.dirname(__file__))

# wrapper to pick correct year
def form(year):
    """
    Fonction qui permet de sélectionner le formulaire d'impôt fédéral par année.

    Returns
    -------
    class instance
        Une instance du formulaire pour l'année sélectionnée.
    """
    if year==2016:
        p = form_2016()
    if year==2017:
        p = form_2017()
    if year==2018:
        p = form_2018()
    if year==2019:
        p = form_2019()
    if year==2020:
        p = form_2020()
    if year == 2021:
        p = form_2021()
    if year == 2022:
        p = form_2022()
    if year == 2023:
        p = form_2023()
    return p

class form_2016(template):
    """
    Formulaire d'impôt de 2016.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/federal/params/federal_2016.csv')
        add_schedule_as_attr(self, module_dir + '/federal/params/schedule_2016.csv')
        self.witb_params = {}
        for prov in ['on', 'qc']:
            self.witb_params[prov] = get_params(
                module_dir + f'/federal/params/fed_witb_{prov}_2016.csv')

class form_2017(form_2016):
    """
    Formulaire d'impôt de 2017.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir+'/federal/params/federal_2017.csv')
        add_params_as_attr(self, module_dir + '/federal/params/fed_witb_qc_2017.csv')
        add_schedule_as_attr(self, module_dir + '/federal/params/schedule_2017.csv')
        self.witb_params = {}
        for prov in ['on', 'qc']:
            self.witb_params[prov] = get_params(
                module_dir + f'/federal/params/fed_witb_{prov}_2017.csv')

class form_2018(form_2017):
    """
    Formulaire d'impôt de 2018.
    """
    def __init__(self):
        add_params_as_attr(self,module_dir+'/federal/params/federal_2018.csv')
        add_params_as_attr(self, module_dir + '/federal/params/fed_witb_qc_2018.csv')
        add_schedule_as_attr(self, module_dir + '/federal/params/schedule_2018.csv')
        self.witb_params = {}
        for prov in ['on', 'qc']:
            self.witb_params[prov] = get_params(
                module_dir + f'/federal/params/fed_witb_{prov}_2018.csv')

class form_2019(form_2018):
    """
    Formulaire d'impôt de 2019.
    """
    def __init__(self):
        add_params_as_attr(self,module_dir+'/federal/params/federal_2019.csv')
        add_params_as_attr(self, module_dir + '/federal/params/fed_witb_qc_2019.csv')
        add_schedule_as_attr(self, module_dir + '/federal/params/schedule_2019.csv')
        self.witb_params = {}
        for prov in ['on', 'qc']:
            self.witb_params[prov] = get_params(
                module_dir + f'/federal/params/fed_witb_{prov}_2019.csv')

    def cpp_deduction(self, p):
        """
        Fonction qui calcule la déduction pour les cotisations au RRQ/RPC de base pour les travailleurs autonomes et pour le régime supplémentaire du RRQ/RPC pour tous.

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
            p.contrib_cpp_deduc += p.payroll['cpp_supp']
            return p.contrib_cpp_deduc
        except AttributeError as e:
            msg = 'le ménage doit être passé dans payroll pour obtenir les contributions cpp/rrq et rqap'
            raise Exception(msg) from e
    
    def get_disabled_cred(self, p, hh):
        """
        Fonction qui calcule le crédit d'impôt non-remboursable pour personnes handicapées : 
          - montant pour le déclarant
          - montant transféré d'une personne à charge.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant du crédit.
        """
        #Ne tient pas pas compte des frais de garde et des dépenses de préposé aux soins
        amount=dep_disa=dep_disa_under_18=0

        if p.disabled:
            amount+= self.disability_cred_amount

        #Supplément pour personne mineure
        if p.age<18:
            amount+= self.disability_cred_supp

        #Montant pour personnes handicapées transféré d'une personne à charge
        if hh.sp.index(p)==0:
            dep_disa= len([ch for ch in hh.dep if ch.disabled])
            if dep_disa>0:
                amount+= dep_disa*self.disability_cred_amount

            dep_disa_under_18= len([ch for ch in hh.dep if ch.disabled and ch.age<18])
            if dep_disa_under_18>0:
                amount+= dep_disa_under_18*self.disability_cred_supp

        return amount

class form_2020(form_2019):
    """
    Formulaire d'impôt de 2020.

    """
    def __init__(self):
        add_params_as_attr(self,module_dir+'/federal/params/federal_2020.csv')
        add_params_as_attr(self, module_dir + '/federal/params/fed_witb_qc_2020.csv')
        add_schedule_as_attr(self, module_dir + '/federal/params/schedule_2020.csv')
        self.witb_params = {}
        for prov in ['on', 'qc']:
            self.witb_params[prov] = get_params(
                module_dir + f'/federal/params/fed_witb_{prov}_2020.csv')


        self.ccb_young += self.ccb_covid_supp
        self.ccb_old += self.ccb_covid_supp

        self.gst_cred_base *= 2
        self.gst_cred_other *= 2
        # note: the measures to increase ccb and gst_credit are based on fiscal year 2019 in reality
        #       but on fiscal year 2020 in our simulator; the difference is small (<50$ in worst case)

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
            Montant personnel de base.
        """
        br_poor, br_rich = self.l_brackets[-2:]

        if p.fed_return['net_income'] <= br_poor:
            basic_amount = self.basic_amount_poor
        elif p.fed_return['net_income'] >= br_rich:
            basic_amount = self.basic_amount_rich
        else:
            slope = (self.basic_amount_rich - self.basic_amount_poor) / (br_rich - br_poor)
            basic_amount = self.basic_amount_poor + (p.fed_return['net_income'] - br_poor) * slope

        return basic_amount

    def calc_net_income(self, p):
        """
        Fonction qui calcule le revenu net au sens de l'impôt.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.fed_return['net_income'] =  max(0, p.fed_return['gross_income']
                                          - p.fed_return['deductions_gross_inc'])
        self.repayments_ei(p)

    def repayments_ei(self, p):
        """
        Fonction qui calcule le montant du remboursement de prestations d'assurance-emploi et qui ajuste le montant des prestations, le revenu net et le revenu brut.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant du remboursement.
        """
        excess_net_inc = max(0, p.fed_return['net_income'] - self.ei_max_net_inc)
        if excess_net_inc > 0:
            repayment = self.ei_rate_repay * min(p.inc_ei, excess_net_inc)
            p.inc_ei -= repayment
            p.fed_return['net_income'] -= repayment
            p.fed_return['gross_income'] -= repayment

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
        p.fed_cdsb = self.get_cdsb(p, hh)
        p.fed_cdsg = self.get_cdsg(p, hh) 
        self.oas_gis_covid_bonus(p)

        p.fed_return['refund_credits'] = (
            p.fed_abatment_qc + p.fed_ccb + p.fed_witb + p.fed_witbds
            + p.fed_med_exp + p.fed_gst_hst_credit)
        
        p.fed_return['rdsp_benefits'] = (p.fed_cdsb + p.fed_cdsg)

    def oas_gis_covid_bonus(self, p):
        """
        Fonction qui calcule le montant supplémentaire unique de Pension de sécurité de vieillesse (PSV) et de Supplément de revenu garanti (SRG). Pour l'année 2020, le gouvernement a versé une prestation unique non imposable de 300$ aux bénéficiaires de la PSV. Les bénéficiaires du SRG ont aussi eu droit à un montant additionnel de 200$.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant du paiement unique de SV et de SRG.
        """

        if p.elig_oas!=False and p.inc_oas>0:
            p.inc_oas += self.oas_covid_bonus

            if p.inc_gis>0:
                p.inc_gis += self.gis_covid_bonus

        return


class form_2021(form_2020):
    """
    Formulaire d'impôt de 2021.
    """

    def __init__(self):
        add_params_as_attr(self, module_dir + "/federal/params/federal_2021.csv")
        add_params_as_attr(self, module_dir + "/federal/params/fed_witb_qc_2021.csv")
        add_schedule_as_attr(self, module_dir + "/federal/params/schedule_2021.csv")
        self.witb_params = {}
        for prov in ["on", "qc"]:
            self.witb_params[prov] = get_params(
                module_dir + f"/federal/params/fed_witb_{prov}_2021.csv"
            )

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
        p.fed_cdsb = self.get_cdsb(p, hh)
        p.fed_cdsg = self.get_cdsg(p, hh)

        p.fed_return['refund_credits'] = (
            p.fed_abatment_qc + p.fed_ccb + p.fed_witb + p.fed_witbds
            + p.fed_med_exp + p.fed_gst_hst_credit)
        
        p.fed_return['rdsp_benefits'] = (p.fed_cdsb + p.fed_cdsg)

    def ccb(self, p, hh, iclaw=True):
        """
        Fonction qui calcule pour 2021 l'Allocation canadienne pour enfants (ACE) avec l’ACE supplément pour jeunes enfants (ACESJE), soit de moins de 6 ans.

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

            if adj_fam_net_inc < self.ccb_ccbycs_cutoff:
                amount_ccbycs = self.ccb_ccbycs_1 * hh.nkids_0_5
            else:
                amount_ccbycs = self.ccb_ccbycs_2 * hh.nkids_0_5

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
                return max(0, amount + amount_ccbycs - clawback) / 2  # same sex couples get 1/2 each
            else:
                return max(0, amount + amount_ccbycs - clawback)

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
        cwb_exempt = 0
        if hh.couple:
            if hh.sp[0].inc_earn < hh.sp[1].inc_earn :
                cwb_exempt = min(min(hh.sp[0].inc_earn, hh.sp[0].fed_return['net_income']), self.exempt_second_earner)
            else:
                cwb_exempt = min(min(hh.sp[1].inc_earn, hh.sp[1].fed_return['net_income']), self.exempt_second_earner)
        amount = rate * max(0, hh.fam_inc_work - base)
        adj_amount = min(witb_max, amount)
        clawback = claw_rate * max(0, hh.fam_net_inc_fed- cwb_exempt - exemption)
        return max(0, adj_amount - clawback)

class form_2022(form_2021):
    """
    Formulaire d'impôt de 2022.
    """

    def __init__(self):
        add_params_as_attr(self, module_dir + "/federal/params/federal_2022.csv")
        add_params_as_attr(self, module_dir + "/federal/params/fed_witb_qc_2022.csv")
        add_schedule_as_attr(self, module_dir + "/federal/params/schedule_2022.csv")
        self.witb_params = {}
        for prov in ["on", "qc"]:
            self.witb_params[prov] = get_params(
                module_dir + f"/federal/params/fed_witb_{prov}_2022.csv"
            )

        self.gst_cred_base *= 1.5
        self.gst_cred_other *= 1.5

        # Pour soutenir les personnes les plus touchées par l’inflation, le gouvernement du Canada a émis un versements supplémentaire pour la TPS pour aider les particuliers et les familles. 
        # Ce versement unique double le montant du crédit pour la TPS que les particuliers et les familles admissibles pour une période de six mois.

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


class form_2023(form_2022):
    """
    Formulaire d'impôt de 2023.
    """

    def __init__(self):
        add_params_as_attr(self, module_dir + "/federal/params/federal_2023.csv")
        add_params_as_attr(self, module_dir + "/federal/params/fed_witb_qc_2023.csv")
        add_schedule_as_attr(self, module_dir + "/federal/params/schedule_2023.csv")
        self.witb_params = {}
        for prov in ["on", "qc"]:
            self.witb_params[prov] = get_params(
                module_dir + f"/federal/params/fed_witb_{prov}_2023.csv"
            )
        
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
            
        gst_amount = max(0, amount - clawback) 
            
        ## BONUS
        # Budget 2023 proposes to introduce an increase to the maximum GSTC
        # amount for January 2023 that would be known as the Grocery Rebate.

        clawback_bonus = self.gst_cred_claw_rate_rebate * max(0, hh.fam_net_inc_fed - self.gst_cred_claw_cutoff)

        amount_bonus = self.gst_base_grocery_rebate
        if hh.couple or hh.nkids_0_18 >= 1:
            amount_bonus += (self.gst_base_grocery_rebate + hh.nkids_0_18 * self.gst_other_grocery_rebate)  # single with kids works same as couple
        else:
            amount_bonus += min(self.gst_other_grocery_rebate,
                          self.gst_cred_rate_rebate * max(0, hh.fam_net_inc_fed - self.gst_cred_base_amount))

        bonus = max(0, amount_bonus - clawback_bonus)
        return gst_amount + bonus