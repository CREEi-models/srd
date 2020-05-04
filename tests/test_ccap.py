import pytest
from math import isclose

import sys
sys.path.append('/Users/pyann/Dropbox (CEDIA)/srd/Model')
import srd
from srd import quebec

qc_form = quebec.form(2016)

def test_no_kid_no_refund():

    p0 = srd.Person(age=45, earn=0)
    p1 = srd.Person(age=45, earn=0)
    hh = srd.Hhold(p0, p1, prov='qc')

    qc_form.file(hh)

    assert p0.prov_return['refund_credits'] == 0
    assert p1.prov_return['refund_credits'] == 0


@pytest.mark.parametrize('kids, refund', [(0, 0), (1, 2392 + 839),
                                          (3, 2392 + 2*1195 + 839),
                                          (5, 2392 + 2*1195 + 2*1793 + 839)])
def test_monoparental(kids, refund):
    p = srd.Person(age=45, earn=0)
    hh = srd.Hhold(p, prov='qc')
    for i in range(kids):
        dep = srd.Dependent(age=3)
        hh.add_dependent(dep)

    qc_form.file(hh)

    assert p.prov_return['refund_credits'] == refund


@pytest.mark.parametrize('male0, male1, share0, share1', [(True, True, .5, .5),
                         (True, False, 0, 1), (False, True, 1, 0),
                         (False, False, .5, .5)])
def test_benefit_woman(male0, male1, share0, share1):
    refund = 2392
    p0 = srd.Person(age=45, male=male0, earn=0)
    p1 = srd.Person(age=45, male=male1, earn=0)
    hh = srd.Hhold(p0, p1, prov='qc')
    dep = srd.Dependent(age=17)
    hh.add_dependent(dep)

    qc_form.file(hh)

    assert p0.prov_return['refund_credits'] == share0 * refund
    assert p1.prov_return['refund_credits'] == share1 * refund


@pytest.mark.parametrize('earn, refund', [(0, 2392 + 839), (35e3, 2392 + 839),
                                          (85e3, 2392 + 839 - 2000)])
def test_clawback(earn, refund):
    p0 = srd.Person(age=45, earn=earn)
    hh = srd.Hhold(p0, prov='ab') # not qc to avoid qc abatment
    dep = srd.Dependent(age=17)
    hh.add_dependent(dep)

    qc_form.file(hh)

    assert isclose(p0.fed_return['refund_credits'], refund, abs_tol=100)

@pytest.mark.parametrize('children, earn, refund',
                         [(1, 100e3, 671), (2, 97e3, 2392 + 1195 - 2000),
                          (5, 97e3, 2392 + 2*1195 + 2*1793 - 2000)])
def test_clawback(children, earn, refund):
    p0 = srd.Person(age=45, earn=earn)
    p1 = srd.Person(age=45, male=False, earn=0)
    hh = srd.Hhold(p0, p1, prov='qc')
    dep = srd.Dependent(age=17)
    for i in range(children):
        hh.add_dependent(dep)

    qc_form.file(hh)

    assert p0.prov_return['refund_credits'] == 0
    assert isclose(p1.prov_return['refund_credits'], refund, abs_tol=100)