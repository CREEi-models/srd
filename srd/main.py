import sys
sys.path.append('/Users/pyann/Dropbox (CEDIA)/srd/Model')

import srd
from srd import tax

def test_year(year):
    p0 = srd.Person(age=62, widow=False)
    p1 = srd.Person(age=66)
    hh = srd.Hhold(p0, p1, child_care_exp=10e3, prov='qc')
    for i in range(0):
        dep = srd.Dependent(age=5)
        hh.dep.append(dep)

    tax_form = tax(year)
    tax_form.compute(hh)

for year in range(2016, 2021):
    print(year)
    test_year(year)
