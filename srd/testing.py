import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.distributions.empirical_distribution import ECDF
pd.options.display.max_columns = None
pd.options.display.max_rows = None


class Testing:
    def __init__(self, data, d_measures, d_income):
        self.data = data
        self.d_measures = d_measures
        self.d_income = d_income
        self.l_markers = '.*o^<>'

    def plot_scatter(self, measure, l_groups=['all'], by_family=False,
                     alpha=1):
        print(measure)
        self.measure = measure
        self.l_groups = l_groups
        self.by_family = by_family
        self.alpha = alpha

        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        self.create_scatter(ax)
        plt.show()

    def plot_ecdf(self, measure, l_groups=['all'], by_family=False):
        print(measure)
        self.measure = measure
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        self.create_ecdf(ax, by_family)
        plt.show()

    def plot_scatter_ecdf(self, measure, l_groups=['all'], by_family=False,
                          alpha=1):
        print(measure)
        self.measure = measure
        self.l_groups = l_groups
        self.by_family = by_family
        self.alpha = alpha

        fig, ax = plt.subplots(1, 2, figsize=(16, 6))
        self.create_scatter(ax[0])
        self.create_ecdf(ax[1])
        plt.show()

    def plot_compare_net_inc(self, measure, income, l_groups=['all'],
                             by_family=False, family_income=False, alpha=1,
                             upper_inc=50e3):
        print(measure)
        self.measure = measure
        self.income = income
        self.by_family = by_family
        self.fam_income = family_income
        self.alpha = alpha
        self.upper_inc = upper_inc

        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        self.compare_net_inc(ax)
        plt.show()

    def create_scatter(self, ax):
        self.ax = ax          
        for group, marker in zip(self.l_groups, self.l_markers):
            self.df = self.data.copy()
            self.group = group
            self.marker = marker

            if group != 'all':
                self.create_condition(group)
                self.drop_hholds()

            meas_srd, meas_bdsps = self.d_measures[self.measure]
            if self.by_family:
                meas = self.df.groupby('ind_econ_fam')[[meas_srd, meas_bdsps]].agg('sum')
            else:
                meas = self.df[[meas_srd, meas_bdsps]]

            self.scatter45(meas[meas_srd], meas[meas_bdsps])
            self.ax.legend()

    def create_condition(self, group):
        cond = self.df[group[0]].copy()
        for k in group[1:]:
            cond &= self.df[k]
        self.cond = cond

    def drop_hholds(self):
        """
        Drops the entire household when one spouse does not satisfy condition.
        """
        l_to_drop = set(self.df.loc[~self.cond, 'ind_econ_fam'])
        self.df = self.df.loc[~self.df.ind_econ_fam.isin(l_to_drop), :]

    def scatter45(self, x, y):
        self.ax.scatter(x, y, label=self.group, marker=self.marker, 
                        alpha=self.alpha)
        x_45 = min(min(x), min(y))
        y_45 = min(max(x), max(y))
        lims = x_45, y_45
        self.ax.plot(lims, lims, c='k', linewidth=0.5, alpha=0.5)
        self.ax.set_xlabel('srd')
        self.ax.set_ylabel('bdsps')
             
    def create_ecdf(self, ax, outer_limits=[-500, 500], sample_graph=int(1e6)):
        self.ax = ax
        self.df = self.data.copy()  # skip the step of forming groups

        meas_srd, meas_bdsps = self.d_measures[self.measure]
        if self.by_family:
            meas = self.df.groupby('ind_econ_fam')[[meas_srd, meas_bdsps, 'weight']].agg('sum')
        else:
            meas = self.df[[meas_srd, meas_bdsps, 'weight']]

        x, y = meas[meas_srd], meas[meas_bdsps]
        non_zero = np.maximum(abs(x), abs(y)) > 0
        perc_non_zero = np.round(sum(non_zero * meas.weight) / sum(meas.weight) * 100, 2)

        diff = x - y
        weight = meas.weight
        outer_lims = outer_limits

        pop_diff = np.repeat(diff, weight)
        sample_diff = np.random.choice(pop_diff, size=sample_graph, replace=False)
        sample_diff.sort()
        ecdf = ECDF(sample_diff)
        cum_prob = ecdf(sample_diff)
        self.ax.plot(sample_diff, cum_prob)

        l_perc = [0, 0.01, 0.99, 1]
        quantiles = np.quantile(sample_diff, l_perc)
        self.ax.axvline(quantiles[1], linestyle='-', linewidth=1, color='r', 
                        label=l_perc[1])
        self.ax.axvline(quantiles[-2], linestyle='--', linewidth=1, color='b',
                        label=l_perc[-2])

        lims = [min(max(outer_lims[0], quantiles[0]), quantiles[1]), 
                max(min(outer_lims[1], quantiles[-1]), quantiles[-2])]
        self.ax.legend(loc='upper left')
        self.ax.set_xlim(lims)
        self.ax.set_xlabel(f'dev. in $ (at least 98% of distr., {perc_non_zero}% non-zero values)')
        self.ax.set_ylabel('cumulative probability')
        self.ax.grid()    

    def compare_net_inc(self, ax, alpha=0.5):
        self.ax = ax

        for group, marker in zip(self.l_groups, self.l_markers):
            self.df = self.data.copy()
            self.group = group
            self.marker = marker
            
            if group != 'all':
                self.create_condition(group)
                self.drop_hholds()

            inc_srd, inc_bdsps = self.d_income[self.income] 
            meas_srd, meas_bdsps = self.d_measures[self.measure]
            if self.fam_income and self.by_family:
                inc = self.df.groupby('ind_econ_fam')[[inc_srd, inc_bdsps]].agg('sum')
                meas = self.df.groupby('ind_econ_fam')[[meas_srd, meas_bdsps]].agg('sum')

            elif self.fam_income and not self.by_family:
                inc = self.df.groupby('ind_econ_fam')[[inc_srd, inc_bdsps]].transform('sum')
                meas = self.df[[meas_srd, meas_bdsps]]

            elif not self.fam_income and not self.by_family:
                inc = self.df[[inc_srd, inc_bdsps]]
                meas = self.df[[meas_srd, meas_bdsps]]

            self.ax.scatter(inc[inc_srd], meas[meas_srd], label='srd', marker='o',
                            alpha=alpha)
            self.ax.scatter(inc[inc_bdsps], meas[meas_bdsps], label='bdsps', marker='*',
                            alpha=alpha)
            self.ax.legend() 
            ax.set_xlabel('net income')
            ax.set_xlim([0, self.upper_inc])
