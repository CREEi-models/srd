import pytest
from math import isclose

import sys
sys.path.append('/Users/pyann/Dropbox (CEDIA)/srd/Model')
import srd
from srd import quebec

qc_form = quebec.form(2016)

@pytest.mark.parametrize('nkids, net_inc', [(0, 18500), (1, 23800), (2, 27000)])
def test_cond_true_10_12_14(nkids, net_inc):
    p = srd.Person(age=45)
    hh = srd.Hhold(p, prov='qc')
    for _ in range(nkids):
        k = srd.Dependent(age=12)
        hh.add_dependent(k)

    qc_form.file(hh)
    p.prov_return['net_income'] = net_inc

    assert qc_form.health_contrib(p, hh) == 0

@pytest.mark.parametrize('nkids, net_inc', [(0, 19000), (1, 24000), (2, 28000)])
def test_cond_false_10_12_14(nkids, net_inc):
    p = srd.Person(age=45)
    hh = srd.Hhold(p, prov='qc')
    for _ in range(nkids):
        k = srd.Dependent(age=12)
        hh.add_dependent(k)

    qc_form.file(hh)
    p.prov_return['net_income'] = net_inc

    assert qc_form.health_contrib(p, hh) > 0

@pytest.mark.parametrize('nkids, net_inc', [(0, 23800), (1, 27000), (2, 29900)])
def test_cond_true_16_18_20(nkids, net_inc):
    p0 = srd.Person(age=45)
    p1 = srd.Person(age=45)
    hh = srd.Hhold(p0, p1, prov='qc')
    for _ in range(nkids):
        k = srd.Dependent(age=12)
        hh.add_dependent(k)

    qc_form.file(hh)
    p0.prov_return['net_income'] = net_inc

    assert qc_form.health_contrib(p0, hh) == 0

@pytest.mark.parametrize('nkids, net_inc', [(0, 24000), (1, 28000), (2, 30000)])
def test_cond_true_16_18_20(nkids, net_inc):
    p0 = srd.Person(age=45)
    p1 = srd.Person(age=45)
    hh = srd.Hhold(p0, p1, prov='qc')
    for _ in range(nkids):
        k = srd.Dependent(age=12)
        hh.add_dependent(k)

    qc_form.file(hh)
    p0.prov_return['net_income'] = net_inc

    assert qc_form.health_contrib(p0, hh) > 0

@pytest.mark.parametrize('inc_gis, amount', [(9300, 0), (9200, 50)])
def test_cond27(inc_gis, amount):
    p = srd.Person(age=78)
    hh = srd.Hhold(p, prov='qc')

    qc_form.file(hh)
    p.inc_gis = inc_gis
    p.prov_return['net_income'] = 41e3

    assert qc_form.health_contrib(p, hh) == amount

@pytest.mark.parametrize('inc_gis, amount', [(5850, 0), (5800, 50)])
def test_cond28(inc_gis, amount):
    p0 = srd.Person(age=78)
    p1 = srd.Person(age=78)
    hh = srd.Hhold(p0, p1, prov='qc')

    qc_form.file(hh)
    p0.inc_gis = inc_gis
    p0.prov_return['net_income'] = 41e3

    assert qc_form.health_contrib(p0, hh) == amount

@pytest.mark.parametrize('inc_gis, amount', [(5400, 0), (5300, 50)])
def test_cond29(inc_gis, amount):
    p0 = srd.Person(age=78)
    p1 = srd.Person(age=62)
    hh = srd.Hhold(p0, p1, prov='qc')

    qc_form.file(hh)
    p0.inc_gis = inc_gis
    p0.prov_return['net_income'] = 41e3

    assert qc_form.health_contrib(p0, hh) == amount

@pytest.mark.parametrize('inc_gis, amount', [(8700, 0), (8600, 50)])
def test_cond31(inc_gis, amount):
    p0 = srd.Person(age=78)
    p1 = srd.Person(age=59)
    hh = srd.Hhold(p0, p1, prov='qc')

    qc_form.file(hh)
    p0.inc_gis = inc_gis
    p0.prov_return['net_income'] = 41e3

    assert qc_form.health_contrib(p0, hh) == amount

@pytest.mark.parametrize('net_income, amount', [(18570, 0), (41e3, 50),
                         (41265, 50), (134e3, 175), (200e3, 1000)])
def test_amount(net_income, amount):
    p = srd.Person(age=70, earn=50e3)
    hh = srd.Hhold(p, prov='qc')

    qc_form.file(hh)
    p.prov_return['net_income'] = net_income

    assert qc_form.health_contrib(p, hh) == amount
