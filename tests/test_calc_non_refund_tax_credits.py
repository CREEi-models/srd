import pytest
from math import isclose

import sys
sys.path.append('/Users/11259018/Dropbox (CEDIA)/srd/Model')
import srd
from srd import federal

fed_form = federal.form(2020)

@pytest.mark.parametrize('earn, basic_amount', [(150e3, 13229), (151e3, 13229),
                         (214e3, 12298), (215e3, 12298),
                         ((150e3+214e3)/2, (13229+12298)/2)])
def test_basic_amount(earn, basic_amount):

    p = srd.Person(age=45, earn=earn)
    hh = srd.Hhold(p, prov='qc')
        
    fed_form.file(hh)
    
    assert isclose(p.fed_return['non_refund_credits'], 0.15*basic_amount, abs_tol=10)