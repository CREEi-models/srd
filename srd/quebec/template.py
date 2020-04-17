from srd import add_params_as_attr, add_schedule_as_attr
import os
import numpy as np
module_dir = os.path.dirname(os.path.dirname(__file__))

def create_return():
        lines = ['gross_income','deductions','net_income','taxable_income','gross_tax_liability',
        'non_refund_credits','refund_credits','net_tax_liability']
        return dict(zip(lines,np.zeros(len(lines))))

class template:
    """
    Gabarit pour impôt provincial Québec.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/quebec/params/measures_2016.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/quebec/params/schedule_2016.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/quebec/params/cchcare_2016.csv',delimiter=';')
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
            self.calc_non_refundable_tax_credits(p,hh)
            p.prov_return['net_tax_liability'] = max(0.0, p.prov_return['gross_tax_liability'] 
                - p.prov_return['non_refund_credits'])
            self.calc_refundable_tax_credits(p,hh)
            p.prov_return['net_tax_liability'] -= p.prov_return['refund_credits']
        return
    def calc_gross_income(self,p):
        """
        Fonction qui calcule le revenu total (brutte).

        Cette fonction correspond au revenu total d'une personne au fin de l'impôt. 

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.prov_return['gross_income'] = p.inc_earn + p.inc_self_earn + p.inc_oas + p.inc_gis + p.inc_cpp + p.inc_rpp + p.inc_othtax + p.inc_rrsp 
        return        
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
    def calc_taxable_income(self,p):
        """
        Fonction qui calcule le revenu imposable au sens de l'impôt.

        Cette fonction correspond au revenu imposable d'une personne au fin de l'impôt. On y soustrait une portion des gains en capitaux. 

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.prov_return['taxable_income'] = p.prov_return['net_income']
        return
    def calc_deductions(self,p):
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
        return
    def work_deduc(self,p):
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
        cred_amount = self.get_age_cred(p) + self.get_single_cred(p,hh) + self.get_pension_cred(p)
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
        amount = self.nrtc_age_max if p.age >= self.nrtc_age else 0.0
        return amount
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
        if hh.couple!=True:
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
        p.prov_return['refund_credits'] = self.witb(p,hh)
    def witb(self,p,hh):
        """
        Prime au travail.
       
        Ce crédit n'est pas encore implémenté. 
        
        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        Returns
        -------
        float
            Montant de la Prime au travail
        """
        return 0.0
    def ccap(self,p,hh):
        """
        Allocation familiale.
       
        Ce crédit remboursable n'est pas encore implémenté. 
        
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
        return 0.0
    def cchcare(self,p,hh):
        """
        Crédit pour frais de garde.
       
        Ce crédit remboursable n'est pas encore implémenté. 
        
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
        """        
        return 0.0
 
     