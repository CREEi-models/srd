import pytest
from math import isclose

import sys
sys.path.append('/Users/pyann/Dropbox (CEDIA)/srd/Model')
import srd
from srd import oas

year = 2016

def test_not_min_years_can():
    p0 = srd.Person(age=70, years_can=9)
    hh = srd.Hhold(p0, prov='qc')

    oas_program = oas.program(year)
    oas_program.file(hh)
    p = hh.sp[0]

    assert p.inc_oas == 0
    assert p.inc_gis == 0
    assert p.allow_surv == 0
    assert p.allow_couple == 0


@pytest.mark.parametrize('age, prog', [(58, 'nothing'), (62, 'allowance'),
                                       (70, 'oas+gis')])
def test_single(age, prog):
    p0 = srd.Person(age=age, widow=True)
    hh = srd.Hhold(p0, prov='qc')

    oas_program = oas.program(year)
    oas_program.file(hh)
    p = hh.sp[0]

    if prog == 'nothing':
        assert p.inc_oas == 0
        assert p.inc_gis == 0
        assert p.allow_surv == 0
        assert p.allow_couple == 0

    if prog == 'allowance':
        assert p.inc_oas == 0
        assert p.inc_gis == 0
        assert p.allow_surv > 0
        assert p.allow_couple == 0

    if prog == 'oas+gis':
        assert p.inc_oas > 0
        assert p.inc_gis > 0
        assert p.allow_surv == 0
        assert p.allow_couple == 0

@pytest.mark.parametrize('age0, age1, prog', [(58, 62, 'nothing'),
                                              (62, 70, 'allowance'),
                                              (69, 70, 'oas+gis')])
def test_couple(age0, age1, prog):
    p0 = srd.Person(age=age0, widow=True)
    p1 = srd.Person(age=age1, widow=True)
    hh = srd.Hhold(p0, p1, prov='qc')

    oas_program = oas.program(year)
    oas_program.file(hh)
    p0, p1 = hh.sp

    if prog == 'nothing':
        assert p0.inc_oas == p1.inc_oas == 0
        assert p0.inc_gis == p1.inc_gis == 0
        assert p0.allow_surv == p1.allow_surv == 0
        assert p0.allow_couple == p1.allow_couple == 0

    if prog == 'allowance':
        assert p0.inc_oas == 0 < p1.inc_oas
        assert p0.inc_gis == 0 < p1.inc_gis
        assert p0.allow_surv == p1.allow_surv == 0
        assert p0.allow_couple > p1.allow_couple == 0

    if prog == 'oas+gis':
        assert p0.inc_oas == p1.inc_oas > 0
        assert p0.inc_gis == p1.inc_gis > 0
        assert p0.allow_surv == p1.allow_surv == 0
        assert p0.allow_couple == p1.allow_couple == 0
