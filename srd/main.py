path_py = 'C:/Users/pyy/Dropbox (CEDIA)/srd/Model'
import sys
sys.path.insert(0, path_py)


import numpy as np

import matplotlib.pyplot as plt

from srd import tax, incentives, Person, Hhold, Dependent, federal  
import srd

jean = Person(age=62)
jacques = Person(age=68)

hh = Hhold(jean, jacques, prov='qc')

for year in range(2016, 2021):

    tax_form = tax(year)
    tax_form.compute(hh)
    
    print(year, hh.sp[0].allow_couple, hh.sp[0].inc_non_work,
          hh.sp[0].inc_tot, hh.fam_disp_inc)


