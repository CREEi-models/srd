from srd import tax
import numpy as np
import pandas as pd
from numba import njit, prange
from itertools import product
from scipy.linalg import cholesky
from scipy.optimize import minimize 

class behavior:
    def __init__(self,icouple=True, ihetero=True, icost=False, nreps=100):
        self.icouple = icouple 
        self.ihetero = ihetero 
        self.icost = icost
        self.nreps = nreps
        return 
    def discretize(self,gridh = [0,1000,2000,3000],Lmax=4e3):
        self.nh = len(gridh)
        self.gridh = gridh
        if self.icouple:
            for i in self.data.index:
                self.data.loc[i,'r_choice'] = np.absolute(gridh-self.data.loc[i,'r_hours_worked']).argmin().astype('int64')
                self.data.loc[i,'s_choice'] = np.absolute(gridh-self.data.loc[i,'s_hours_worked']).argmin().astype('int64')
            self.data['r_choice_hours'] = self.data['r_choice'].replace(dict(zip(np.arange(self.nh),self.gridh)))
            self.data['s_choice_hours'] = self.data['s_choice'].replace(dict(zip(np.arange(self.nh),self.gridh)))
            self.data['h_choice'] = self.data['r_choice']*self.nh + self.data['s_choice']
            self.gridh = list(product(*[self.gridh,self.gridh]))
            self.nh = len(self.gridh)
        self.Lmax = Lmax
        return 
    def dispinc(self,row,hours):
        if self.icouple:
            row['hhold'].sp[0].earn = hours[0]*row['r_wage']
            row['hhold'].sp[1].earn = hours[1]*row['s_wage']
            self.tax.compute(row['hhold'])
        else :
            row['hhold'].sp[0].earn = hours*row['r_wage']
            self.tax.compute(row['hhold'])
        return row['hhold'].fam_disp_inc()
    def budget(self,year=2020):
        self.tax = tax(year)
        for j,h in enumerate(self.gridh):
            self.data['cons_'+str(j)] = self.data.apply(self.dispinc,axis=1,args=(h)) 
        return 
    def set_shifters(self,list_of_varnames):
        self.shifters_vars = list_of_varnames
        self.nshifters = len(list_of_varnames)
        return 
    def shifters(self):
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
        self.pars = pd.DataFrame(columns=['group','label','value','se','free'])
        self.pars.set_index(['group','label'],inplace=True)
        # consumption
        self.pars.loc[('C','constant'),:] = [1e-2,0.0,True]
        # respondent leisure 
        self.pars.loc[('L(r)','constant'),:] = [1e-2,0.0,True]
        for v in self.shifters_vars:
            self.pars.loc[('L(r)',v),:] = [0.0,0.0,True]
        # if heterogeneity
        if self.ihetero:
            self.pars.loc[('L(r)','sigma'),:] = [-3,0.0,True]
        # spouse (if couple)
        if self.icouple: 
            self.pars.loc[('L(s)','constant'),:] = [1e-2,0.0,True]
            for v in self.shifters_vars:
                self.pars.loc[('L(s)',v),:] = [0.0,0.0,True]
            # if heterogeneity
            if self.ihetero:
                self.pars.loc[('L(s)','sigma'),:] = [-3,0.0,True]
        # joint leisure (if couple)
        if self.icouple:
            self.pars.loc[('L(r,s)','constant'),:] = [1e-2,0.0,True]
        # correlation UH
        if self.icouple:
            if self.ihetero:
                self.pars.loc[('L(r,s)','rho'),:] = [0.0,0.0,True]
        # fixed costs
        if self.icost:
            for h in range(1,self.nh):
                self.pars.loc[('FC',str(h)),:] = [0.0,0.0,True]
        # number of parameters
        self.npars = len(self.pars)
        self.nfreepars = self.pars['free'].sum()
        return 
    def fixpar(self,group,label,value):
        self.pars.loc[(group,label),'free'] = False 
        self.pars.loc[(group,label),'value'] = value
        self.nfreepars = self.pars['free'].sum()
        return 
    def initdata(self,file):
        self.data = pd.read_pickle(file)
        if self.icouple: 
            self.data = self.data.loc[self.data.couple,:]
        else :
            self.data = self.data.loc[self.data.couple==False,:]    
        self.n = len(self.data)
        return 
    def initdraws(self):
        if self.icouple:
            self.draws_r = np.random.normal((self.n,self.nreps))
            self.draws_s = np.random.normal((self.n,self.nreps))
        else :
            self.draws_r = np.random.normal((self.n,self.nreps))   
        return 
    def set_theta(self,theta):
        self.pars.loc[self.pars.free,'value'] = theta
        return 
    def extract_theta(self):
        theta = self.pars.loc[self.pars.free,'value']
        return theta
    def loglike(self,theta):
        self.set_theta(theta)
        # compute shifters
        self.shifters()
        N = self.n
        R = self.nreps       
        if self.icouple:
            mu_r = self.data.loc[:,'mu_r'].values
            mu_s = self.data.loc[:,'mu_s'].values
            mu_c = self.pars.loc[('C','constant'),'value'].values
            mu_rs = self.pars.loc[('L(r,s)','constant'),'value']
            C = self.data[['cons_'+str(j) for j in range(self.nh)]].values
            Lmax = self.Lmax
            Lr = [Lmax-h[0] for h in self.gridh]
            Ls = [Lmax-h[1] for h in self.gridh]
            V = np.zeros((2,2))
            V[0,0] = np.exp(self.pars.loc[('L(r)','sigma'),'value'])
            V[1,1] = np.exp(self.pars.loc[('L(s)','sigma'),'value'])
            V[1,0] = np.tanh(self.pars.loc[('L(r,s)','rho'),'value'])*np.sqrt(V[0,0]*V[1,1])
            V[0,1] = V[1,0]
            Lv = cholesky(V, lower=True)
            eta_r = self.draws_r
            eta_s = self.draws_s
            J = self.nh
            choice = self.data.loc[:,'h_choice']
            fcosts = self.pars.loc[self.pars.index.get_level_values(0)=='FC','value'].values
            prob = prob_couple(choice,mu_r,mu_s,mu_c,mu_rs,C,Lr,Ls,Lv,eta_r,eta_s,fcosts,N,R,J)      
        return np.mean(np.log(prob))
            
    def estimate(self):
        init_theta = self.extract_theta()
        neg_loglike = -self.loglike 
        results = minimize(neg_loglike,init_theta,method='BFGS')
        if results.success:
            print('optimizer exited successfully with ', results.nit,' iterations.')
        else :
            print('DID NOT EXIT SUCCESSFULLY!', results.nit,' iterations.')
        self.set_theta(results.x)
        self.loglike_value = loglike(results.x)
        return 
    def covar(self):
        return 
    def summary(self):
        return 

@njit(parallel=False)
def prob_couple(choice,mu_r,mu_s,mu_c,mu_rs,
                    C,Lr,Ls,Lv,eta_r,eta_s,fcosts,N,R,J):
    pr = np.zeros((N,R))
    u = np.zeros((N,J))   
    for r in range(R):
        mur = mu_r + Lv[0,0]*eta_r[:,r]
        mus = mu_s + Lv[1,0]*eta_r[:,r] + Lv[1,1]*eta_s[:,r]
        for j in range(J):
            u[:,j] = (mur*np.log(Lr[j]) + mus*np.log(Ls[j]) 
                 + mu_c*np.log(C[:,j]) + mu_rs*np.log(Lr[j])*np.log(Ls[j])+ fcosts[j])
        for i in range(N):
            pr[i,r] = np.exp(u[i,choice[i]])/np.sum(np.exp(u[i,:]))
    return np.mean(pr,axis=1)
        
            
        
            
    
