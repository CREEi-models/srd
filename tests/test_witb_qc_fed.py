import importlib
from math import isclose
import pytest
import hhold
import run
importlib.reload(hhold)
importlib.reload(run)

run = run.Run(year=2016)
run.create_calculators()

@pytest.mark.parametrize('earn, witb', [(1000, 0), (2400, 0), (16000, 825),
                                        (12000, 1650), (20300, 0), (21000, 0)])
def test_witb_single(earn, witb):
    p = hhold.Person(earn=earn)
    hh = hhold.Hhold(p, prov='qc')

    run.file(hh)

    assert isclose(p.witb, witb, abs_tol=50)

@pytest.mark.parametrize('earn, witb', [(1000, 0), (2400, 0), (14500, 500),
                                        (12135, 967), (16974, 0), (18000, 0)])
def test_witb_single_dep(earn, witb):
    p = hhold.Person(earn=earn)
    hh = hhold.Hhold(p, prov='qc')
    dependent = hhold.Dependent(age=12)
    hh.dep.append(dependent)

    run.file(hh)

    assert isclose(p.witb, witb, abs_tol=50)

@pytest.mark.parametrize('earn, witb', [(1000, 0), (3600, 0), (10000, 1300),
                                        (18000, 2580), (31434, 0), (32000, 0)])
def test_witb_couple(earn, witb):
    p0 = hhold.Person(earn=earn/2)
    p1 = hhold.Person(earn=earn/2)
    hh = hhold.Hhold(p0, second=p1, prov='qc')

    run.file(hh)

    assert isclose(p0.witb, witb, abs_tol=50)
    assert isclose(p1.witb, witb, abs_tol=50)

@pytest.mark.parametrize('earn, witb', [(1000, 0), (3600, 0), (21000, 500),
                                        (18000, 1007), (23718, 0), (24000, 0)])
def test_witb_couple_dep(earn, witb):
    p0 = hhold.Person(earn=earn/2)
    p1 = hhold.Person(earn=earn/2)
    hh = hhold.Hhold(p0, second=p1, prov='qc')
    dependent = hhold.Dependent(age=12)
    hh.dep.append(dependent)

    run.file(hh)

    assert isclose(p0.witb, witb, abs_tol=50)
    assert isclose(p1.witb, witb, abs_tol=50)