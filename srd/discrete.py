from srd import tax
from srd import covid
import numpy as np
import pandas as pd
from numba import njit, prange
from itertools import product
from scipy.linalg import cholesky
from scipy.optimize import minimize
from functools import partial

class behavior:
    def __init__(self,icouple=True, ihetero=True, icost=False, nreps=100):
        """Classe pour estimer modèle offre de travail par méthode de vraisemblance simulée

        Keyword Arguments:
            icouple {bool} -- vrai si considère échantillon de couple (default: {True})
            ihetero {bool} -- vrai si permet hétérogénéité inobservée (default: {True})
            icost {bool} -- vrai si permet coût fixe pour chaque option (default: {False})
            nreps {int} -- nombre de réplication si permet hétérogénéité inobservée (default: {100})
        """
        self.icouple = icouple
        self.ihetero = ihetero
        self.icost = icost
        self.nreps = nreps
        return
    def discretize(self,gridh = [0,1000,2000,3000],Lmax=4e3):
        """Fonction permetant de discrétiser les heures sur une grille

        Keyword Arguments:
            gridh {list} -- liste de choix discret (default: {[0,1000,2000,3000]})
            Lmax {float} -- nb heure loisir maximal (default: {4e3})
        """
        self.nh = len(gridh)
        self.gridh = gridh
        if self.icouple:
            for i in self.data.index:
                self.data.loc[i,'r_choice'] = np.absolute(gridh-self.data.loc[i,'r_hours_worked']).argmin().astype('int64')
                self.data.loc[i,'s_choice'] = np.absolute(gridh-self.data.loc[i,'s_hours_worked']).argmin().astype('int64')
            self.data['r_choice_hours'] = self.data['r_choice'].replace(dict(zip(np.arange(self.nh),self.gridh)))
            self.data['s_choice_hours'] = self.data['s_choice'].replace(dict(zip(np.arange(self.nh),self.gridh)))
            self.data['h_choice'] = self.data['r_choice']*self.nh + self.data['s_choice']
            self.gridh_c = list(product(*[self.gridh,self.gridh]))
            self.nh_c = len(self.gridh_c)
        else :
            for i in self.data.index:
                self.data.loc[i,'r_choice'] = np.absolute(gridh-self.data.loc[i,'r_hours_worked']).argmin().astype('int64')
            self.data['r_choice_hours'] = self.data['r_choice'].replace(dict(zip(np.arange(self.nh),self.gridh)))
            self.data['h_choice'] = self.data.loc[:,'r_choice']
            self.nh = len(self.gridh)
        self.Lmax = Lmax
        return
    #def map_chunk(self,df):
    #    return df.apply(self.map_dispinc,axis=1)
    def dispinc(self,row,hours):
        """Fonction permettant le calcul du revenu disponible étant donné un choix d'heures travaillées

        Arguments:
            row {pandas} -- ligne pandas contenant les information d'un ménage
            hours {float ou tuple de float} -- Si couples, tuple d'heures travaillées, si personne seule, un seul nombre.

        Returns:
            [float] -- le revenu disponible du ménage.
        """
        if self.icouple:
            row['hhold'].sp[0].inc_earn = hours[0]*row['r_wage']
            row['hhold'].sp[1].inc_earn = hours[1]*row['s_wage']
        else :
            row['hhold'].sp[0].inc_earn = hours*row['r_wage']
        self.tax.compute(row['hhold'])
        self.tax.disp_inc(row['hhold'])
        return max(row['hhold'].fam_disp_inc,1.0)
    def budget(self,year=2020,policy=False,iload=False):
        """Fonction qui calcule tous les revenus disponibles pour la grille d'heures

        Keyword Arguments:
            year {int} -- année du système fiscal (default: {2020})
        """
        if iload:
            budget = pd.read_pickle('budget.pkl')
            self.data = self.data.merge(budget,left_index=True,right_index=True)
        else:
            data = self.data.copy()
            cov = covid.policy()
            cov.shut_all_measures()
            self.tax = tax(year,policy=cov)
            for j,h in enumerate(self.gridh_c):
                f = partial(self.dispinc,hours=h)
                self.data['cons_'+str(j)] = data.swifter.apply(f,axis=1)

            budget = self.data[['cons_'+str(j) for j in range(self.nh_c)]]
            budget.to_pickle('budget.pkl')
        return
    def set_shifters(self,list_of_varnames):
        """Fonction permettant de spécifier les noms de variables qui ajusteront l'utilité marginale du loisir.

        Arguments:
            list_of_varnames {[type]} -- liste de noms de variables (sans les préfixes r_ ou s_)
        """
        self.shifters_vars = list_of_varnames
        self.nshifters = len(list_of_varnames)
        return
    def shifters(self):
        """ Fonction qui calcule la valeur des utilités marginales du loisir (sans la portion inobservables)
        """
        # respondent
        mu = self.pars.loc[self.pars.index.get_level_values(0)=='L(r)','value']
        mu = mu.reset_index().set_index('label')['value']
        self.data['mu_r'] = mu['constant']
        for v in self.shifters_vars:
                self.data['mu_r'] += self.data['r_'+v]*mu[v]
        if self.icouple:
            mu = self.pars.loc[self.pars.index.get_level_values(0)=='L(s)','value']
            mu = mu.reset_index().set_index('label')['value']
            self.data['mu_s'] = mu['constant']
            for v in self.shifters_vars:
                self.data['mu_s'] += self.data['s_'+v]*mu[v]
        return
    def initparams(self):
        """ Fonction qui initialise les paramètres de départ du modèle.
        """
        self.pars = pd.DataFrame(columns=['group','label','value','se','free'])
        self.pars.set_index(['group','label'],inplace=True)
        # consumption
        self.pars.loc[('C','constant'),:] = [0.0,0.0,True]
        # respondent leisure
        self.pars.loc[('L(r)','constant'),:] = [0.0,0.0,True]
        for v in self.shifters_vars:
            self.pars.loc[('L(r)',v),:] = [0.0,0.0,True]
        # if heterogeneity
        if self.ihetero:
            self.pars.loc[('L(r)','sigma'),:] = [-1,0.0,True]
        # spouse (if couple)
        if self.icouple:
            self.pars.loc[('L(s)','constant'),:] = [0.0,0.0,True]
            for v in self.shifters_vars:
                self.pars.loc[('L(s)',v),:] = [0.0,0.0,True]
            # if heterogeneity
            if self.ihetero:
                self.pars.loc[('L(s)','sigma'),:] = [-1,0.0,True]
        # joint leisure (if couple)
        if self.icouple:
            self.pars.loc[('L(r,s)','constant'),:] = [0.0,0.0,True]
        # correlation UH
        if self.icouple:
            if self.ihetero:
                self.pars.loc[('L(r,s)','rho'),:] = [0.0,0.0,True]
        # fixed costs
        if self.icost:
            for h in range(1,self.nh):
                self.pars.loc[('FC(r)',str(h)),:] = [0.0,0.0,True]
            if self.icouple:
                for h in range(1,self.nh):
                    self.pars.loc[('FC(s)',str(h)),:] = [0.0,0.0,True]
        # number of parameters
        self.npars = len(self.pars)
        self.nfreepars = self.pars['free'].sum()
        return
    def fixpar(self,group,label,value):
        """ Fonction afin de fixer la valeur d'un paramètre (contraint l'estimation)

        Arguments:
            group {[type]} -- Le groupe de paramètres (C,L(r),L(s),L(r,s),FC(r),FC(s))
            label {[type]} -- Le nom du paramètre (constant ou le nom d'un shifter, etc)
            value {[type]} -- Valeur à laquelle le paramètre est contraint
        """
        self.pars.loc[(group,label),'free'] = False
        self.pars.loc[(group,label),'value'] = value
        self.nfreepars = self.pars['free'].sum()
        return
    def freepar(self,group,label):
        """ Fonction afin de fixer la valeur d'un paramètre (contraint l'estimation)

        Arguments:
            group {[type]} -- Le groupe de paramètres (C,L(r),L(s),L(r,s),FC(r),FC(s))
            label {[type]} -- Le nom du paramètre (constant ou le nom d'un shifter, etc)
            value {[type]} -- Valeur à laquelle le paramètre est contraint
        """
        self.pars.loc[(group,label),'free'] = True
        self.nfreepars = self.pars['free'].sum()
        return
    def initdata(self,file):
        """Fonction qui initialise les données.

        Voir le notebook create_hhold.ipynb pour un exemple de mise en forme.

        Arguments:
            file {str} -- le nom du fichier de données mise en forme.
        """
        self.data = pd.read_pickle(file)
        if self.icouple:
            self.data = self.data.loc[self.data.couple,:]
        else :
            self.data = self.data.loc[self.data.couple==False,:]
        self.n = len(self.data)
        return
    def initdraws(self):
        """Initialisation des tirages aléatoires pour l'estimation.
        """
        if self.icouple:
            self.draws_r = np.random.normal(size=(self.n,self.nreps))
            self.draws_s = np.random.normal(size=(self.n,self.nreps))
        else :
            self.draws_r = np.random.normal(size=(self.n,self.nreps))
        return
    def set_theta(self,theta):
        """Fonction permettant d'assigner les paramètres libres à l'instance pars

        Arguments:
            theta {numpy.array} -- Vecteur de paramètres libres.
        """
        self.pars.loc[self.pars.free,'value'] = theta
        return
    def extract_theta(self):
        """Fonction permettant d'extraire les paramètres libres provenant de l'instance pars

        Returns:
            [numpy.array] -- vecteur des paramètres libres.
        """
        theta = self.pars.loc[self.pars.free,'value']
        return theta
    def callback(self,x):      
        fobj = self.loglike(x)
        self.set_theta(x)
        print('iter = ',self.iter_num)
        print('parameters at iteration:')
        print(self.pars['value'])
        print('likelihood = ', fobj)
        self.iter_num +=1
    def get_prob(self,theta):
        self.set_theta(theta)
        # compute shifters
        self.shifters()
        N = self.n
        R = self.nreps
        if self.icouple:
            J = self.nh_c
            mu_r = self.data.loc[:,'mu_r'].astype('float64').values.reshape((N,1))
            mu_s = self.data.loc[:,'mu_s'].astype('float64').values.reshape((N,1))
            mu_c = self.pars.loc[('C','constant'),'value']
            mu_rs = self.pars.loc[('L(r,s)','constant'),'value']
            C = self.data[['cons_'+str(j) for j in range(self.nh_c)]].values.reshape((N,J))
            Lmax = self.Lmax
            Lr = np.array([Lmax-h[0] for h in self.gridh_c]).reshape((1,J))
            Ls = np.array([Lmax-h[1] for h in self.gridh_c]).reshape((1,J))
            V = np.zeros((2,2))
            V[0,0] = np.exp(self.pars.loc[('L(r)','sigma'),'value'])
            V[1,1] = np.exp(self.pars.loc[('L(s)','sigma'),'value'])
            V[1,0] = np.tanh(self.pars.loc[('L(r,s)','rho'),'value'])*np.sqrt(V[0,0]*V[1,1])
            V[0,1] = V[1,0]
            Lv = cholesky(V, lower=True)
            eta_r = self.draws_r
            eta_s = self.draws_s

            choice = self.data.loc[:,'h_choice'].astype('int64').values
            if self.icost:
                fcosts_r = self.pars.loc[self.pars.index.get_level_values(0)=='FC(r)','value'].values
                fcosts_r = np.insert(fcosts_r,0,0.0)
                fcosts_s = self.pars.loc[self.pars.index.get_level_values(0)=='FC(s)','value'].values
                fcosts_s = np.insert(fcosts_s,0,0.0)
                fcosts_r = np.array(np.repeat(fcosts_r,self.nh),dtype='float64').reshape((1,J))
                fcosts_s = np.array(np.kron(np.ones(self.nh),fcosts_s),dtype='float64').reshape((1,J))
            else :
                fcosts_r = np.zeros(J)
                fcosts_s = np.zeros(J)
            utils = np.zeros((N,J))
            pr = np.zeros((N,R))
            for r in range(R):
                mur = mu_r + Lv[0,0]*eta_r[:,r]
                mus = mu_s + Lv[1,0]*eta_r[:,r] + Lv[1,1]*eta_s[:,r]
                utils = mur @ np.log(Lr) + mus @ np.log(Ls) + mu_c * np.log(C) 
                utils += np.ones((N,1)) @ (mu_rs*(np.log(Lr)*np.log(Ls)) +fcosts_r + fcosts_s)
                #for j in range(J):
                #    utils[:,j] = mur*np.log(Lr[j]) + mus*np.log(Ls[j]) + mu_c*np.log(C[:,j]) + mu_rs*np.log(Lr[j])*np.log(Ls[j]) + fcosts_r[j] + fcosts_s[j]
                num = np.exp(utils[np.arange(N),choice])
                den = np.sum(np.exp(utils),axis=1)
                pr[:,r] = num/den
                #print(np.min(np.mean(pr,axis=1)),np.max(np.mean(pr,axis=1)))
            #pr = prob_couple(choice,mu_r,mu_s,mu_c,mu_rs,C,Lr,Ls,Lv,eta_r,eta_s,fcosts_r,fcosts_s,N,R,J)
        else :
            mu_r = self.data.loc[:,'mu_r'].astype('float64').values
            mu_c = self.pars.loc[('C','constant'),'value'].values
            C = self.data[['cons_'+str(j) for j in range(self.nh)]].values
            Lmax = self.Lmax
            Lr = [Lmax-h for h in self.gridh]
            sigma = np.sqrt(np.exp(self.pars.loc[('L(r)','sigma'),'value']))
            eta_r = self.draws_r
            J = self.nh
            choice = self.data.loc[:,'r_choice'].astype('int64').values
            if self.icost:
                fcosts = self.pars.loc[self.pars.index.get_level_values(0)=='FC','value'].values
                fcosts = np.insert(fcosts,0,0.0)
            else :
                fcosts = np.zeros(J)
            pr = prob_single(choice,mu_r,mu_c,C,Lr,sigma,eta_r,fcosts,N,R,J)
        return np.mean(pr,axis=1)
    def loglike(self,theta):
        """Log-vraisemblance simulées

        Arguments:
            theta {numpy.array} -- vecteur de paramètres libres.

        Returns:
            [float] -- Vraisemblance simulée (moyenne)
        """

        pr = self.get_prob(theta)
        return np.mean(np.log(pr))

    def loglike_i(self,theta):
        """Contribution à la vraisemblance simulée

        Arguments:
            theta {numpy.array} -- vecteur de paramètres libres.

        Returns:
            [numpy.array] -- vecteur des contributions de chaque ménage à la log-vraisemblance
        """

        pr = self.get_prob(theta)
        return np.log(pr)

    def estimate(self):
        """ Fonction permettant d'estimer les paramètres par maximum de vraisemblance simulée

        Utilise l'algorithme BFGS. Après l'estimation, les paramètres sont placés dans pars et la log vraisemblance simulée est sauvegardée comme attribut de la classe.

        """
        init_theta = self.extract_theta()
        neg_loglike = lambda q: -self.loglike(q)
        self.iter_num = 0
        results = minimize(neg_loglike,init_theta,method='BFGS',callback=self.callback)
        if results.success:
            print('optimizer exited successfully with ', results.nit,' iterations.')
        else :
            print('did not exit successfully!', results.nit,' iterations.')
        self.set_theta(results.x)
        self.loglike_value = self.loglike(results.x)
        return
    def covar(self):
        """ Fonction permettant de calculer les écart-types.

        Utilise la méthode du produit des gradients croisés (OPG). Les écart-types sont placés dans pars et la matrice variance-covariance est sauvegardée comme attribut de la classe.
        """
        # number of free parameters and number of observations
        npars = self.nfreepars
        n = self.n
        # matrix to save gragients
        G = np.zeros((n,npars))
        # step for computing gradient
        eps = 1e-4
        # get thetas from pars object
        theta = self.extract_theta()
        # compute baseline likelihood contributions
        fn_zero = self.loglike_i(theta)
        # compute gradient of each obs with respect to each parameter
        for i in range(npars):
            theta_up = theta[:]
            theta_up[i] += eps
            fn_up = self.loglike_i(theta_up)
            G[:,i] = (fn_up - fn_zero)/eps
        # outer product of gradient formula (OPG)
        B = G.T @ G /n
        # covariance matrix
        cov = np.linalg.inv(B)/n
        # save for future reference
        self.cov_pars = cov
        # compute standard errors
        ses = np.sqrt(np.diagonal(cov))
        # save standard errors in parameters
        self.pars.loc[self.pars.free,'se'] = ses
        return

