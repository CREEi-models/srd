import importlib
from math import isclose
import pytest
import hhold
import run
importlib.reload(hhold)
importlib.reload(run)

run = run.Run(year=2016)
run.create_calculators()


@pytest.mark.parametrize('prov, EI_contrib', [('qc', 152), ('on', 188)])
def test_prov_EI(prov, EI_contrib):
    p = hhold.Person(earn=10000)
    hh = hhold.Hhold(p, prov=prov)

    run.file(hh)
    
    assert isclose(hh.sp[0].EI_contrib, EI_contrib, rel_tol=0.01)

@pytest.mark.parametrize('inc_earn, EI_contrib', 
                         [(10000, 152), (80000, 50800*0.0152),
                        (100000, 50800*0.0152)])
def test_inc_earn_EI(inc_earn, EI_contrib):
    p = hhold.Person(earn=inc_earn)
    hh = hhold.Hhold(p, prov='qc')

    run.file(hh)
    
    assert isclose(hh.sp[0].EI_contrib, EI_contrib, rel_tol=0.01)

def test_not_qc_QPIP():
    p = hhold.Person(earn=10000)
    hh = hhold.Hhold(p, prov='on')

    run.file(hh)
    
    assert hh.sp[0].QPIP_contrib == 0

@pytest.mark.parametrize('inc_earn, inc_self_earn, QPIP_contrib', 
                         [(1000, 0, 0), (2001, 0, 0.00548*2000),
                         (0, 2001, 0.00973*2000)])
def test_earn_QPIP(inc_earn, inc_self_earn, QPIP_contrib):
    p = hhold.Person(earn=inc_earn, selfemp_earn= inc_self_earn)
    hh = hhold.Hhold(p, prov='qc')

    run.file(hh)
    
    assert isclose(hh.sp[0].QPIP_contrib, QPIP_contrib, rel_tol=0.01)

@pytest.mark.parametrize('inc_earn, inc_self_earn', [(80000, 20000), 
                         (100000, 10000)])
def test_max_QPIP(inc_earn, inc_self_earn):
    p = hhold.Person(earn=inc_earn, selfemp_earn= inc_self_earn)
    hh = hhold.Hhold(p, prov='qc')

    run.file(hh)
    
    assert isclose(hh.sp[0].QPIP_contrib, 0.00548*71500, rel_tol=0.01)

@pytest.mark.parametrize('age', [17, 70, 80])
def test_age_CPP(age):
    p = hhold.Person(earn=10000)
    p.age = age
    hh = hhold.Hhold(p, prov='qc')

    run.file(hh)
    
    assert hh.sp[0].CPP_contrib == 0

def test_prov_CPP():
    p = hhold.Person(age=50, earn=10000)
    hh_QC = hhold.Hhold(p, prov='qc')

    run.file(hh_QC)

    p = hhold.Person(age=50, earn=10000)
    hh_ON = hhold.Hhold(p, prov='on')

    run.file(hh_ON)
    
    assert hh_QC.sp[0].CPP_contrib > hh_ON.sp[0].CPP_contrib > 0