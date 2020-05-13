import sys
sys.path.append('/Users/pyann/Dropbox (CEDIA)/srd/Model')
import pickle
import time

import srd
from srd import tax, Person, Hhold, Dependent, covid

policy = covid.policy(icovid_gst=True)
# policy.shut_all_measures()
print(vars(policy))
tax_form = tax(2020, policy=policy)

p0 = Person(months_cesb=1)
earn = [3000] * 4 + [1000] * 8
p1 = Person(months_cesb=2, earn=earn, essential_worker=True)
hh = Hhold(p0, p1, prov='qc')
dep = Dependent(age=12)
hh.dep.append(dep)

tax_form.compute(hh)

print(p1.__dict__)
print(p1.inc_earn)
print(len(p1.inc_earn_month), p1.inc_earn_month)

