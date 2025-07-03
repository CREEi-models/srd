from copy import deepcopy
# INITIALIZE INDIVIDUALS AND HOUSEHOLDS #


class Person:
    """
    Classe pour définir une personne.

    Ceci définit une personne et son profil en termes de revenus et d'actifs.

    Parameters
    ----------
    age: int
        âge de l'individu
    male: bool
        prend la valeur True si l'individu est un homme
    earn: float
        revenu de travail
    rpp: float
        revenu de régime complémentaire de retraite (RCR)
    cpp: float
        revenu du Régime de rentes du Québec (RRQ) ou du Régime de pensions du Canada (RPC)
    net_cap_gains: float
        gains (ou pertes si valeur négative) nets en capital réalisés dans l'année
    prev_cap_losses: float
        pertes en capital nettes d'autres années (avec facteur d'inclusion partielle déjà appliqué)
    cap_gains_exempt: float
        exonération des gains en capital admissibles demandée (sur gains en capital nets); soumis à un plafond à vie
    othtax: float
        autre revenu imposable
    othntax: float
        autre revenu non-imposable
    inc_rrsp: float
        revenu de REER (retrait de fonds)
    inc_rdsp: float
        revenus de REEI (retrait de fonds) provenant des bons, subventions ou revenus de placements
    inc_bip: float
        montant du programme de revenu de base
    inc_ss: float
        montant du programme de solidarité sociale
    self_earn: float
        revenu de travail autonome
    div_elig: float
        montant réel des dividendes déterminés (canadiens)
    div_other_can: float
        montant réel des dividendes ordinaires (canadiens)
    cdsg: float
        montant cumulatif de la subvention canadienne pour invalidité (SCEI) reçue
    cdsb: 
        montant cumulatif du bon canadien pour invalidité reçu
    con_rrsp: float
        cotisation REER
    con_rdsp: float
        cotisation REEI.
    con_non_rrsp: float
        cotisation autre que REER ou REEI (p.ex. à un CELI ou à des comptes non enregistrés)
    con_rpp: float
        cotisation à un régime de pension agréé (RPA)
    union_dues: float
        cotisations syndicales, professionnelles ou autres
    donation: float
        don de bienfaisance et autres dons
    gift: float
        dons de biens culturels et écosensibles
    years_can: int
        nombre d'années vécues au Canada depuis l’âge de 18 ans lorsque la Pension de la sécurité de la vieillesse (PSV) est demandée
    disabled: boolean
        statut d'invalidité selon les règles fiscales (le même statut est utilisé pour l'ensemble des mesures fiscales modélisées)
    widow: boolean
        statut de veuf/veuve selon le Programme de la sécurité de la vieillesse
    med_exp: float
        montant des dépenses en santé admissibles selon les règles fiscales (le même montant est utilisé pour tous les paliers de gouvernement)
    ndays_chcare_k1: float
        nombre de jours de garde du premier enfant
    ndays_chcare_k2: float
        nombre de jours de garde du second enfant
    asset: float
        valeur marchande des actifs (avoirs liquides) comptabilisés aux fins d'admissibilité à l'aide sociale (vérifier la définition selon la province)
    oas_years_post: int
        nombre d'années de report pour la PSV (après 65 ans)
    months_cerb_cesb: int
        nombre de mois pour lesquels la PCU ou la PCUE est demandée
    student: boolean
        statut d'étudiant aux fins d'admissibilité à la PCUE
    essential_worker: boolean
        True si travailleur essentiel (au Québec seulement)
    hours_month: float
        nombre d'heures travaillées par mois
    prev_inc_work: float
        revenu du travail de l'année précédente
    dep_senior: boolean
        True si la personne aînée n'est pas autonome aux du crédit d'impôt pour maintien à domicile des aînés
    home_support_cost: float
        dépenses engagées pour des services de maintien à domicile rendus ou à être rendus à partir du jour du 70e anniversaire
    home_access_cost: float
        dépenses engagées pour améliorer l'accessibilité et la fonctionnalité du logement (si personne handicapée ou agée)
    months_ei: int
        nombre de mois pour lesquels l'Assurance-Emploi sont demandée
    months_crb: int
        nombre de mois pour lesquels la PCRE est demandée
    pub_drug_insurance: boolean
        True si la personne doit cotiser à l'Assurance médicaments du Québec (pas d'assurance médicaments privée)
    tax_shield: boolean
        True si la personne demande le crédit d'impôt bouclier ficscal au Québec
    rent: float
        dépense de logement
    prop_tax: float
        dépense sur taxe foncière
    long_term_ss : boolean
        True si la personne a reçu des prestations de solidarité sociale durant au moins 66 mois parmi les 72 derniers mois
    """
    def __init__(self, age=50, male=True, earn=0, rpp=0, cpp=0,
                 net_cap_gains=0, prev_cap_losses=0, cap_gains_exempt=0,
                 othtax=0, othntax=0, inc_rrsp=0,inc_rdsp=0, self_earn=0, div_elig=0,
                 div_other_can=0,cdsg =0,cdsb=0, con_rrsp=0,con_rdsp=0, con_non_rrsp=0, con_rpp=0,
                 union_dues=0, donation=0, gift=0, years_can=None,
                 disabled=False, widow=False, med_exp=0, ndays_chcare_k1=0,
                 ndays_chcare_k2=0, asset=0, oas_years_post=0,
                 months_cerb_cesb=0, student=False, essential_worker=False,
                 emp_temp_constraints=False, hours_month=None, prev_inc_work=None,
                 dep_senior=False, home_support_cost=0,home_access_cost=0,months_ei=0, 
                 months_crb =0, pub_drug_insurance=False, tax_shield=False,prop_tax=0,
                 long_term_ss=False):
        self.age = age
        self.male = male
        self.attach_inc_work_month(earn, self_earn)
        self.attach_prev_work_inc(prev_inc_work)
        self.inc_rpp = rpp
        self.inc_cpp = cpp
        self.net_cap_gains = net_cap_gains
        self.prev_cap_losses = prev_cap_losses
        self.cap_gains_exempt = cap_gains_exempt  # for example for small businesses
        self.inc_othtax = othtax
        self.inc_othntax = othntax
        self.div_elig = div_elig
        self.div_other_can = div_other_can
        self.inc_rrsp = inc_rrsp
        self.inc_rdsp = inc_rdsp
        self.cdsg = cdsg
        self.cdsb = cdsb
        self.con_rrsp = con_rrsp
        self.con_rdsp = con_rdsp
        self.con_non_rrsp = con_non_rrsp
        self.con_rpp = con_rpp
        self.union_dues = union_dues
        self.donation = donation
        self.gift = gift
        self.years_can = max(0,age-18) if years_can is None else years_can  # number of years in Canada (max = 40)
        self.disabled = disabled
        self.widow = widow
        self.med_exp = med_exp
        self.ndays_chcare_k1 = ndays_chcare_k1  # should be the kid with the most days,
        self.ndays_chcare_k2 = ndays_chcare_k2  # second kid with most days, in same order for both spouses
        self.asset = asset
        self.months_crb = months_crb
        self.months_ei = months_ei
        self.oas_years_post = oas_years_post
        self.compute_months_cerb_cesb(months_cerb_cesb, student)
        self.pub_drug_insurance = pub_drug_insurance
        self.tax_shield = tax_shield
        self.student = student
        self.essential_worker = essential_worker
        self.emp_temp_constraints = emp_temp_constraints 
        self.hours_month = hours_month  # could enter list of hours for ei
        self.dep_senior = dep_senior
        self.home_support_cost = home_support_cost
        self.home_access_cost = home_access_cost
        self.prop_tax = prop_tax
        self.long_term_ss = long_term_ss
        self.pension_split = 0
        self.pension_split_qc = 0
        self.pension_deduction = 0
        self.pension_deduction_qc = 0
        self.inc_oas = 0
        self.inc_gis = 0
        self.inc_ei = 0
        self.allow_couple = 0
        self.allow_surv = 0
        self.allow_housing = 0
        self.inc_cerb = 0
        self.inc_cesb = 0
        self.inc_crb = 0
        self.inc_iprew = 0
        self.inc_sa = None #{'amount':0, 'basic amount': 0, 'temporary amount':0, 'kids_adjustments':0, 'clawback':0}
        self.inc_ss = None #{'amount':0, 'basic amount':0, 'severe constraints': 0, 'kids adjustments':0, 'clawback':0}
        self.inc_bip = None #{'amount':0, 'basic amount':0, 'single adjustment':0, 'dep adjustment':0, 'reduce': 0}
        self.covid = None
        self.after_tax_inc = None
        self.disp_inc = None
        self.fed_return = None
        self.prov_return = None
        self.payroll = None
        self.prov_contrib = None
        

    def attach_prev_work_inc(self, prev_work_inc):
        """
        Fonction qui ajoute le revenu du travail de l'an passé s'il est disponible,
        ou l'approxime avec le revenu du travail de l'année courante sinon.

        Parameters
        ----------
        prev_work_inc: float
            revenu de travail de l'année précédente
        """
        if prev_work_inc is None:
            self.prev_inc_work = self.inc_earn + self.inc_self_earn
        else:
            self.prev_inc_work = prev_work_inc

    def attach_inc_work_month(self, earn, self_earn):
        """
        Fonction qui convertit le revenu de travail annuel en revenu mensuel et vice versa.

        On entre le revenu de travail annuel ou mensuel (liste avec 12 éléments)
        et le revenu de travail annuel et mensuel deviennent des attributs de la personne.

        Parameters
        ----------
        earn: float or list
            revenu de travail salarié
        self_earn: float or list
            revenu de travail autonome
        """
        if isinstance(earn, list):
            earn_month = earn
            self.inc_earn = sum(earn)
        else:
            earn_month = [earn / 12] * 12
            self.inc_earn = earn

        if isinstance(self_earn, list):
            self_earn_month = self_earn
            self.inc_self_earn = sum(self_earn)
        else:
            self_earn_month = [self_earn / 12] * 12
            self.inc_self_earn = self_earn

        self.inc_work_month = [x + y for x, y in zip(earn_month, self_earn_month)]

    @property
    def inc_work(self):
        """
        Fonction qui retourne le revenu de travail.

        Inclut le revenu de travail autonome.

        Returns
        -------
        float
            Revenu de travail.
        """
        return self.inc_earn + self.inc_self_earn
            

    @property
    def inc_non_work(self):
        """
        Fonction qui retourne le total des revenus autres que les revenus du travail.

        Returns
        -------
        float
            Revenu provenant de sources autres que le travail.
        """
        return (self.inc_rpp + self.inc_cpp + self.inc_othtax
                + self.inc_othntax + self.inc_rrsp + self.inc_oas
                + self.inc_gis + self.allow_couple + self.allow_surv
                + self.inc_ei + self.net_cap_gains
                + self.div_elig + self.div_other_can + self.inc_cerb + self.inc_cesb + self.inc_iprew + self.inc_crb)

    @property
    def inc_tot(self):
        """
        Fonction qui retourne le revenu total.

        Ce revenu total contient les montants réels des dividendes de sociétés
        canadiennes (et non les montants imposables).

        Returns
        -------
        float
            Revenu total.
        """
        return self.inc_work + self.inc_non_work

    def compute_months_cerb_cesb(self, months_cerb_cesb, student):
        """
        Fonction qui établit le nombre de mois de PCU ou de PCUE selon le nombre de mois
        pour lesquels la personne demande la prestation et selon son statut d'étudiant.

        Parameters
        ----------
        months_cerb_cesb: int
            nombre de mois pour lesquels la prestation est demandée
        student: boolean
            True si la personne est étudiante (ou l'était en décembre 2019)
        """
        self.months_cesb = self.months_cerb = 0
        if months_cerb_cesb > 0:
            if student:
                self.months_cesb = months_cerb_cesb
            else:
                self.months_cerb = months_cerb_cesb  # assuming that last year's work income > 5000

    def copy(self):
        """
        Fonction qui produit une copie des attributs de la personne.
        """
        self.temp = deepcopy(self.__dict__)

    def reset(self):
        """
        Fonction qui utilise la copie des attributs de la personne
        pour réinitialiser l'instance de la personne.
        """
        l_attr = [k for k in self.__dict__ if k != 'temp']
        for k in l_attr:
            delattr(self, k)
        for attr, val in self.temp.items():
            setattr(self, attr, val)


