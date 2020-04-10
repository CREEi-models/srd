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
    Gabarit pour impôt fédéral.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/federal/params/federal_2016.csv',delimiter=';')
        add_schedule_as_attr(self, module_dir + '/federal/params/schedule_2016.csv')
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
            p.fed_return = create_return()
            self.calc_gross_income(p)
            self.calc_deductions(p)
            self.calc_net_income(p)
            self.calc_taxable_income(p)
            self.calc_tax(p)
            self.calc_non_refundable_tax_credits(p)
            p.fed_return['net_tax_liability'] = max(0.0, p.fed_return['gross_tax_liability'] 
                - p.fed_return['non_refund_credits'])
            self.calc_refundable_tax_credits(p,hh)
            p.fed_return['net_tax_liability'] -= p.fed_return['refund_credits']
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
        p.fed_return['gross_income'] = p.inc_earn + p.inc_self_earn + p.inc_oas + p.inc_gis + p.inc_cpp + p.inc_rpp + p.inc_othtax + p.inc_rrsp 
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
        p.fed_return['net_income'] =  p.fed_return['gross_income'] - p.fed_return['deductions']
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
        p.fed_return['taxable_income'] = p.fed_return['net_income']
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
        p.fed_return['deductions'] = p.con_rrsp
        p.fed_return['deductions'] += p.inc_gis
        return
    def calc_tax(self, p):
        """
        Fonction qui calcule l'impôt à payer selon la table d'impôt.

        Cette fonction utilise la table d'impôt de l'année cours. 
        
        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        ind = np.searchsorted(self.l_brackets, p.fed_return['taxable_income'], 'right') - 1
        p.fed_return['gross_tax_liability'] = self.l_constant[ind] + \
            self.l_rates[ind] * (p.fed_return['taxable_income'] - self.l_brackets[ind])
    def calc_non_refundable_tax_credits(self, p):
        """
        Fonction qui calcule les crédits d'impôt non-remboursable.

        Cette fonction fait la somme de tous les crédits d'impôt modélisés. 
        
        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        p.fed_return['non_refund_credits'] = self.rate_non_ref_tax_cred * (self.basic_amount 
                            + self.get_age_cred(p) + self.get_pension_cred(p) 
                            + self.get_disabled_cred(p))
    def get_age_cred(self, p):
        """
        Crédit d'impôt selon l'âge.

        Ce crédit est non-remboursable. 
        
        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        amount = self.age_cred_amount if p.age >= self.min_age_cred else 0.0
        clawback = self.age_cred_claw_rate * max(0, p.fed_return['net_income'] - self.age_cred_exemption)
        return max(0, amount - clawback)
    def get_pension_cred(self, p):
        """
        Crédit d'impôt pour revenu de retraite.

        Ce crédit est non-remboursable. 
        
        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        return min(p.inc_rpp, self.pension_cred_amount)
    def get_disabled_cred(self, p):
        """
        Crédit d'impôt pour invalidité.

        Ce crédit est non-remboursable. 
        
        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        amount = self.disability_cred_amount if p.disabled else 0
        return amount
        # this is only line 316; how to take line 318 into account?
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
        p.fed_return['refund_credits'] = 0
        p.fed_return['refund_credits'] += self.abatment(p,hh)
        p.fed_return['refund_credits'] += self.uccb(p,hh)
        p.fed_return['refund_credits'] += self.cctb(p,hh)
        p.fed_return['refund_credits'] += self.ncbs(p,hh)
        p.fed_return['refund_credits'] += self.ccb(p,hh)
        p.fed_return['refund_credits'] += self.witb(p,hh)
        p.fed_return['refund_credits'] += self.witbds(p,hh)
        return
    def abatment(self, p, hh):
        """
        Abatement du Québec à l'impôt fédéral.
       
        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        Returns
        -------
        float
            Montant de l'abatement
        """
        if hh.prov == 'qc':
            return p.fed_return['net_tax_liability']*self.rate_abatment_qc
        else :
            return 0.0    
    def uccb(self,p,hh):
        """
        Montant de la PUGE (UCCB).
       
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
            Montant de la PUGE (UCCB)
        """
        return 0.0
    def cctb(self,p,hh):
        """
        Prestation canadienne pour enfants (CCTB).
       
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
            Montant de la PFCE (CCTB)
        """
        return 0.0
    def ncbs(self,p,hh):
        """
        Supplément à la prestation nationale pour enfants (NCBS).
       
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
            Montant de la SPNE (NCBS)
        """
        return 0.0
    def ccb(self,p,hh):
        """
        Allocation canadienne pour enfants (CCB).
       
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
            Montant de la ACE (CCB)
        """        
        return 0.0
    def witb(self,p,hh):
        """
        Prestation fiscale pour le revenu de travail (WITB).
       
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
            Montant de la PFRT (WITB)
        """
        return 0.0
    def witbds(self,p,hh):
        """
        Supplément pour invalidité à Prestation fiscale pour le revenu de travail (WITBDS).
       
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
            Montant de la SIPFRT (WITBDS)
        """
        return 0.0
 
     