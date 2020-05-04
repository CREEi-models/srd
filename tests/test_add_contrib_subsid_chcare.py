import pytest
from math import isclose

import sys
sys.path.append('/Users/pyann/Dropbox (CEDIA)/srd/Model')
import srd
from srd import quebec

qc_form = quebec.form(2016)

@pytest.mark.parametrize('days1, days2', [(0, 0), (100, 0), (100, 100), (200, 0),
                                          (200, 100)])
def test_ndays(days1, days2):

    earn = 70e3
    p0 = srd.Person(age=45, earn=earn)
    hh0 = srd.Hhold(p0, prov='qc')

    p1 =srd.Person(age=45, ndays_chcare_k1=days1, ndays_chcare_k2=days2, earn=earn)
    hh1 = srd.Hhold(p1, prov='qc')
    amount = days1 * 0.70 + days2 * 0.70 / 2

    qc_form.file(hh0)
    qc_form.file(hh1)

    assert p1.prov_return['gross_tax_liability'] - p0.prov_return['gross_tax_liability'] == amount

@pytest.mark.parametrize('days1, days2', [(0, 0), (100, 0), (100, 100), (200, 0),
                                          (200, 100)])
def test_ndays_rich(days1, days2):
    earn = 200e3
    p0 = srd.Person(age=45, earn=earn)
    hh0 = srd.Hhold(p0, prov='qc')

    p1 =srd.Person(age=45, ndays_chcare_k1=days1, ndays_chcare_k2=days2, earn=earn)
    hh1 = srd.Hhold(p1, prov='qc')
    amount = days1 * (0.70 + 12.45) + days2 * (0.70 + 12.45) / 2

    qc_form.file(hh0)
    qc_form.file(hh1)
    contrib = p1.prov_return['gross_tax_liability'] - p0.prov_return['gross_tax_liability']

    assert  isclose(contrib, amount)

@pytest.mark.parametrize('days1, days2', [(0, 0), (100, 0), (100, 100), (200, 0),
                                          (200, 100)])
def test_ndays_100(days1, days2):
    earn = 100e3
    p0 = srd.Person(age=45, earn=earn)
    hh0 = srd.Hhold(p0, prov='qc')

    p1 =srd.Person(age=45, ndays_chcare_k1=days1, ndays_chcare_k2=days2, earn=earn)
    hh1 = srd.Hhold(p1, prov='qc')

    qc_form.file(hh0)
    qc_form.file(hh1)
    contrib = p1.prov_return['gross_tax_liability'] - p0.prov_return['gross_tax_liability']

    fam_net_inc = sum([s.prov_return['net_income'] for s in hh1.sp])
    contrib_k1 = (fam_net_inc - 75820) * 0.039 / 260 + 0.70
    amount = days1 * contrib_k1 + days2 * contrib_k1 / 2

    assert  isclose(contrib, amount)

@pytest.mark.parametrize('days1, days2, s0, s1', [(0, 0, 1, 0), (0, 0, 0, 1),
                         (100, 0, 1, 0), (100, 0, 0, 1), (100, 0, 0.5, 0.5),
                         (100, 100, 1, 0), (100, 0, 0, 1), (100, 0, 0.5, 0.5)])
def test_shares(days1, days2, s0, s1):
    earn = 70e3 / 2
    p0_base = srd.Person(age=45, earn=earn)
    p1_base =srd.Person(age=45, earn=earn)
    hh_base = srd.Hhold(p0_base, p1_base, prov='qc')

    p0 =srd.Person(age=45, ndays_chcare_k1=s0*days1, ndays_chcare_k2=s0*days2, earn=earn)
    p1 =srd.Person(age=45, ndays_chcare_k1=s1*days1, ndays_chcare_k2=s1*days2, earn=earn)
    hh = srd.Hhold(p0, p1, prov='qc')
    amount = days1 * 0.70 + days2 * 0.70 / 2

    qc_form.file(hh_base)
    qc_form.file(hh)

    contrib0 = p0.prov_return['gross_tax_liability'] - p0_base.prov_return['gross_tax_liability']
    contrib1 = p1.prov_return['gross_tax_liability'] - p1_base.prov_return['gross_tax_liability']

    assert contrib0 == s0 * amount
    assert contrib1 == s1 * amount

def test_removal_2019():
    qc_form = quebec.form(2019)
    earn = 100e3
    p0 = srd.Person(age=45, earn=earn)
    hh0 = srd.Hhold(p0, prov='qc')

    p1 =srd.Person(age=45, ndays_chcare_k1=200, earn=earn)
    hh1 = srd.Hhold(p1, prov='qc')

    qc_form.file(hh0)
    qc_form.file(hh1)
    contrib = p1.prov_return['gross_tax_liability'] - p0.prov_return['gross_tax_liability']

    assert  contrib == 0