# note: 

import pytest
from math import isclose

import sys
sys.path.append('/Users/pyann/Dropbox (CEDIA)/srd/Model')
from srd import tax, Person, Hhold, Dependent, covid

year = 2020

def test_not_eligible():
    p0 = Person(asset=1000)
    p1 = Person(asset=2600)
    hh = Hhold(p0, p1, prov='qc')

    tax_form = tax(year)
    tax_form.compute_ass(hh)

    assert p0.inc_social_ass == 0
    assert p1.inc_social_ass == 0

@pytest.mark.parametrize('earn, amount', [(1000, 12588),
                                          (10000 / 2, 6528.40)])
def test_couple(earn, amount):
    p0 = Person(asset=1000, earn=earn)
    p1 = Person(asset=1000, earn=earn)
    hh = Hhold(p0, p1, prov='qc')

    tax_form = tax(year)
    tax_form.compute_payroll(hh)
    tax_form.compute_ass(hh)
    contributions = sum([sum(p.payroll.values()) for p in hh.sp])

    for p in hh.sp:
        assert p.inc_social_ass == amount / 2

def test_exemption_couple():
    earn = (3600 - 100) /2
    p0 = Person(asset=1000, earn=earn)
    p1 = Person(asset=1000, earn=earn)
    hh = Hhold(p0, p1, prov='qc')

    tax_form = tax(year)
    tax_form.compute_payroll(hh)
    tax_form.compute_ass(hh)
    inc_social_below = p0.inc_social_ass

    earn = (3600 + 100) /2
    p0 = Person(asset=1000, earn=earn)
    p1 = Person(asset=1000, earn=earn)
    hh = Hhold(p0, p1, prov='qc')

    tax_form = tax(year)
    tax_form.compute_payroll(hh)
    tax_form.compute_ass(hh)
    inc_social_above = p0.inc_social_ass

    assert inc_social_below == 12588 / 2 > inc_social_above



