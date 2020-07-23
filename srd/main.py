path_py = '/Users/pyann/Dropbox (CEDIA)/srd/Model'

import sys
sys.path.append(path_py)
import numpy as np
import matplotlib.pyplot as plt

from srd import tax, incentives, Person, Hhold, Dependent, federal
from srd.covid import policy


policy = policy()
policy.shut_all_measures()
policy.iei = True

for year in range(2016, 2021):

    tax_form = tax(year)

    p0 = Person(earn=20000, age=32)
    p1 = Person(earn=100000, age=40)
    hh = Hhold(p0, p1, prov='qc')
    d1 = Dependent(age=17)
    d2 = Dependent(age=18)
    hh.add_dependent(d1, d2)

    tax_form.compute(hh)
    print(year, ' :', hh.fam_disp_inc)

# for year in range(2016, 2021):

#     print(year)

#     julia1 = Person(age=70, rpp=20e3, inc_rrsp=20e3)
#     jules1 = Person(age=65, cpp=5000)
#     hh = Hhold(julia1, jules1, prov='qc')
#     james = Dependent(age=5)
#     jean = Dependent(age=12)
#     joseph =Dependent(age=18)
#     hh.add_dependent(james, jean, joseph)

#     tax_form = tax(year)
#     tax_form.compute(hh)

#     print(vars(hh))




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