path_py = '/Users/pyann/Dropbox (CEDIA)/srd/Model'

import sys
sys.path.append(path_py)
import numpy as np
import matplotlib.pyplot as plt

from srd import tax, incentives, Person, Hhold, Dependent
from srd.covid import policy

for year in range(2016, 2021):

    tax_form = tax(year)

    p0 = Person(age=64, rpp=50e3,)
    p1 = Person(age=70, rpp=100e3)
    hh = Hhold(p0, p1, prov='qc')

    hh = tax_form.compute(hh, n_points=1)

    print(hh.fam_disp_inc)



# def main():
#     file = '/Users/pyann/Dropbox (CEDIA)/srd/notebooks/data/bdsps_hhold.pkl'
#     ref = incentives(case_mode=False, data_file=file, multiprocessing=False)
#     ref.set_hours(nh=11,maxh=40, dh=10, hours_full=35)
#     ref.set_wages(minwage=13.1)

#     # smaller dataframe:

#     ref.cases = ref.cases.iloc[:10, :]

#     # ei_measures = policy(icerb=False, icesb=False, iei=True)
#     # ei_tax_system = tax(2020, iass=True, policy=ei_measures)
#     # ref.set_tax_system(ei_tax_system)

#     covid_measures = policy()
#     covid_tax_system = tax(2020, iass=True, policy=covid_measures)
#     ref.set_tax_system(covid_tax_system)


#     print(ref.get_one_emtr(10))


# if __name__ == '__main__':
#     main()