@njit(parallel=False)
def prob_couple(choice,mu_r,mu_s,mu_c,mu_rs,
                    C,Lr,Ls,Lv,eta_r,eta_s, fcosts_r, fcosts_s, N, R, J):
    """Fonction numba pour calculer la probabilité d'observer les choix des ménages.

    Arguments:
        choice {numpy.array} -- vecteur des choix (discret en indice) des N ménages
        mu_r {numpy.array} -- vecteur des utilités marginales du loisir de r
        mu_s {numpy.array} -- vecteur des utilités marginales du loisir de s
        mu_c {float} -- utilité marginale de la consommation (fixe)
        mu_rs {float} -- utilité marginale du loisir conjoint
        C {numpy.array} -- matrice des revenus disponibles (N par J ou J est le nombre d'alternatives)
        Lr {numpy.array} -- vecteur des heures de loisirs de r (J alternatives)
        Ls {numpy.array} -- vecteur des heures de loisirs de s (J alternatives)
        Lv {numpy.array} -- décomposition de cholesky de la matrice variance covariance des termes inobservables
        eta_r {numpy.array} -- tirages N(0,1) pour le terme inobservables du répondant (N par R)
        eta_s {numpy.array} -- tirages N(0,1) pour le terme inobservables du conjoint (N par R)
        fcosts_r {numpy.array} -- paramètres de coûts fixes des alternatives (r).
        fcosts_s {numpy.array} -- paramètres de coûts fixes des alternatives (s).
        N {int} -- nombre de ménages
        R {int} -- nombre de réplications (simulations)
        J {int} -- nombre d'alternatives

    Returns:
        [numpy.array] -- probabilités d'observer le choix de chacun des ménages (N par 1)
    """

    utils = np.zeros((N,J))
    pi = np.zeros((N,R))
    for r in range(R):
        mur = mu_r + Lv[0,0]*eta_r[:,r]
        mus = mu_s + Lv[1,0]*eta_r[:,r] + Lv[1,1]*eta_s[:,r]
        for j in range(J):
            utils[:,j] = mur*np.log(Lr[j]) + mus*np.log(Ls[j]) + mu_c*np.log(C[:,j]) + mu_rs*np.log(Lr[j])*np.log(Ls[j]) + fcosts_r[j] + fcosts_s[j]
        for i in range(N):
            pi[i,r] = np.exp(utils[i,choice[i]])/np.sum(np.exp(utils[i,:]))
    return pi

