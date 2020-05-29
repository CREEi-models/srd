import sys
sys.path.append('/Users/pyann/Dropbox (CEDIA)/srd/Model')

import numpy as np
import matplotlib.pyplot as plt
import pickle
import time

import srd
from srd import tax, Person, Hhold, Dependent, covid, incentives

policy = covid.policy()
policy.shut_all_measures()
tax_form = tax(2020, policy=policy)

p0 = Person(asset=1000, earn=5000)
p1 = Person()
hh = Hhold(p0, p1, n_adults_in_hh=1, prov='qc')



print(hh.n_adults_in_hh)

tax_form.compute(hh)

print(p0.qc_single_cred)



# p0 = Person(age=25, earn=1000)
# p1 = Person(age=25, earn=1000)
# hh = Hhold(p0, p1, prov='qc')
# d = Dependent(age=3)
# hh.dep.append(d)

# tax_form.compute(hh)
# print(p0.__dict__)
# print(p1.__dict__)

# l_hh =[]

# for nkids in [0, 1, 2]:
#     p0 = Person(age=25, earn=8*4*40*13.10)
#     p1 = Person(age=25, earn=0)
#     hh = Hhold(p0, p1, prov='qc')
#     for k in range(nkids):
#         d = Dependent(age=3)
#         hh.dep.append(d)

#     tax_form.compute(hh)
#     print(p0.disp_inc, p1.disp_inc)
#     print(hh.fam_disp_inc)

#     l_hh.append(hh)

# l_vars = [vars(hh.sp[0]) for hh in l_hh]
# # print(l_vars)

# d ={}
# for var in l_vars[0]:
#     for i, _ in enumerate(l_vars):
#         val = l_vars[i][var]
#         if var not in d:
#             d[var] = [val]
#         else:
#             d[var].append(val)

# d_clean = {k: d[k] for k in d if d[k][0] != d[k][1]}
# d_res = {k: v for k, v in d_clean.items() if k in ['fed_chcare', 'fed_ccb', 'fed_gst_hst_credit', 'qc_chcare', 'qc_ccap', 'qc_solidarity']}

# print(d_res)




