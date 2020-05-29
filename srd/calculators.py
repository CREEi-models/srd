import numpy as np
from srd import federal, oas, quebec, payroll, assistance, covid, Person, Hhold, Dependent
from itertools import product, chain
import pandas as pd
import swifter
from multiprocessing import cpu_count, Pool

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
    icovid_all: boolean
        vrai si calcul des mesures d'urgence liées à la covid-19 est demandé (seulement en 2020)
    """
    def __init__(self, year, prov='qc', ifed=True, ioas=True, iprov=True,
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
        if policy.some_measures and year==2020:
            self.covid = covid.programs(policy)
        if ifed:
            self.federal = federal.form(year, policy)
        if iprov:
            if prov == 'qc':
                self.prov = quebec.form(year)
        if ioas:
            self.oas = oas.program(year, self.federal)
        if iass:
            self.ass = assistance.program(year)
        return

    def compute(self, hh):
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
        if self.policy.some_measures and self.year==2020:
            self.compute_covid(hh)
        if self.ifed:
            self.compute_federal(hh)
        if self.iprov:
            self.compute_prov(hh)
        if self.iass:
            self.compute_ass(hh)
        self.disp_inc(hh)

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
    def compute_covid(self, hh):
        """
        Calcul des prestations canadiennes d'urgences (PCU et PCUE)
        et du programme incitatif pour la rétention des travailleurs essentiels (PIRTE).

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        self.covid.compute(hh)

    def compute_ass(self, hh):
        """
        Calcul de l'aide sociale.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        for p in hh.sp:
            p.inc_social_ass = self.ass.apply(hh)

    def compute_after_tax_inc(self,hh):
        """
        Calcul du revenu après impôt fédéral et provincial.

        Calcul fait au niveau individuel et ensuite rattaché à la personne. Un calcul au niveau du ménage est aussi effectué.
        """
        for p in hh.sp:
            after_tax_inc = p.inc_tot
            if self.ifed:
                after_tax_inc -= p.fed_return['net_tax_liability']
            if self.iprov:
                after_tax_inc -= p.prov_return['net_tax_liability']
            p.after_tax_inc = after_tax_inc
        return
    def disp_inc(self,hh):
        """
        Calcul du revenu disponible après impôt, cotisations (sociale et REER) et aide sociale.

        Calcul fait au niveau individuel et ensuite rattaché à la personne.

        """
        self.compute_after_tax_inc(hh)
        for p in hh.sp:
            disp_inc = p.after_tax_inc
            if self.ipayroll:
                disp_inc -= sum(list(p.payroll.values()))
            if self.iass:
                disp_inc += p.inc_social_ass
            disp_inc -= p.con_rrsp
            p.disp_inc = disp_inc

class incentives:
    def __init__(self, case_mode=True, year=2020,data_file=None):
        self.case_mode = case_mode
        self.year = year
        self.set_wages()
        self.set_cases()
        if case_mode:
            self.init_hh()
        else :
            self.load_hh(data_file)

        self.set_hours()
        self.set_covid()
        self.set_tax_system()
        return
    def set_cases(self,icouple=True, isp_work=True, ikids=True,
                  iessential=True, insch=True, wages=np.linspace(1,5,10)):
        self.icouple = icouple
        self.isp_work = isp_work
        self.ikids = ikids
        self.iessential = iessential
        self.insch = insch
        self.wages = wages
        l_index = []
        if self.icouple:
            l_index.append(['single','couple'])
            if self.isp_work:
                l_index.append([True,False])
            else :
                l_index.append([False])
        else :
            # for couple
            l_index.append(['single'])
            # for sp_work
            l_index.append([False])
        if self.ikids:
            l_index.append([0,1,2])
        else :
            l_index.append([0])
        if self.iessential:
            l_index.append([True,False])
        else :
            l_index.append([False])
        if self.insch:
            l_index.append([True,False])
        else :
            l_index.append([False])
        l_index.append(wages)
        cases = list(product(*l_index))
        cases = pd.DataFrame(index=pd.MultiIndex.from_tuples(cases))
        cases.index.names=['couple','sp_work', 'nkids',  'essential', 'student', 'wage_multiple']
        to_drop = (cases.index.get_level_values(0)=='single') & (cases.index.get_level_values('sp_work')==True)
        cases = cases.loc[to_drop==False,:]
        self.cases = cases
        return
    def set_hours(self,nh=51,maxh=50,dh=10,weeks_per_year=52.1,hours_full=40):
        self.nh = nh
        self.maxh = maxh
        self.gridh = np.linspace(0,self.maxh,self.nh)
        self.dh = dh
        self.weeks_per_year = weeks_per_year
        self.hours_full = hours_full
        return
    def set_covid(self,months_pre=3,months_covid=4):
        self.months_pre = months_pre
        self.months_covid = months_covid
        self.months_post = 12 - months_pre - months_covid
        self.share_covid = months_covid*4/self.weeks_per_year
        self.share_pre = 0.5*(1-self.share_covid)
        self.share_post = 0.5*(1-self.share_covid)
        return
    def set_wages(self,minwage=13.1,avgwage=25.0):
        self.minwage = minwage
        self.avgwage = avgwage
        return
    def set_tax_system(self,tax_system=None):
        if tax_system!=None:
            self.tax_system = tax_system
        else :
            self.tax_system = tax(self.year,iass=False)
        return
    def init_hh(self):
        self.cases['hhold'] = None
        for i in self.cases.index:
            p = Person(age=45, essential_worker=i[3], student=i[4])
            hh = Hhold(p,prov='qc')
            if i[0]=='couple':
                if i[1]:
                    sp_earn = self.avgwage*40.0*52.1
                else :
                    sp_earn = 0.0
                sp = Person(age=45,earn=sp_earn)
                hh.sp.append(sp)
            if i[2]>0:
                for k in range(i[2]):
                    d = Dependent(age=3)
                    hh.dep.append(d)
            self.cases.loc[i,'hhold'] = hh
        return
    def load_hh(self,file):
        self.cases = pd.read_pickle(file)
        self.cases['couple'] = np.where(self.cases['couple'],'couple','single')
        self.cases['sp_work'] = self.cases['s_inc_earn']>0.0
        self.cases['nkids'] = np.where(self.cases['n_kids']>2,2,self.cases['n_kids'])
        self.cases['essential'] = self.cases['r_essential_worker']
        self.cases['student'] = False
        self.cases['wage_multiple'] = self.cases['r_wage']/self.minwage
        self.cases['r_hours_worked_week'] = self.cases['r_hours_worked']/50
        self.cases['s_hours_worked_week'] = self.cases['s_hours_worked']/50
        self.cases = self.cases.set_index(['couple','sp_work','nkids','essential','student','wage_multiple'])
        return
    def map_dispinc(self, row):
        """
        Map les attributs aux ménages
        """
        if row['hhold'].sp[0].student:
            earn_pre = [0.0]*self.months_pre
        else :
            earn_pre = [row['earn_pre'] / self.months_pre] * self.months_pre
        earn_covid = [row['earn_covid'] / self.months_covid] * self.months_covid
        if self.months_post > 0:
            if row['hhold'].sp[0].student:
                earn_post = [0.0] * self.months_post
            else :
                earn_post = [row['earn_post'] / self.months_post] * self.months_post
            row['hhold'].sp[0].inc_earn = list(chain(*[earn_pre,earn_covid,earn_post]))
        else :
            row['hhold'].sp[0].inc_earn = list(chain(*[earn_pre,earn_covid]))
        row['hhold'].sp[0].attach_inc_earn_month(row['hhold'].sp[0].inc_earn)
        if row['hhold'].sp[0].student:
            row['hhold'].sp[0].months_cesb = self.months_covid
        else :
            row['hhold'].sp[0].months_cerb = self.months_covid
        self.tax_system.compute(row['hhold'])
        self.tax_system.disp_inc(row['hhold'])
        return row['hhold'].fam_disp_inc
    def set_track_fed(self,attributes=[]):
        """ Fonction qu permet de sortir des éléments du rapport d'impôt fédéral

        Keyword Arguments:
            attributes {list} -- liste des attributs (default: {[]})
        """
        self.fed_track = attributes
        return
    def set_track_prov(self,attributes=[]):
        """ Fonction qu permet de sortir des éléments du rapport d'impôt du Québec

        Keyword Arguments:
            attributes {list} -- liste des attributs (default: {[]})
        """
        self.prov_track = attributes
        return
    def map_chunk(self,df):
        return df.apply(self.map_dispinc,axis=1)
    def get_dispinc(self,h,ifed=False,iprov=False):
        results = self.cases.copy()
        results['wage'] = self.minwage * np.array(results.index.get_level_values('wage_multiple'))
        if self.case_mode:
            results['earn_pre'] = self.hours_full * self.weeks_per_year * self.share_pre * results['wage']
            results['earn_post'] = self.hours_full *self.weeks_per_year * self.share_post * results['wage']
        else :
            results['earn_pre'] = results['r_hours_worked_week'] * self.weeks_per_year * self.share_pre * results['wage']
            results['earn_post'] = results['r_hours_worked_week'] *self.weeks_per_year * self.share_post * results['wage']
        results['earn_covid'] = h * self.weeks_per_year * self.share_covid * results['wage']
        results['earn'] = results['earn_pre'] + results['earn_covid'] + results['earn_post']
        nchunks = cpu_count()
        chunks = np.array_split(results,nchunks)
        p = Pool(nchunks)
        results['dispinc'] = pd.concat(p.map(self.map_chunk,chunks))
        p.close()
        p.join()
        if ifed:
            for attr in self.fed_track:
                results['fed_'+attr] = [hh.sp[0].fed_return[attr] for hh in results['hhold']]
        if iprov:
            for attr in self.prov_track:
                results['prov_'+attr] = [hh.sp[0].prov_return[attr] for hh in results['hhold']]
        return results
    def get_one_emtr(self,h):
        work_base = self.get_dispinc(h)
        work_more = self.get_dispinc(h+self.dh)
        temi = 1.0 - (work_more['dispinc'] - work_base['dispinc'])/(work_more['earn'] - work_base['earn'])
        return temi
    def get_one_ptr(self,h):
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
