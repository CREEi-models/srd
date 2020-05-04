import pytest
from math import isclose

import sys
sys.path.append('/Users/pyann/Dropbox (CEDIA)/srd/Model')
import srd
from srd import oas

year = 2016


@pytest.mark.parametrize('age, inc_oas', [(58, 0), (62, 0), (70, 7000)])
def test_age_oas(age, inc_oas):
    p = srd.Person(age=70)
    hh = srd.Hhold(p, prov='qc')
    p = hh.sp[0]
    p.age = age

    oas_program = oas.program(year)
    oas_program.file(hh)

    assert isclose(p.inc_oas, inc_oas, rel_tol=0.1)

@pytest.mark.parametrize('net_inc, inc_oas', [(60000, 7000), (80000, 5000),
                                              (150000, 0)])
def test_net_inc_oas(net_inc, inc_oas):
    p = srd.Person(age=70)
    hh = srd.Hhold(p, prov='qc')
    p = hh.sp[0]
    p.net_inc = net_inc

    oas_program = oas.program(year)
    oas_program.file(hh)

    assert isclose(p.inc_oas, inc_oas, rel_tol=0.1)

@pytest.mark.parametrize('inc_non_work, inc_gis', [(0, 10000), (10000, 4000),
                                              (20000, 0)])
def test_inc_non_work_inc_gis(inc_non_work, inc_gis):
    p = srd.Person(age=70, othtax=inc_non_work)
    hh = srd.Hhold(p, prov='qc')

    oas_program = oas.program(year)
    oas_program.file(hh)

    assert isclose(p.inc_gis, inc_gis, rel_tol=0.1)

@pytest.mark.parametrize('age, allow_surv', [(58, 0), (62, 15000), (67, 0)])
def test_age_surv_allow(age, allow_surv):
    p = srd.Person(age=70, widow=True)
    p.net_inc = 0
    p.age = age
    hh = srd.Hhold(p, prov='qc')

    oas_program = oas.program(year)
    oas_program.file(hh)

    assert isclose(p.allow_surv, allow_surv, rel_tol=0.2)

@pytest.mark.parametrize('widow, allow_surv', [(False, 0), (True, 15000)])
def test_widow_surv_allow(widow, allow_surv):
    p = srd.Person(age=70)
    hh = srd.Hhold(p, prov='qc')
    p = hh.sp[0]
    p.net_inc = 0
    p.age = 62
    p.widow = widow

    oas_program = oas.program(year)
    oas_program.file(hh)

    assert isclose(p.allow_surv, allow_surv, rel_tol=0.2)