@njit(parallel=False)
def prob_single(choice,mu_r,mu_c,C,Lr,sigma,eta,fcosts,N,R,J):
    """Fonction numba pour calculer la probabilité d'observer les choix des ménages.

    Arguments:
        choice {numpy.array} -- vecteur des choix (discret en indice) des N ménages
        mu_r {numpy.array} -- vecteur des utilités marginales du loisir de r
        mu_c {float} -- utilité marginale de la consommation (fixe)
        C {numpy.array} -- matrice des revenus disponibles (N par J ou J est le nombre d'alternatives)
        Lr {numpy.array} -- vecteur des heures de loisirs de r (J alternatives)
        sigma {float} -- écart-type de la distribution du terme inobservable.
        eta {numpy.array} -- tirages N(0,1) pour le terme inobservables du répondant (N par R)
        fcosts {numpy.array} -- paramètres de coûts fixes des J alternatives.
        N {int} -- nombre de ménages
        R {int} -- nombre de réplications (simulations)
        J {int} -- nombre d'alternatives
    Returns:
        [numpy.array] -- probabilités d'observer le choix de chacun des ménages (N par 1)
    """

    pi = np.zeros(N)
    u = np.zeros((N,J))
    for r in range(R):
        mur = mu_r + sigma*eta[:,r]
        for j in range(J):
            u[:,j] = (mur*np.log(Lr[j]) + mu_c*np.log(C[:,j]) + fcosts[j])
        for i in range(N):
            pi[i] += np.exp(u[i,choice[i]])/np.sum(np.exp(u[i,:]))
    return pi/R




