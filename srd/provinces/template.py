"""
Gabarit simplifié pour l'impôt provincial (version barebones).

Ce module contient uniquement les paliers d'imposition et le montant personnel de base.
Il peut être utilisé pour les provinces qui ne sont pas entièrement modélisées (QC, ON).
"""
import os
import numpy as np

module_dir = os.path.dirname(os.path.dirname(__file__))


def create_return():
    """Crée un dictionnaire vide pour le résultat fiscal."""
    lines = ['gross_income', 'deductions_gross_inc', 'net_income',
             'deductions_net_inc', 'taxable_income', 'gross_tax_liability',
             'non_refund_credits', 'refund_credits', 'net_tax_liability']
    return dict(zip(lines, np.zeros(len(lines))))


class template:
    """
    Gabarit simplifié pour l'impôt provincial.
    
    Contient uniquement:
    - Paliers d'imposition (tax brackets)
    - Montant personnel de base (basic personal amount)
    
    Les provinces utilisant ce gabarit copient le revenu imposable du fédéral.
    """

    def file(self, hh):
        """
        Fonction qui permet de calculer l'impôt provincial simplifié.

        Cette fonction calcule l'impôt brut selon les paliers d'imposition
        et applique le crédit pour montant personnel de base.

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
            p.prov_return['net_tax_liability'] = max(
                0,
                p.prov_return['gross_tax_liability'] - p.prov_return['non_refund_credits']
            )

    def copy_fed_return(self, p):
        """
        Copie le revenu brut, les déductions et les revenus net/imposable du fédéral.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        for line in ['gross_income', 'deductions_gross_inc', 'net_income',
                     'deductions_net_inc', 'taxable_income']:
            p.prov_return[line] = p.fed_return[line]
        p.prov_return['taxable_income'] = p.fed_return['gross_income'] - p.fed_return['deductions_net_inc'] # On retire OAS mais pas les éléments du gross income qui varie selon la province. 



    def calc_tax(self, p):
        """
        Calcule l'impôt brut selon les paliers d'imposition.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        """
        ind = np.searchsorted(self.l_brackets, p.prov_return['taxable_income'], 'right') - 1
        p.prov_return['gross_tax_liability'] = (
            self.l_constant[ind] +
            self.l_rates[ind] * (p.prov_return['taxable_income'] - self.l_brackets[ind])
        )

    def calc_non_refundable_tax_credits(self, p, hh):
        """
        Calcule les crédits d'impôt non-remboursables (montant personnel de base seulement).

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        # Crédit pour montant personnel de base
        p.prov_return['non_refund_credits'] = self.nrtc_rate * self.nrtc_base
