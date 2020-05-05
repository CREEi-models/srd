import sys
sys.path.append('/Users/pyann/Dropbox (CEDIA)/srd/Model')
import pickle
import time

import srd
from srd import tax

tax_form = tax(2020)

with open('bdsps/l_hh.pkl', "rb") as f:
    l_hh = pickle.load(f)
print(len(l_hh))

start = time.time()

for i, hh in enumerate(l_hh):
    print(i)
    tax_form.compute(hh)

print(time.time() - start)
