path_py = '/Users/pyann/Dropbox (CEDIA)/srd/Model'

import sys
sys.path.append(path_py)
import numpy as np
import matplotlib.pyplot as plt

from srd import tax, incentives, Person, Hhold, Dependent
from srd.covid import policy

for year in range(2016, 2021):
    print(year)

    tax_form = tax(year)

    p0 = Person(age=50, earn = 40e3, med_exp=5000)
    p1 = Person(earn=10e3, med_exp=10000)
    d = Dependent(age=12, med_exp=1000)
    hh = Hhold(p0, p1, prov='qc')
    hh.dep.append(d)
    print([p.med_exp for p in hh.sp] + [d.med_exp for d in hh.dep])

    tax_form.compute(hh)
    print(vars(hh))



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