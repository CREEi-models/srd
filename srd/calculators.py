import numpy as np
from srd import federal, oas, quebec, ontario, payroll, assistance, covid, ei, Person, Hhold, Dependent
from itertools import product
import pandas as pd
from multiprocessing import cpu_count, Pool


class tax:
    """
    Classe générale pour le calcul des impôts, cotisations et prestations.

    Parameters
    ----------
    year: int
        année pour le calcul
    ifed: boolean
        vrai si le calcul de l'impôt fédéral est demandé
    ioas: boolean
        vrai si le calcul des prestations de PSV, SRG, Allocation et Allocation au survivant est demandé
    iprov: boolean
        vrai si le calcul de l'impôt provincial est demandé
    ipayroll: boolean
        vrai si le calcul des cotisations sociales est demandé
    iass: boolean
        vrai si le calcul des prestations d'aide sociale est demandé
    policy: policy
        instance de la classe *policy* du module *covid*
    """
    def __init__(self, year, ifed=True, ioas=True, iprov=True,
                 ipayroll=True, iass=True, policy=covid.policy()):
        self.year = year
        self.ifed = ifed
        self.iprov = iprov
        self.ipayroll = ipayroll
        self.ioas = ioas
        self.iass = iass
        self.policy = policy

        if ipayroll:
            self.payroll = payroll(year)
        if policy.some_measures and year == 2020:
            self.covid = covid.programs(policy)
        if policy.iei and year == 2020:
            self.ei = ei.program(year)
        if ifed:
            self.federal = federal.form(year, policy)
        if iprov:
            self.prov = {'qc': quebec.form(year),
                         'on': ontario.form(year)}
        if ioas:
            self.oas = oas.program(year, self.federal)
        if iass:
            self.ass = assistance.program(year)

    def compute(self, hh, n_points=1):
        """
        Cette fonction transfère des revenus de pension pour les couples admissibles
        et retient la solution qui maximise le revenu disponible familial.
        Si n_points=0, pas de fractionnement des revenus de pension. Par défaut
        (n_points=1), les revenus bruts sont égalisés dans la mesure des transferts
        possibles. Pour n>1, une simulation est faite pour chaque point de la grille.
        À noter que lorsque n augmente, les solutions avec n inférieur (notamment n=0)
        sont aussi considérées.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        n_points: int
            nombre de points utilisés pour optimiser le fractionnement de revenus de
            pension
        """
        if not hh.elig_split or (n_points == 0):
            self.compute_all(hh)
            return hh

        hh.copy()
        self.compute_all(hh)

        if hh.elig_split and n_points > 0:
            fam_disp_inc_max, transfer_max = hh.fam_disp_inc, 0

            desired_transfer = (hh.sp[0].inc_tot - hh.sp[1].inc_tot) / 2
            transfer = np.clip(desired_transfer, - hh.sp[1].max_split,
                               hh.sp[0].max_split)
            self.compute_with_transfer(hh, transfer)

            if hh.fam_disp_inc > fam_disp_inc_max:
                fam_disp_inc_max, transfer_max = hh.fam_disp_inc, transfer

            if n_points > 1:
                grid_transfers = np.linspace(hh.sp[1].max_split,
                                             hh.sp[0].max_split, n_points-1)
                for transfer in grid_transfers:
                    self.compute_with_transfer(hh, transfer)
                    if hh.fam_disp_inc > fam_disp_inc_max:
                        fam_disp_inc_max, transfer_max = hh.fam_disp_inc, transfer

            if transfer != transfer_max:
                self.compute_with_transfer(hh, transfer_max)

    def compute_with_transfer(self, hh, transfer):
        """
        Cette fonction effectue les transferts de revenus de pension et appelle
        la fonction qui simule le ménage.

        Parameters
        ----------
        hh: Hold
            instance de la classe Hhold
        transfer: float
            transfert du premier au second conjoint (du second au premier si négatif)
        """
        hh.reset()
        p0, p1 = hh.sp[0], hh.sp[1]
        if transfer < 0:
            p0.pension_split = - transfer
            p1.pension_deduction = - transfer
            if p1.age >= 65:
                p0.pension_split_qc = p0.pension_split
                p1.pension_deduction_qc = p1.pension_deduction
        else:
            p1.pension_split = transfer
            p0.pension_deduction = transfer
            if p0.age >= 65:
                p1.pension_split_qc = p1.pension_split
                p0.pension_deduction_qc = p0.pension_deduction

        self.compute_all(hh)

    def compute_all(self, hh):
        """
        Calcule tous les éléments demandés.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        if self.ipayroll:
            self.compute_payroll(hh)  # put payroll before oas
        if self.ioas:
            self.compute_oas(hh)
        if self.policy.some_measures and self.year == 2020:
            self.compute_covid(hh)
        if self.policy.iei and self.year == 2020:
            self.compute_ei(hh)
        if self.ifed:
            self.compute_federal(hh)
        if self.iprov:
            self.compute_prov(hh)
        if self.iass:
            self.compute_ass(hh)
        self.disp_inc(hh)

    def compute_oas(self, hh):
        """
        Calcul des prestations de PSV, SRG, Allocation et Allocation au survivant.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        self.oas.file(hh)

    def compute_federal(self, hh):
        """
        Calcul de l'impôt fédéral.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        self.federal.file(hh)

    def compute_prov(self, hh):
        """
        Calcul de l'impôt provincial.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        self.prov[hh.prov].file(hh)


    def compute_payroll(self, hh):
        """
        Calcul des cotisations sociales.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        self.payroll.compute(hh)

    def compute_covid(self, hh):
        """
        Calcul de la PCU, de la PCUE et du PIRTE (pour 2020).

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        self.covid.compute(hh)

    def compute_ei(self, hh):
        """
        Calcul des prestations de l'assurance emploi qui remplaceraient la PCU (contrefactuel).

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        for p in hh.sp:
            self.ei.compute_benefits_covid(p, hh)

    def compute_ass(self, hh):
        """
        Calcul des prestations d'aide sociale.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        amount = self.ass.apply(hh)
        for p in hh.sp:
            p.inc_social_ass = amount

    def compute_after_tax_inc(self, hh):
        """
        Calcul du revenu après impôt fédéral et provincial.

        Calcul fait au niveau individuel et ensuite rattaché à la personne; le résultat au niveau du ménage est aussi disponible.
        """
        for p in hh.sp:
            after_tax_inc = p.inc_tot
            if self.ifed:
                after_tax_inc -= p.fed_return['net_tax_liability']
            if self.iprov:
                after_tax_inc -= p.prov_return['net_tax_liability']
            p.after_tax_inc = after_tax_inc

    def disp_inc(self, hh):
        """
        Calcul du revenu disponible après impôts, cotisations sociales, épargne (positive ou négative) et prestations.

        Calcul fait au niveau individuel et ensuite rattaché à la personne; le résultat au niveau du ménage est aussi disponible.

        """
        self.compute_after_tax_inc(hh)
        for p in hh.sp:
            disp_inc = p.after_tax_inc
            if self.ipayroll:
                disp_inc -= sum(list(p.payroll.values()))
            if self.iass:
                disp_inc += p.inc_social_ass
            disp_inc -= p.con_rrsp + p.con_non_rrsp
            p.disp_inc = disp_inc


