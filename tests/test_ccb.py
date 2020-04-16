import pytest
from math import isclose

import sys
sys.path.append('/Users/11259018/Dropbox (CEDIA)/srd/Model')
import srd
from srd import federal

fed_form = federal.form(2019)

@pytest.mark.parametrize('age, refund', [(0, 6639), (5, 6639), (6, 5602), 
                                        (17, 5602), (18, 0), (45, 0)])
def test_age_refund(age, refund):
    p = srd.Person(age=45, earn=0)
    hh = srd.Hhold(p, prov='qc')
    dep = srd.Dependent(age=age)
    hh.add_dependent(dep)
        
    fed_form.file(hh)
    
    assert p.fed_return['refund_credits'] == refund

@pytest.mark.parametrize('children', [0, 1, 2, 4, 6])
def test_young_children(children):
    refund = 6639
    p = srd.Person(age=45, earn=0)
    hh = srd.Hhold(p, prov='qc')
    for i in range(children):
        dep = srd.Dependent(age=3)
        hh.add_dependent(dep)
    
    fed_form.file(hh)
    
    assert p.fed_return['refund_credits'] == children * refund

@pytest.mark.parametrize('children', [0, 1, 2, 4, 6])
def test_old_children(children):
    refund = 5602
    p = srd.Person(age=45, earn=0)
    hh = srd.Hhold(p, prov='qc')
    for i in range(children):
        dep = srd.Dependent(age=17)
        hh.add_dependent(dep)
    
    fed_form.file(hh)
    
    assert p.fed_return['refund_credits'] == children * refund

@pytest.mark.parametrize('male0, male1, share0, share1', [(True, True, .5, .5), 
                         (True, False, 0, 1), (False, True, 1, 0), 
                         (False, False, .5, .5)])
def test_benefit_woman(male0, male1, share0, share1):
    refund = 5602
    p0 = srd.Person(age=45, male=male0, earn=0)
    p1 = srd.Person(age=45, male=male1, earn=0)
    hh = srd.Hhold(p0, p1, prov='qc')
    dep = srd.Dependent(age=17)
    hh.add_dependent(dep)
    
    fed_form.file(hh)
    
    assert p0.fed_return['refund_credits'] == share0 * refund
    assert p1.fed_return['refund_credits'] == share1 * refund

@pytest.mark.parametrize('earn, refund', [(0, 5602), (31000, 5602),
                                          (160000, 0)])
def test_clawback(earn, refund):
    p0 = srd.Person(age=45, earn=earn)
    hh = srd.Hhold(p0, prov='ab') # not qc to avoid qc abatment
    dep = srd.Dependent(age=17)
    hh.add_dependent(dep)
    
    fed_form.file(hh)
    
    assert isclose(p0.fed_return['refund_credits'], refund, abs_tol=100)

@pytest.mark.parametrize('children, earn, rate', 
                         [(1, 32000, .07), (2, 32000, .135), (3, 32000, .19), 
                          (4, 32000, .23), (5, 32000, .23),
                          (1, 68000, .032), (2, 68000, .057), (3, 68000, .08), 
                          (4, 68000, .095), (5, 68000, .095)])
def test_clawback(children, earn, rate):
    p0 = srd.Person(age=45, earn=earn)
    hh = srd.Hhold(p0, prov='ab') # not qc to avoid qc abatment
    dep = srd.Dependent(age=17)
    for i in range(children):
        hh.add_dependent(dep)
    
    fed_form.file(hh)
    refund_credits0 = p0.fed_return['refund_credits']

    p0 = srd.Person(age=45, earn=earn+1)
    hh = srd.Hhold(p0, prov='ab') # not qc to avoid qc abatment
    dep = srd.Dependent(age=17)
    for i in range(children):
        hh.add_dependent(dep)
    
    fed_form.file(hh)
    refund_credits1 = p0.fed_return['refund_credits']
    
    assert isclose(refund_credits0 - rate, refund_credits1)