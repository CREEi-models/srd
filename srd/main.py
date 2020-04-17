import sys
sys.path.append('/Users/11259018/Dropbox (CEDIA)/srd/Model')

import srd
from srd import federal, quebec

fed_form = federal.form(2016)
qc_form = quebec.form(2020)

jean = srd.Person(age=45,earn=50e3, disabled=True)
pauline = srd.Person(age=70,earn=25e3)
hh = srd.Hhold(jean,pauline,prov='qc')
child = srd.Dependent(age=0)
hh.add_dependent(child)

fed_form.file(hh)
qc_form.file(hh)

print(jean.fed_return)
print(jean.prov_return)

