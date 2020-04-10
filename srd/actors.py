import numpy as np


# INITIALIZE INDIVIDUALS AND HOUSEHOLDS #

class Person:
    """
    Classe pour définir une personne.

    Ceci définit une personne et son profil en terme de revenus et actifs. 
    
    Parameters
    ----------
    age: int
        age de l'individu
    earn: float
        revenu de travail
    rpp: float
        revenu de RCR
    cpp: float
        revenu de RRQ
    othtax: float
        autre revenu imposable
    othntax: float
        autre revenu non-imposable 
    inc_rrsp: float
        revenu de REER (sortie)
    selfemp_earn: float
        revenu de travailleur autonome 
    con_rrsp: float
        contribution REER
    years_can: int
        nombre d'année au Canada
    disabled: boolean
        statut d'invalidité
    cqppc: float
        contribution au RRQ
    widow: boolean
        statut de veuf/veuve
    asset: float 
        valeur marchande des actifs
    dc_exp0_7: int
        nombre de dépendants âges 0 à 7 ans
    dc_exp8_16: int
        nombre de dépendants âges 8 à 16 ans
    oas_years_post: int
        n/d
    """
    def __init__(self, age=50, earn=0, rpp=0, cpp=0, othtax=0, othntax=0, 
                 inc_rrsp=0, selfemp_earn=0, con_rrsp=0, years_can=None,
                 disabled=False, cqppc = None, widow=False,
                 asset=0, dc_exp0_7=0, dc_exp8_16=0, oas_years_post = 0):
        self.age = age
        self.inc_earn = earn
        self.inc_rpp = rpp
        self.inc_cpp = cpp
        self.inc_othtax = othtax
        self.inc_othntax = othntax
        self.inc_rrsp = inc_rrsp
        self.con_rrsp = con_rrsp
        self.years_can = years_can # number of years in Canada (max = 40)
        self.inc_self_earn = selfemp_earn
        self.disabled = disabled        
        self.cqppc = cqppc
        self.widow = widow
        self.asset = asset
        self.dc_exp0_7 = dc_exp0_7
        self.dc_exp8_16 = dc_exp8_16
        self.oas_years_post = oas_years_post
        self.inc_oas = 0.0
        self.inc_gis = 0.0
        self.allow_couple = 0
        self.allow_surv = 0
        self.fed_return = None 
        self.pro_return = None
        self.payroll = None 
        self.net_inc = self.inc_tot()
        self.disp_inc = self.net_inc - self.con_rrsp
        return 
    def inc_work(self):
        """
        Fonction qui retourne le revenu de travail.

        Inclut le revenu de travailleur autonome.

        Returns
        -------

        float
            revenu de travail.
        """
        return self.inc_earn + self.inc_self_earn
    def inc_non_work(self):
        """
        Fonction qui retourne le revenu autre que travail
        
        Returns
        -------

        float
            revenu autre que travail.
        """
        return self.inc_rpp + self.inc_cpp + self.inc_othtax + self.inc_othntax + self.inc_rrsp + self.inc_oas + self.inc_gis
    def inc_tot(self):
        """
        Fonction qui retourne le revenu total.

        Returns
        -------

        float
            revenu total.
        """
        return self.inc_work() + self.inc_non_work()

class Dependent:
    """
    Classe pour définir un dépendant.

    Ceci définit un dépendant et son profil. 
    
    Parameters
    ----------
    age: int
        age de l'individu
    disa: boolean
        statut d'invalidité
    child_care: float
        montant des dépenses frais de garde
    school: float
        montant des dépenses scolarité
    home_care: float
        montant d'aide à domicile
    health_care: float
        montant de dépenses en santé admissibles
    """
    
    def __init__(self, age, disa=None, child_care=None, school=None,
                home_care=None, health_care=None):
        self.age = age
        self.disa = disa
        self.child_care = child_care
        self.school = school
        self.home_care = home_care
        self.health_care = health_care


class Hhold:
    """
    Classe pour définir un ménage.

    Ceci définit un ménage et son profil. 
    
    Parameters
    ----------
    first: Person
        instance Person du premier membre du couple
    second: Person
        instance Person du 2e membre (si 2e membre)
    prov: str
        province (qc = quebec)
    """
    def __init__(self, first, second=None, prov='qc'):
        self.sp = [first]
        self.couple = bool(second)
        if self.couple:
            self.sp.append(second)
        self.prov = prov
        self.dep = []
        self.count()
    def fam_inc_work(self):
        """
        Fonction qui calcule le revenu familial de travail.
        
        Returns
        -------
        float
            Revenu familial de travail
        """
        return sum([p.inc_work() for p in self.sp])
    def fam_inc_non_work(self):
        """
        Fonction qui calcule le revenu familial autre que travail.
        
        Returns
        -------
        float
            Revenu familial autre que travail
        """
        return sum([p.inc_non_work() for p in self.sp])
    def fam_tot_inc(self):
        """
        Fonction qui calcule le revenu familial total.
        
        Returns
        -------
        float
            Revenu familial total
        """
        return sum([p.inc_tot() for p in self.sp])
    def fam_net_inc(self):
        """
        Fonction qui calcule le revenu familial après impôt.
        
        Returns
        -------
        float
            Revenu familial total après impôt
        """
        return sum([p.net_inc for p in self.sp])
    def fam_disp_inc(self):
        """
        Fonction qui calcule le revenu familial disponible.

        Il s'agit du revenu après impôt, cotisations sociales et REER.
        
        Returns
        -------
        float
            Revenu familial disponible après impôt et cotisations.
        """
        return sum([p.disp_inc for p in self.sp])

    def add_dependent(self, dependent): # necessary?
        """
        Fonction pour ajouter un dépendant.

        Parameters
        ----------
        dependent: Dependent
            instance de la classe Dependent
        """
        self.dep.append(dependent)     

    def count(self): # do we need this?
        """
        Fonction pour calculer la composition du ménage.
        """
        self.ndep = len(self.dep)
        self.nkids = len([s for s in self.dep if s.age <= 30])
        self.nold = len([s for s in self.dep if s.age >= 65])
        self.nhh = 1 + self.couple + len(self.dep)
        self.hh_size = 1 + self.couple + self.nkids


    def split_pension_income(self):
        # use this function after inc_oas has been computed?
        # age eligibility? type of pension eligible?
        # see documentation Gaelle
        """
        Fonction pour faire le fractionnement des revenus de retraite.
        """
        # compute net transfers from 0 to 1
        income = []
        for p in self.sp:
            income.append(p.inc_oas + p.inc_cpp + p.inc_rpp + p.inc_othtax)
        transfer = np.clip((income[0] - income[1]) / 2,
            -common.max_split * (self.sp[1].inc_rpp + self.sp[1].inc_othtax),
            common.max_split * (self.sp[0].inc_rpp + self.sp[0].inc_othtax))

        who = 0 if transfer > 0 else 1
        inc_rpp_othtax = self.sp[who].inc_rpp + self.sp[who].inc_othtax + 1e-12
        rpp_transfer = self.sp[who].inc_rpp / inc_rpp_othtax * transfer
        othtax_transfer = self.sp[who].inc_othtax / inc_rpp_othtax * transfer
        for who, sp in enumerate(self.sp):
            if who == 0:
                rpp = sp.rpp - rpp_transfer
                othtax = sp.othtax - othtax_transfer
            else:
                rpp = sp.rpp + rpp_transfer
                othtax = sp.othtax + othtax_transfer
