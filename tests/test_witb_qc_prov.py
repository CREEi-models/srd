import pytest
from math import isclose

import sys
sys.path.append('/Users/pyann/Dropbox (CEDIA)/srd/Model')
import srd
from srd import quebec

@pytest.mark.parametrize('work_inc, net_inc, amount', [(0, 0, 0), (2400, 2400, 0),
                                                       (20e3, 17722, 0),
                                                       (20e3, 16722, 100)])
def test_single(work_inc, net_inc, amount):
    p = srd.Person(age=45, earn=work_inc)
    hh = srd.Hhold(p, prov='qc')

    qc_form = quebec.form(2016)
    qc_form.file(hh)
    p.prov_return['net_income'] = net_inc
    print(p.__dict__)

    assert isclose(qc_form.witb(p, hh), amount, abs_tol=1)

@pytest.mark.parametrize('work_inc, net_inc, amount', [(0, 0, 0), (3600, 3600, 0),
                                                       (20e3, 27521, 0),
                                                       (20e3, 26521, 100)])
def test_couple(work_inc, net_inc, amount):
    p0 = srd.Person(age=45, earn=work_inc)
    p1 = srd.Person(age=45, earn=0)
    hh = srd.Hhold(p0, p1, prov='qc')

    qc_form = quebec.form(2016)
    qc_form.file(hh)
    p0.prov_return['net_income'] = net_inc

    assert isclose(qc_form.witb(p0, hh), amount, abs_tol=1)
    assert isclose(qc_form.witb(p1, hh), 0, abs_tol=1)



# test based on https://cffp.recherche.usherbrooke.ca/outils-ressources/guide-mesures-fiscales/credit-impot-remboursable-prime-travail/
# check if children are taken into account


@pytest.mark.parametrize('nkids, work_inc, net_inc, amount',
                         [(1, 0, 0, 0), (1, 2400, 2400, 0),
                          (1, 20e3, 0, 2496), (1, 40000, 36680, 0)])
def test_single_dep(nkids, work_inc, net_inc, amount):
    p0 = srd.Person(age=45, earn=work_inc)
    hh = srd.Hhold(p0, prov='qc')
    if nkids == 1:
        d = srd.Dependent(age=12)
        hh.add_dependent(d)

    qc_form = quebec.form(2019)
    qc_form.file(hh)
    p0.prov_return['net_income'] = net_inc

    assert isclose(qc_form.witb(p0, hh), amount, abs_tol=1)

@pytest.mark.parametrize('nkids, work_inc, net_inc, amount',
                         [(1, 0, 0, 0), (1, 3600, 3600, 0),
                          (1, 50e3, 0, 3246), (1, 50e3, 49044, 0)])
def test_couple_dep(nkids, work_inc, net_inc, amount):
    p0 = srd.Person(age=45, earn=work_inc)
    p1 = srd.Person(age=45, earn=0)
    hh = srd.Hhold(p0, p1,prov='qc')
    if nkids == 1:
        d = srd.Dependent(age=12)
        hh.add_dependent(d)

    qc_form = quebec.form(2019)
    qc_form.file(hh)
    p0.prov_return['net_income'] = net_inc

    assert isclose(qc_form.witb(p0, hh), amount, abs_tol=1)