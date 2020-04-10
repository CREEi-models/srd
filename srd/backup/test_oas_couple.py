import importlib
from math import isclose
import pytest
import hhold
import run
importlib.reload(hhold)
importlib.reload(run)

run = run.Run(year=2016)
run.create_calculators()


@pytest.mark.parametrize('age, inc_oas', [(58, 0), (62, 0), (70, 7000)])
def test_age_oas(age, inc_oas):
    p0 = hhold.Person(age=age)
    p1 = hhold.Person(age=age)
    hh = hhold.Hhold(p0, second=p1, prov='qc')
    
    run.file(hh)
    
    for p in hh.sp:
        assert isclose(p.inc_oas, inc_oas, rel_tol=0.1)

@pytest.mark.parametrize('net_inc, inc_oas', [(60000, 7000), (80000, 5000), 
                                              (150000, 0)])
def test_net_inc_oas(net_inc, inc_oas):
    p0 = hhold.Person(age=70)
    p1 = hhold.Person(age=70)
    for p in [p0, p1]:
        p.net_inc = net_inc
    hh = hhold.Hhold(p0, second=p1, prov='qc')
    
    run.file(hh)

    for p in hh.sp:
        assert isclose(p.inc_oas, inc_oas, rel_tol=0.1)

@pytest.mark.parametrize('inc_non_work, inc_gis', [(0, 6000), (10000, 2500),
                                              (20000, 0)])
def test_inc_non_work_inc_gis(inc_non_work, inc_gis):
    p0 = hhold.Person(age=70)
    p1 = hhold.Person(age=70)
    for p in [p0, p1]:
        p.inc_work
        p.inc_work = inc_non_work
    hh = hhold.Hhold(p0, second=p1, prov='qc')

    run.file(hh)
    
    assert isclose(p.inc_gis, inc_gis, rel_tol=0.1)

@pytest.mark.parametrize('age, allow_couple', [(58, 0), (62, 15000), (67, 0)])
def test_age_allow_couple(age, allow_couple):
    p0 = hhold.Person(age=70)
    p1 = hhold.Person()
    p1.age = age
    hh = hhold.Hhold(p0, second=p1, prov='qc')

    run.file(hh)
    assert isclose(p1.allow_couple, allow_couple, rel_tol=0.2)