class Dependent:
    """
    Classe pour définir un dépendant.

    Ceci définit un dépendant et son profil.

    Parameters
    ----------
    age: int
        âge de l'individu
    disabled: boolean
        statut d'invalidité
    child_care: float
        dépenses réelles de frais de garde
    educ_level: float
        niveau de scolarité de l'établissement d'enseignement fréquenté
    educ_exp: float
        frais de scolarité
    home_care: float
        dépenses engagées pour des services de maintien à domicile rendus ou à être rendus à partir du jour du 70e anniversaire
    med_exp: float
        dépenses en santé admissibles
    alimony: float
        pension alimentaire mensuelle recue pour chaque enfant (si le dépendant est un enfant)
    """

    def __init__(self, age, disabled=False, child_care=0, educ_exp=None, educ_level=None,
                 home_care=None, med_exp=0, alimony=0):
        self.age = age
        self.disabled = disabled
        self.child_care = child_care
        self.educ_exp = educ_exp
        self.educ_level = educ_level
        self.home_care = home_care
        self.med_exp = med_exp
        self.alimony = alimony


class Hhold:
    """
    Classe pour définir un ménage.

    Ceci définit un ménage et son profil.

    Parameters
    ----------
    first: Person
        instance Person du 1er membre du couple
    second: Person
        instance Person du 2e membre du couple, s'il y a lieu
    prov: str
        province (qc = Québec)
    n_adults_in_hh: int
        nombre d'adultes (18 ans et plus) dans le ménage
    """
    def __init__(self, first, second=None, prov='qc', n_adults_in_hh=None, prev_fam_net_inc_prov=None,rent=0):
        self.sp = [first]
        self.couple = bool(second)
        if self.couple:
            self.sp.append(second)
        self.prev_fam_net_inc_prov = prev_fam_net_inc_prov
        self.prov = prov
        self.dep = []
        self.nkids_0_6 = 0
        self.nkids_7_16 = 0
        self.nkids_0_17 = 0
        self.nkids_0_18 = 0
        self.n_adults_in_hh = self.adjust_n_adults(n_adults_in_hh)
        self.compute_max_split()
        self.assess_elig_split()
        self.rent = rent

    def adjust_n_adults(self, n_adults_in_hh):
        """
        Fonction qui calcule le nombre d'adultes dans le ménage si celui-ci
        n'est pas fourni.

        Parameters
        ----------
        n_adults_in_hh: float
            nombre d'adultes dans le ménage s'il est fourni, None sinon

        Returns
        -------
        float
            Nombre d'adultes dans le ménage.
        """
        if n_adults_in_hh:
            return n_adults_in_hh
        else:
            adult_deps = len([s for s in self.dep if s.age > 18])
            return 2 + adult_deps if self.couple else 1 + adult_deps

    @property
    def fam_inc_work(self):
        """
        Fonction qui calcule le revenu de travail du ménage.

        Returns
        -------
        float
            Revenu de travail du ménage.
        """
        return sum([p.inc_work for p in self.sp])

    def fam_inc_non_work(self):
        """
        Fonction qui calcule le revenu familial de sources autres que le travail.

        Returns
        -------
        float
            Revenu familial de sources autres que le travail.
        """
        return sum([p.inc_non_work for p in self.sp])

    @property
    def fam_net_inc_prov(self):
        """
        Fonction qui calcule le revenu familial net pour l'impôt et les programmes provinciaux.

        Returns
        -------
        float
            Revenu familial net provincial.
        """
        return sum([s.prov_return['net_income'] for s in self.sp])

    @property
    def fam_net_inc_fed(self):
        """
        Fonction qui calcule le revenu familial net pour l'impôt et les programmes fédéraux.

        Returns
        -------
        float
            Revenu familial net fédéral.
        """
        return sum([s.fed_return['net_income'] for s in self.sp])

    @property
    def fam_inc_tot(self):
        """
        Fonction qui calcule le revenu familial total.

        Returns
        -------
        float
            Revenu familial total.
        """
        return sum([p.inc_tot for p in self.sp])

    @property
    def fam_after_tax_inc(self):
        """
        Fonction qui calcule le revenu familial après impôts.

        Returns
        -------
        float
            Revenu familial après impôts.
        """
        try:
            return sum([p.after_tax_inc for p in self.sp])
        except TypeError as e:
            print(f'{e}: need to run household through simulator to obtain fam_after_tax_inc')

    @property
    def fam_disp_inc(self):
        """
        Fonction qui additionne les revenus disponibles du conjoint pour obtenir le revenu disponible familial.
        
        Il s'agit du revenu disponible après impôts, cotisations sociales, épargne (positive ou négative) et prestations.

        Returns
        -------
        float
            Revenu familial disponible, après impôts et cotisations.
        """
        try:
            return sum([p.disp_inc for p in self.sp])
        except TypeError as e:
            print(f'{e}: need to run household through simulator to obtain fam_disp_inc')

    @property
    def child_care_exp(self):
        """
        Fonction qui calcule la dépense en frais de garde pour le ménage.

        Returns
        -------
        float
            Montant total des dépenses de frais de garde.
        """
        return sum([d.child_care for d in self.dep])

    def add_dependent(self, *dependents):  # necessary?
        """
        Fonction pour ajouter un ou plusieurs dépendant(s).

        Parameters
        ----------
        dependent: Dependent
            instance de la classe Dependent ou liste d'instances de la classe Dependent
        """
        for s in dependents:
            self.dep.append(s)
        self.count()

    def count(self):
        """
        Fonction pour calculer le nombre d'enfants dans différentes catégories d'âge.
        """
        self.nkids_0_5 = len([s for s in self.dep if s.age <= 5])
        self.nkids_6_17 = len([s for s in self.dep if 5 < s.age <= 17])
        self.nkids_0_17 = self.nkids_0_5 + self.nkids_6_17
        self.nkids_0_6 = len([s for s in self.dep if s.age <= 6])
        self.nkids_7_16 = len([s for s in self.dep if 6 < s.age <= 16])
        self.nkids_0_18 = len([s for s in self.dep if s.age <= 18])

    def compute_max_split(self):
        """
        Fonction qui calcule le montant maximal de revenu de pension pouvant être fractionné, et qui l'attache à chaque conjoint du ménage dans l'attribut *max_split*.
        """
        if not self.couple:
            self.sp[0].max_split = 0
        else:
            for p in self.sp:
                p.max_split = 0.5 * p.inc_rpp
                if p.age >= 65:
                    p.max_split += 0.5 * p.inc_rrsp

    def assess_elig_split(self):
        """
        Fonction qui établit si le ménage est admissible pour le fractionnement du revenu
        de pension, et qui l'attache au ménage dans l'attribut *elig_split*.
        """
        self.elig_split = len([p for p in self.sp if p.max_split > 0]) > 0

    def copy(self):
        """
        Fonction qui produit une copie des attributs du ménage
        et des personnes dans le ménage.
        """
        d_attr_not_sp = {k: v for k, v in vars(self).items() if k != 'sp'}
        for p in self.sp:
            p.copy()
        self.temp = deepcopy(d_attr_not_sp)

    def reset(self):
        """
        Fonction qui utilise la copie des attributs du ménage et des personnes
        pour réinitialiser l'instance du ménage.
        """
        for p in self.sp:
            p.reset()
        l_attr = [k for k in self.__dict__ if k not in ('sp', 'temp')]
        for k in l_attr:
            delattr(self, k)
        for attr, val in self.temp.items():
            setattr(self, attr, val)
