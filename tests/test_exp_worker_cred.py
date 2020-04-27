import pytest
from math import isclose

import sys
sys.path.append('/Users/pyann/Dropbox (CEDIA)/srd/Model')
import srd
from srd import quebec

# I use https://cffp.recherche.usherbrooke.ca/outils-ressources/guide-mesures-fiscales/credit-impot-prolongation-carriere/
# since they don't seem to adjust for taxable income (lines 37 and 38, grille de calcul),
# we add some non-work income to avoid a reduction

@pytest.mark.parametrize('age, amount', [(59, 0), (60, 1500), (64, 1500),
                                        (65, 1650), (70, 1650)])
def test_age(age, amount):
    p = srd.Person(age=age, earn=30e3, othtax=10e3)
    hh = srd.Hhold(p, prov='qc')

    qc_form = quebec.form(2019)
    qc_form.file(hh)

    assert isclose(qc_form.get_exp_worker_cred(p), amount, abs_tol=1)

@pytest.mark.parametrize('work_inc, amount', [(5000, 0), (20e3, 1500),
                         (34610, 1500), (64610, 0), (49610, 750)])
def test_work_inc_63(work_inc, amount):
    p = srd.Person(age=63, earn=work_inc, othtax=10e3)
    hh = srd.Hhold(p, prov='qc')

    qc_form = quebec.form(2019)
    qc_form.file(hh)

    assert isclose(qc_form.get_exp_worker_cred(p), amount, abs_tol=1)

@pytest.mark.parametrize('work_inc, amount', [(5000, 0), (20e3, 1650),
                         (34610, 1650), (67610, 0), ((34610+67610)/2, 825)])
def test_work_inc_66(work_inc, amount):
    p = srd.Person(age=66, earn=work_inc, othtax=20e3)
    hh = srd.Hhold(p, prov='qc')

    qc_form = quebec.form(2019)
    qc_form.file(hh)

    assert isclose(qc_form.get_exp_worker_cred(p), amount, abs_tol=1)
