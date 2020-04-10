import numpy as np 
from srd import federal, oas

class tax:
    """
    Classe général pour le calcul des impôts, contributions et prestations. 

    Parameters
    ----------
    year: int 
        année pour le calcul 
    ifed: boolean
        vrai si calcul de l'impôt fédéral demandé
    ioas: boolean
        vrai si calcul des prestations de PSV et SRG est demandé
    iprov: boolean
        vrai si calcul de l'impôt provincial est demandé
    ipayroll: boolean
        vrai si calcul des cotisations sociales est demandé
    """
    def __init__(self,year,ifed=True,ioas=True,iprov=False,ipayroll=False):
        self.year = year
        self.ifed = ifed
        self.iprov = iprov
        self.ipayroll = ipayroll
        if ifed:
            self.federal = federal.form(year)
        self.ioas = ioas
        if ioas:
            self.oas = oas.program(year)
        return
    def compute(self,hh):
        """
        Calcul tous les éléments demandés.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        if self.ioas:
            self.compute_oas(hh)
        if self.ifed:
            self.compute_federal(hh)
        if self.iprov:
            self.compute_prov(hh)
        if self.ipayroll:
            self.compute_payroll(hh)
        return 
    def compute_oas(self,hh):
        """
        Calcul des prestations de PSV et SRG.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        self.oas.file(hh)
    def compute_federal(self,hh):
        """
        Calcul de l'impôt fédéral.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        self.federal.file(hh)
        return
    def compute_prov(self,hh):
        """
        Calcul de l'impôt provincial.

        N'est pas implémenté pour l'instant. 

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        return
    def compute_payroll(self,hh):
        """
        Calcul des cotisations sociales.

        N'est pas implémenté pour l'instant. 

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        return
    def netinc(self,hh):
        """
        Calcul du revenu après impôt fédéral et provincial.

        Calcul fait au niveau individuel et ensuite rattaché à la personne. Un calcul au niveau du ménage est aussi effectué.

        """
        for p in hh.sp:
            ninc = p.inc_tot() 
            if self.ifed:
                ninc -= p.fed_return['net_tax_liability']  
            if self.iprov:
                ninc -= p.prov_return['net_tax_liability']
            p.net_inc = ninc 
        return
    def dispinc(self,hh):
        """
        Calcul du revenu disponible après impôt et cotisations (sociale et REER).

        Calcul fait au niveau individuel et ensuite rattaché à la personne. Un calcul au niveau du ménage est aussi effectué.

        """
        self.netinc(hh)
        for p in hh.sp:
            ninc = p.net_inc
            if self.ipayroll:
                ninc -= p.payroll['total']
            ninc -= p.con_rrsp
            p.disp_inc = ninc       
        return
