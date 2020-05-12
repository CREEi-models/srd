import pytest
from math import isclose

import sys
sys.path.append('/Users/pyann/Dropbox (CEDIA)/srd/Model')
from srd import tax, Person, Hhold, Dependent, covid

year = 2020

def test_increase_cbb_gst():
    tax_form = tax(2020)
    p = Person()
    hh = Hhold(p, prov='qc')
    d = Dependent(age=12)
    hh.dep.append(d)

    tax_form.compute(hh)

    gst_covid = p.fed_gst_hst_credit
    ccb_covid = p.fed_ccb

    policy = covid.policy()
    policy.shut_all_measures()
    tax_form = tax(2020, policy=policy)
    p = Person()
    hh = Hhold(p, prov='qc')
    d = Dependent(age=12)
    hh.dep.append(d)

    tax_form.compute(hh)

    gst = p.fed_gst_hst_credit
    ccb = p.fed_ccb

    assert gst_covid > gst
    assert ccb_covid == ccb + 300

def test_cerb():
    tax_form = tax(2020)
    p = Person(earn=6000, months_cerb=2)
    hh = Hhold(p, prov='qc')

    tax_form.compute(hh)

    assert p.covid['cerb'] == 4000

def test_no_cerb():
    tax_form = tax(2020)
    p = Person(earn=4000, months_cerb=2)
    hh = Hhold(p, prov='qc')

    tax_form.compute(hh)

    assert p.covid['cerb'] == 0

def test_base_cesb():
    tax_form = tax(2020)
    p = Person(earn=6000, months_cesb=2)
    hh = Hhold(p, prov='qc')

    tax_form.compute(hh)

    assert p.covid['cerb'] == 0
    assert p.covid['cesb'] == 2500

def test_supp_disabled_cesb():
    tax_form = tax(2020)
    p = Person(earn=6000, months_cesb=2, disabled=True)
    hh = Hhold(p, prov='qc')

    tax_form.compute(hh)

    assert p.covid['cerb'] == 0
    assert p.covid['cesb'] == 4000

def test_no_cesb():
    tax_form = tax(2020)
    p = Person(earn=4000, months_cesb=0)
    hh = Hhold(p, prov='qc')

    tax_form.compute(hh)

    assert p.covid['cesb'] == 0

def test_supp_dep_cesb():
    tax_form = tax(2020)
    p = Person(months_cesb=1)
    hh = Hhold(p, prov='qc')
    dep = Dependent(age=12)
    hh.dep.append(dep)

    tax_form.compute(hh)

    assert p.covid['cesb'] == 2000

def test_couple_cesb_disabled():
    tax_form = tax(2020)
    p0 = Person(months_cesb=1)
    p1 = Person(months_cesb=3, disabled=True)

    hh = Hhold(p0, p1, prov='qc')

    tax_form.compute(hh)

    assert p0.covid['cesb'] == 1250
    assert p1.covid['cesb'] == 6000

def test_couple_cesb_dep():

    tax_form = tax(2020)
    p0 = Person(months_cesb=1)
    p1 = Person(months_cesb=2)
    hh = Hhold(p0, p1, prov='qc')
    dep = Dependent(age=12)
    hh.dep.append(dep)

    tax_form.compute(hh)

    assert p0.covid['cesb'] == 1250 + 750 / 2
    assert p1.covid['cesb'] == 2 * (1250 + 750 / 2)

def test_couple_cesb_dep_disabled():

    tax_form = tax(2020)
    p0 = Person(months_cesb=1, disabled=True)
    p1 = Person(months_cesb=2)
    hh = Hhold(p0, p1, prov='qc')
    dep = Dependent(age=12)
    hh.dep.append(dep)

    tax_form.compute(hh)

    assert p0.covid['cesb'] == 2000
    assert p1.covid['cesb'] == 4000

def test_iprew():
    tax_form = tax(2020)
    p = Person(essential_worker=True, earn=6000)
    hh = Hhold(p, prov='qc')

    tax_form.compute(hh)

    assert p.covid['cesb'] == 0
    assert p.covid['iprew'] == 1600

def test_no_iprew():
    tax_form = tax(2020)
    p = Person(essential_worker=False, earn=6000)
    hh = Hhold(p, prov='qc')

    tax_form.compute(hh)

    assert p.covid['iprew'] == 0

    p = Person(essential_worker=True, earn=4000)
    hh = Hhold(p, prov='qc')

    tax_form.compute(hh)

    assert p.covid['iprew'] == 0

    p = Person(essential_worker=True, earn=6000, othntax=30000)
    hh = Hhold(p, prov='qc')

    tax_form.compute(hh)

    assert p.covid['iprew'] == 0
