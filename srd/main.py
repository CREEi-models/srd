path_py = '/Users/pyann/Dropbox (CEDIA)/srd/Model'

import sys
sys.path.append(path_py)
import numpy as np
import matplotlib.pyplot as plt

from srd import tax, incentives, Person, Hhold, Dependent, federal
from srd.covid import policy    

year=2020
earn=10000

julia = Person(age=40, earn=earn, div_elig=100, div_other_can=200)
hh = Hhold(julia, prov='qc')
# james = Dependent(age=5)
# jean = Dependent(age=12)
# joseph = Dependent(age=18)
# hh.add_dependent(james, jean, joseph)



tax_form = tax(year)

print(vars(tax_form.prov['qc']))