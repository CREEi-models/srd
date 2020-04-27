import sys
sys.path.append('/Users/pyann/Dropbox (CEDIA)/srd/Model')

import srd
from srd import federal, quebec

year=2016
fed_form = federal.form(year)
qc_form = quebec.form(year)

p0 = srd.Person(age=65, earn=40000)
p1 = srd.Person(age=65, earn=0)
hh = srd.Hhold(p0, p1, prov='qc')


fed_form.file(hh)
qc_form.file(hh)

print(p0.age, p0.prov_return['contributions'])


