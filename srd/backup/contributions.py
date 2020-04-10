import importlib
from srd import cpp
from srd import tools
importlib.reload(tools)

class Contrib:
    def __init__(self, path_params, year):
        tools.add_params_as_attr(self, path_params +'/others/contributions.csv')
        self.year = year
        self.QPP_rules = cpp.rules(qpp=True)
        self.CPP_rules = cpp.rules(qpp=False)

    def file(self, hh):
        for p in hh.sp:
            self.get_EI_contrib(p, hh)
            p.QPIP_contrib = 0
            if hh.prov == 'qc':
                self.get_QPIP_contrib(p, hh)               
            self.get_CPP_contrib(p, hh)

    def get_EI_contrib(self, p, hh):
        """Employment Insurance"""       
        rate = self.rate_EI_qc if hh.prov == 'qc' else self.rate_EI
        p.EI_contrib = rate * min(p.inc_earn, self.max_earn_EI)

    def get_QPIP_contrib(self, p, hh):
        """Quebec Parental Insurance Plan
        (contributions first deducted from wages,
        then from self-employed earnings)"""
        if p.inc_earn + p.inc_self_earn <= self.qualifying_threshold_QPIP:
            p.QPIP_contrib = 0
            return
        if p.inc_earn <= self.max_QPIP_earn:
            p.QPIP_contrib = self.rate_QPIP_earn * p.inc_earn + \
                self.rate_QPIP_selfemp_earn * min(p.inc_self_earn, self.max_QPIP_earn - p.inc_earn)
        else:
            p.QPIP_contrib = self.rate_QPIP_earn * self.max_QPIP_earn

    def get_CPP_contrib(self, p, hh):
        rules = self.QPP_rules if hh.prov == 'qc' else self.CPP_rules
        if (p.age < self.min_age_CPP) | (p.age > self.max_age_CPP):
             p.CPP_contrib = 0
        else:
            acc = cpp.account(byear=self.year - p.age, rules=rules)
            acc.MakeContrib(year=self.year, earn=p.inc_earn)
            hist = acc.history[p.age - self.min_age_CPP]
            p.CPP_contrib = hist.contrib + hist.contrib_s1 + hist.contrib_s2   