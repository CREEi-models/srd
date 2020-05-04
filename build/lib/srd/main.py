import sys
sys.path.append('/Users/pyann/Dropbox (CEDIA)/srd/Model')

import srd
from srd import federal, quebec

fed_form = federal.form(2016)
qc_form = quebec.form(2016)

# jean = srd.Person(age=45,earn=0, disabled=True)
# pauline = srd.Person(age=70, earn=0)
# hh = srd.Hhold(jean,prov='qc')
# k1 = srd.Dependent(age=5)
# k2 = srd.Dependent(age=10)
# hh.add_dependent(k1, k2)

p0 = srd.Person(age=45, earn=97e5)
p1 = srd.Person(age=45, male=False, earn=0)
hh = srd.Hhold(p0, prov='qc')
dep = srd.Dependent(age=17)
for i in range(3):
    hh.add_dependent(dep)

fed_form.file(hh)
qc_form.file(hh)

print(jean.prov_return)

