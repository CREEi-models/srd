import importlib
import run
import hhold
importlib.reload(run)
importlib.reload(hhold)

# création de personnes
p0 = hhold.Person(age=75)
p1 = hhold.Person(age=70)

# création d'un ménage avec ces deux personnes


for p in [p0, p1]:
    p.inc_work
    p.inc_work = 60000
try:
    hh = hhold.Hhold(p0, second=p1, prov='qc')
except:
    hh = hhold.Hhold(p0, prov='qc')

run = run.Run(year=2016)
run.create_calculators()

run.file(hh)

print(f'hh net income: {hh.fam_net_inc}')

for p in hh.sp:
    print(f'age: {p.age}, oas: {p.inc_oas}, gis: {p.inc_gis}', 
          f'allow_couple {p.allow_couple}, allow_surv {p.allow_surv}')

