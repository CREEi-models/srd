import pytest
from math import isclose

import sys
sys.path.append('/Users/11259018/Dropbox (CEDIA)/srd/Model')
import srd
from srd import quebec

qc_form = quebec.form(2016)

@pytest.mark.parametrize('age, amount', [(0, 8000), (6, 8000), (12, 5000), 
                                         (16, 5000), (17, 0)])
def test_age_amount(age, amount):
    p = srd.Person(age=45, earn=0)
    hh = srd.Hhold(p, child_care_exp=8000, prov='qc')
    dep = srd.Dependent(age=age)
    hh.add_dependent(dep)
        
    qc_form.file(hh)
    
    assert qc_form.chcare(p, hh) == 0.75 * amount #0.75 rate for fam_inc=0

@pytest.mark.parametrize('nkids, amount', [(0, 0), (1, 9000), (2, 2*9000)])
def test_number_young_kids_amount(nkids, amount):
    p = srd.Person(age=45, earn=0)
    hh = srd.Hhold(p, child_care_exp=100e3, prov='qc')
    for i in range(nkids):
        dep = srd.Dependent(age=5)
        hh.add_dependent(dep)
        
    qc_form.file(hh)
    
    assert qc_form.chcare(p, hh) == 0.75 * amount #0.75 rate for fam_inc=0

@pytest.mark.parametrize('inc, rate', [(0, 0.75), (10e3, 0.75), (35e3, 0.74),
                                        (50e3, 0.63), (100e3, 0.57)])
def test_earn_amount(inc, rate):
    p = srd.Person(age=45, othtax=inc)
    hh = srd.Hhold(p, child_care_exp=10e3, prov='qc')
    dep = srd.Dependent(age=5)
    hh.add_dependent(dep)
    amount = 9000
        
    qc_form.file(hh)
    
    assert qc_form.chcare(p, hh) == rate * amount