class incentives:
    def __init__(self, case_mode=True, year=2020, data_file=None,
                 multiprocessing=True):
        self.case_mode = case_mode
        self.year = year
        self.set_wages()
        self.set_cases()
        if case_mode:
            self.init_hh()
        else:
            self.load_hh(data_file)
        self.set_hours()
        self.set_covid()
        self.set_tax_system()
        self.multiprocessing = multiprocessing

    def set_cases(self, icouple=True, isp_work=True, ikids=True,
                  iessential=True, insch=True, wages=np.linspace(1, 5, 10)):
        self.icouple = icouple
        self.isp_work = isp_work
        self.ikids = ikids
        self.iessential = iessential
        self.insch = insch
        self.wages = wages
        l_index = []
        if self.icouple:
            l_index.append(['single', 'couple'])
            if self.isp_work:
                l_index.append([True, False])
            else:
                l_index.append([False])
        else:
            # for couple
            l_index.append(['single'])
            # for sp_work
            l_index.append([False])
        if self.ikids:
            l_index.append([0,1,2])
        else:
            l_index.append([0])
        if self.iessential:
            l_index.append([True,False])
        else:
            l_index.append([False])
        if self.insch:
            l_index.append([True,False])
        else:
            l_index.append([False])
        l_index.append(wages)
        cases = list(product(*l_index))
        cases = pd.DataFrame(index=pd.MultiIndex.from_tuples(cases))
        cases.index.names = ['couple', 'sp_work', 'nkids',  'essential',
                             'student', 'wage_multiple']
        to_drop = (cases.index.get_level_values(0)=='single') & (cases.index.get_level_values('sp_work')==True)
        cases = cases.loc[to_drop==False, :]
        self.cases = cases

    def set_hours(self, nh=51, maxh=50, dh=10, weeks_per_year=52.1,
                  hours_full=40):
        self.nh = nh
        self.maxh = maxh
        self.gridh = np.linspace(0,self.maxh, self.nh)
        self.dh = dh
        self.weeks_per_year = weeks_per_year
        self.hours_full = hours_full

    def set_covid(self, months_pre=3, months_covid=4):
        self.months_pre = months_pre
        self.months_covid = months_covid
        self.months_post = 12 - months_pre - months_covid
        self.share_covid = months_covid * 4 / self.weeks_per_year
        self.share_pre = self.months_pre * 4 / self.weeks_per_year
        self.share_post = self.months_post * 4 / self.weeks_per_year

    def set_wages(self,minwage=13.1, avgwage=25.0):
        self.minwage = minwage
        self.avgwage = avgwage

    def set_tax_system(self, tax_system=None):
        if tax_system is not None:
            self.tax_system = tax_system
        else :
            self.tax_system = tax(self.year,iass=False)

    def init_hh(self):
        self.cases['hhold'] = None
        for i in self.cases.index:
            p = Person(age=45, essential_worker=i[3], student=i[4])
            hh = Hhold(p, prov='qc')
            if i[0] == 'couple':
                if i[1]:
                    sp_earn = self.avgwage * self.hours_full * 52.1
                else:
                    sp_earn = 0.0
                sp = Person(age=45,earn=sp_earn)
                hh.sp.append(sp)
            if i[2] > 0:
                for k in range(i[2]):
                    d = Dependent(age=3)
                    hh.dep.append(d)
            self.cases.loc[i,'hhold'] = hh

    def load_hh(self, file):
        if isinstance(file, pd.DataFrame):
            self.cases = file
        else:
            self.cases = pd.read_pickle(file)
        self.cases['couple'] = np.where(self.cases['couple'],'couple','single')
        self.cases['sp_work'] = self.cases['s_inc_earn'] > 0
        self.cases['nkids'] = np.where(self.cases['n_kids']>2,2,self.cases['n_kids'])
        self.cases['essential'] = self.cases['r_essential_worker']
        self.cases['student'] = self.cases['r_student']
        self.cases['wage_multiple'] = self.cases['r_wage']/self.minwage
        self.cases['r_hours_worked_week'] = self.cases['r_hours_worked'] / 50
        self.cases['s_hours_worked_week'] = self.cases['s_hours_worked'] / 50
        self.cases = self.cases.set_index(['couple', 'sp_work', 'nkids',
                                           'essential', 'student',
                                           'wage_multiple'])

    def map_dispinc(self, row):
        """
        Map les attributs aux ménages
        """
        hours_pre = [row['hours_pre'] / self.months_pre] * self.months_pre
        hours_covid = [row['hours_covid'] / self.months_covid] * self.months_covid
        earn_pre = [row['earn_pre'] / self.months_pre] * self.months_pre
        earn_covid = [row['earn_covid'] / self.months_covid] * self.months_covid
        if self.months_post > 0:
            hours_post = [row['hours_post'] / self.months_post] * self.months_post
            earn_post = [row['earn_post'] / self.months_post] * self.months_post
            row['hhold'].sp[0].hours_month = hours_pre + hours_covid + hours_post
            row['hhold'].sp[0].inc_earn = earn_pre + earn_covid + earn_post
            row['hhold'].sp[0].inc_self_earn = earn_pre + earn_covid + earn_post
        else:
            row['hhold'].sp[0].inc_earn = earn_pre + earn_covid
        row['hhold'].sp[0].attach_inc_work_month(row['hhold'].sp[0].inc_earn,
                                                 [0] * 12) # hourly wage based on earn and self_earn mapped into inc_earn
        if row['hhold'].sp[0].student:
            row['hhold'].sp[0].months_cesb = self.months_covid
        else:
            row['hhold'].sp[0].months_cerb = self.months_covid
        self.tax_system.compute(row['hhold'])
        self.tax_system.disp_inc(row['hhold'])
        return row['hhold'].fam_disp_inc

    def set_track_fed(self, attributes=[]):
        """ Fonction qui permet de sortir des éléments du rapport d'impôt fédéral

        Keyword Arguments:
            attributes {list} -- liste des attributs (default: {[]})
        """
        self.fed_track = attributes

    def set_track_prov(self, attributes=[]):
        """ Fonction qu permet de sortir des éléments du rapport d'impôt du Québec

        Keyword Arguments:
            attributes {list} -- liste des attributs (default: {[]})
        """
        self.prov_track = attributes

    def map_chunk(self, df):
        return df.apply(self.map_dispinc,axis=1)

    def get_dispinc(self,h,ifed=False,iprov=False):
        results = self.cases.copy()
        results['wage'] = self.minwage * np.array(results.index.get_level_values('wage_multiple'))
        if self.case_mode:
            results['hours_pre'] = self.hours_full * self.weeks_per_year * self.share_pre
            results['hours_post'] = self.hours_full * self.weeks_per_year * self.share_pre
        else:
            results['hours_pre'] = results['r_hours_worked_week'] * self.weeks_per_year * self.share_pre
            results['hours_post'] = results['r_hours_worked_week'] *self.weeks_per_year * self.share_post
        results['earn_pre'] = results['hours_pre'] * results['wage']
        results['earn_post'] = results['hours_post'] * results['wage']
        results['hours_covid'] = h * self.weeks_per_year * self.share_covid
        results['earn_covid'] = results['hours_covid'] * results['wage']
        results['earn'] = results['earn_pre'] + results['earn_covid'] + results['earn_post']
        if self.multiprocessing:
            nchunks = cpu_count()
            chunks = np.array_split(results,nchunks)
            p = Pool(nchunks)
            results['dispinc'] = pd.concat(p.map(self.map_chunk,chunks))
            p.close()
            p.join()
        else:
            results['dispinc'] = results.apply(self.map_dispinc, axis=1)
        if ifed:
            for attr in self.fed_track:
                results['fed_'+attr] = [hh.sp[0].fed_return[attr] for hh in results['hhold']]
        if iprov:
            for attr in self.prov_track:
                results['prov_'+attr] = [hh.sp[0].prov_return[attr] for hh in results['hhold']]
        return results

    def get_one_emtr(self, h):
        work_base = self.get_dispinc(h)
        work_more = self.get_dispinc(h+self.dh)
        temi = 1.0 - (work_more['dispinc'] - work_base['dispinc'])/(work_more['earn'] - work_base['earn'])
        return temi

    def get_one_ptr(self, h):
        work_base = self.get_dispinc(0)
        work_more = self.get_dispinc(h)
        tepi = 1.0 - (work_more['dispinc'] - work_base['dispinc'])/(work_more['earn'] - work_base['earn'])
        return tepi

    def emtr(self):
        results = self.cases.copy()
        for h in self.gridh:
            results['temi_'+str(int(h))] = self.get_one_emtr(h)
        return results

    def ptr(self):
        results = self.cases.copy()
        for h in self.gridh[1:]:
            results['tepi_'+str(int(h))] = self.get_one_ptr(h)
        return results

    def dispinc(self):
        results = self.cases.copy()
        for h in self.gridh:
            res = self.get_dispinc(h)
            results['dispinc_'+str(int(h))] = res['dispinc']
        return results

    def compute_emtr_ptr_dispinc(self):
        for h in self.gridh:
            self.cases['temi_'+str(int(h))] = self.get_one_emtr(h)
        for h in self.gridh[1:]:
            self.cases['tepi_'+str(int(h))] = self.get_one_ptr(h)
        for h in self.gridh:
            res = self.get_dispinc(h)
            self.cases['dispinc_'+str(int(h))] = res['dispinc']
