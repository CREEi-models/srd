import pytest
from math import isclose

import sys
sys.path.append('/Users/pyann/Dropbox (CEDIA)/srd/Model')
import srd
from srd import federal

@pytest.mark.parametrize('earn, witb', [(1000, 0), (2400, 0), (16000, 825),
                                        (12000, 1650), (20300, 0), (21000, 0)])
def test_witb_single(earn, witb):
    p = srd.Person(earn=earn)
    hh = srd.Hhold(p, prov='qc')

    fed_form = federal.form(2016)
    fed_form.file(hh)

    assert isclose(fed_form.witb(p, hh), witb, abs_tol=50)

@pytest.mark.parametrize('earn, witb', [(1000, 0), (2400, 0), (14500, 500),
                                        (12135, 967), (16974, 0), (18000, 0)])
def test_witb_single_dep(earn, witb):
    p = srd.Person(earn=earn)
    hh = srd.Hhold(p, prov='qc')
    dependent = srd.Dependent(age=12)
    hh.dep.append(dependent)

    fed_form = federal.form(2016)
    fed_form.file(hh)

    assert isclose(fed_form.witb(p, hh), witb, abs_tol=50)

@pytest.mark.parametrize('earn, witb', [(1000, 0), (3600, 0), (10000, 1300),
                                        (18000, 2580), (31434, 0), (32000, 0)])
def test_witb_couple(earn, witb):
    p0 = srd.Person(earn=earn/2)
    p1 = srd.Person(earn=earn/2)
    hh = srd.Hhold(p0, second=p1, prov='qc')

    fed_form = federal.form(2016)
    fed_form.file(hh)

    assert isclose(fed_form.witb(p0, hh), witb/2, abs_tol=50)
    assert isclose(fed_form.witb(p1, hh), witb/2, abs_tol=50)


@pytest.mark.parametrize('earn, witb', [(1000, 0), (3600, 0), (21000, 500),
                                        (18000, 1007), (23718, 0), (24000, 0)])
def test_witb_couple_dep(earn, witb):
    p0 = srd.Person(earn=earn/2)
    p1 = srd.Person(earn=earn/2)
    hh = srd.Hhold(p0, second=p1, prov='qc')
    dependent = srd.Dependent(age=12)
    hh.dep.append(dependent)

    fed_form = federal.form(2016)
    fed_form.file(hh)

    assert isclose(fed_form.witb(p0, hh), witb/2, abs_tol=50)
    assert isclose(fed_form.witb(p1, hh), witb/2, abs_tol=50)

@pytest.mark.parametrize('earn, witb', [(1000, 0), (1200, 0), (20e3, 530),
                                        (30e3, 0), (20332+1000, 530 - 200)])
def test_witbds_single(earn, witb):
    p = srd.Person(earn=earn, disabled=True)
    hh = srd.Hhold(p, prov='qc')

    fed_form = federal.form(2016)
    fed_form.file(hh)

    assert isclose(fed_form.witbds(p, hh), witb, abs_tol=10)


@pytest.mark.parametrize('earn, witb', [(1000, 0), (1200, 0), (16974, 530),
                                        (25e3, 0), (16974+1000, 530-200)])
def test_witbds_single_dep(earn, witb):
    p = srd.Person(earn=earn, disabled=True)
    hh = srd.Hhold(p, prov='qc')
    dependent = srd.Dependent(age=12)
    hh.dep.append(dependent)

    fed_form = federal.form(2016)
    fed_form.file(hh)

    assert isclose(fed_form.witbds(p, hh), witb, abs_tol=50)

@pytest.mark.parametrize('earn, witb', [(1000, 0), (1200, 0), (31434, 530),
                                        (34084, 0), (31434+1000, 530-200)])
def test_witbds_couple(earn, witb):
    p0 = srd.Person(earn=earn/2, disabled=True)
    p1 = srd.Person(earn=earn/2, disabled=False)
    hh = srd.Hhold(p0, second=p1, prov='qc')

    fed_form = federal.form(2016)
    fed_form.file(hh)

    assert isclose(fed_form.witbds(p0, hh), witb, abs_tol=50)
    assert isclose(fed_form.witbds(p1, hh), 0, abs_tol=50)

@pytest.mark.parametrize('earn, witb', [(1000, 0), (1200, 0), (31434, 530),
                                        (36734, 0), (31434+1000, 530-100)])
def test_witbds_dis_couple(earn, witb):
    p0 = srd.Person(earn=earn/2, disabled=True)
    p1 = srd.Person(earn=earn/2, disabled=True)
    hh = srd.Hhold(p0, second=p1, prov='qc')

    fed_form = federal.form(2016)
    fed_form.file(hh)

    assert isclose(fed_form.witbds(p0, hh), witb, abs_tol=10)
    assert isclose(fed_form.witbds(p1, hh), witb, abs_tol=10)

@pytest.mark.parametrize('earn, witb', [(1000, 0), (1200, 0), (23718, 530),
                                        (26369, 0), (23718+1000, 530-200)])
def test_witbds_couple_dep(earn, witb):
    p0 = srd.Person(earn=earn/2, disabled=True)
    p1 = srd.Person(earn=earn/2, disabled=False)
    hh = srd.Hhold(p0, second=p1, prov='qc')
    dependent = srd.Dependent(age=12)
    hh.dep.append(dependent)

    fed_form = federal.form(2016)
    fed_form.file(hh)

    assert isclose(fed_form.witbds(p0, hh), witb, abs_tol=10)
    assert isclose(fed_form.witbds(p1, hh), 0, abs_tol=10)

@pytest.mark.parametrize('earn, witb', [(1000, 0), (1200, 0), (23718, 530),
                                        (29019, 0), (23718+1000, 530-100)])
def test_witbds_dis_couple_dep(earn, witb):
    p0 = srd.Person(earn=earn/2, disabled=True)
    p1 = srd.Person(earn=earn/2, disabled=True)
    hh = srd.Hhold(p0, second=p1, prov='qc')
    dependent = srd.Dependent(age=12)
    hh.dep.append(dependent)

    fed_form = federal.form(2016)
    fed_form.file(hh)

    assert isclose(fed_form.witbds(p0, hh), witb, abs_tol=10)
    assert isclose(fed_form.witbds(p1, hh), witb, abs_tol=10)

