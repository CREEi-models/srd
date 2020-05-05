import numpy as np
from srd import federal, oas, quebec, payroll, assistance

class tax:
    """
    Classe générale pour le calcul des impôts, contributions et prestations.

    Parameters
    ----------
    year: int
        année pour le calcul
    prov: str
        province (pour le moment seulement Québec, par défaut)
    ifed: boolean
        vrai si calcul de l'impôt fédéral demandé
    ioas: boolean
        vrai si calcul des prestations de PSV et SRG est demandé
    iprov: boolean
        vrai si calcul de l'impôt provincial est demandé
    ipayroll: boolean
        vrai si calcul des cotisations sociales est demandé
    """
    def __init__(self,year,prov='qc',ifed=True,ioas=True,iprov=True,ipayroll=True,iass=True):
        self.year = year
        self.ifed = ifed
        self.iprov = iprov
        self.ipayroll = ipayroll
        self.ioas = ioas
        self.iass = iass
        if ipayroll:
            self.payroll = payroll(year)
        if ifed:
            self.federal = federal.form(year)
        if iprov:
            if prov=='qc':
                self.prov = quebec.form(year)
        if ioas:
            self.oas = oas.program(year)
        if iass:
            self.ass = assistance.program(year)
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
        if self.ipayroll:
            self.compute_payroll(hh)
        if self.ifed:
            self.compute_federal(hh)
        if self.iprov:
            self.compute_prov(hh)
        if self.iass:
            self.compute_ass(hh)

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

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        self.prov.file(hh)
        return
    def compute_payroll(self,hh):
        """
        Calcul des cotisations sociales.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        self.payroll.compute(hh)
        return
    def compute_ass(self,hh):
        """
        Calcul de l'aide sociale.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        ass = self.ass.apply(hh)
        for p in hh.sp:
            p.inc_social_ass = ass / (1 + hh.couple)

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
    def disp_inc(self,hh):
        """
        Calcul du revenu disponible après impôt, cotisations (sociale et REER) et aide sociale.

        Calcul fait au niveau individuel et ensuite rattaché à la personne.

        """
        self.netinc(hh)
        for p in hh.sp:
            ninc = p.net_inc
            if self.ipayroll:
                ninc -= sum(list(p.payroll.values()))
            if self.iass:
                ninc += p.inc_social_ass
            ninc -= p.con_rrsp
            p.disp_inc = ninc
        return
