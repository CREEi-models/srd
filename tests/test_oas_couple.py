import pytest
from math import isclose

import sys
sys.path.append('/Users/pyann/Dropbox (CEDIA)/srd/Model')
import srd
from srd import oas

year = 2019

@pytest.mark.parametrize('age, inc_oas', [(58, 0), (62, 0), (70, 7000)])
def test_age_oas(age, inc_oas):
    p0 = srd.Person(age=age)
    p1 = srd.Person(age=age)
    hh = srd.Hhold(p0, second=p1, prov='qc')

    oas_program = oas.program(year)
    oas_program.file(hh)

    for p in hh.sp:
        assert isclose(p.inc_oas, inc_oas, rel_tol=0.1)

@pytest.mark.parametrize('net_inc, inc_oas', [(60000, 7000), (80000, 6000),
                                              (150000, 0)])
def test_net_inc_oas(net_inc, inc_oas):
    p0 = srd.Person(age=70, othtax=net_inc)
    p1 = srd.Person(age=70, othtax=net_inc)
    hh = srd.Hhold(p0, second=p1, prov='qc')

    oas_program = oas.program(year)
    oas_program.file(hh)

    for p in hh.sp:
        assert isclose(p.inc_oas, inc_oas, rel_tol=0.1)

@pytest.mark.parametrize('inc_non_work, inc_gis', [(0, 6000), (10000, 12*95.41),
                                              (20000, 0)])
def test_inc_non_work_inc_gis(inc_non_work, inc_gis):
    p0 = srd.Person(age=70, othtax=inc_non_work)
    p1 = srd.Person(age=70, othtax=inc_non_work)
    hh = srd.Hhold(p0, second=p1, prov='qc')

    oas_program = oas.program(year)
    oas_program.file(hh)

    assert isclose(p0.inc_gis, inc_gis, rel_tol=0.1)

@pytest.mark.parametrize('age, allow_couple', [(58, 0), (62, 15000), (67, 0)])
def test_age_allow_couple(age, allow_couple):
    p0 = srd.Person(age=70)
    p1 = srd.Person()
    p1.age = age
    hh = srd.Hhold(p0, second=p1, prov='qc')

    oas_program = oas.program(year)
    oas_program.file(hh)

    assert isclose(p1.allow_couple, allow_couple, rel_tol=0.2)