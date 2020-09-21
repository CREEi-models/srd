path_py = '/Users/pyann/Dropbox (CEDIA)/srd/Model'

import sys
sys.path.append(path_py)
import numpy as np
import matplotlib.pyplot as plt

from srd import tax, incentives, Person, Hhold, Dependent, federal
from srd.covid import policy    

jean = Person(age=45, earn=40000)
jacques = Person(age=40, earn=50000)
jeanne = Dependent(age=4, child_care=10000)
joaquim = Dependent(age=8, child_care=8000)

hh = Hhold(jean, jacques, prov='on')

hh.add_dependent(jeanne, joaquim)


tax_form = tax(2020)
tax_form.compute(hh)

print(hh.fam_disp_inc)
