import pytest
from math import isclose

import sys
sys.path.append('/Users/pyann/Dropbox (CEDIA)/srd/Model')
import srd
from srd import quebec

qc_form = quebec.form(2016)

@pytest.mark.parametrize('income, amount', [(0, 966), (33e3, 966), (51e3, 0),
                                            (34e3+(51e3-34e3)/2, 480),
                                            (100e3, 0)])
def test_single(income, amount):
    p = srd.Person(age=45, othtax=income)
    hh = srd.Hhold(p, prov='qc')

    qc_form.file(hh)

    assert isclose(qc_form.solidarity(p, hh), amount, abs_tol=50)


@pytest.mark.parametrize('income, amount', [(0, 1231), (33e3, 1231), (56e3, 0),
                                            (34e3+(56e3-34e3)/2, 620),
                                            (100e3, 0)])
def test_couple(income, amount):
    p0 = srd.Person(age=45, othtax=income/2)
    p1 = srd.Person(age=45, othtax=income/2)
    hh = srd.Hhold(p0, p1, prov='qc')

    qc_form.file(hh)

    assert isclose(qc_form.solidarity(p0, hh), amount/2, abs_tol=50)

@pytest.mark.parametrize('income, amount', [(0, 1200), (33e3, 1200), (55e3, 0),
                                            (34e3+(55e3-34e3)/2, 600),
                                            (100e3, 0)])
def test_single_2kids(income, amount):
    p = srd.Person(age=45, othtax=income)
    hh = srd.Hhold(p, prov='qc')
    d0 = srd.Dependent(age=12)
    d1 = srd.Dependent(age=12)
    hh.add_dependent(d0, d1)

    qc_form.file(hh)

    assert isclose(qc_form.solidarity(p, hh), amount, abs_tol=50)

