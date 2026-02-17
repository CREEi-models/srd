#!/usr/bin/env python3
"""Test script for barebones provincial tax calculations."""
import srd
from srd import Person, Hhold, provinces, federal, quebec, ontario
from srd.payroll import payroll

# Test loading all province forms
print("=== Test chargement des formulaires provinciaux ===")
for prov in provinces.PROVINCES:
    form = provinces.form(prov, 2023)
    print(f"{prov.upper()}: nrtc_base={form.nrtc_base}, nrtc_rate={form.nrtc_rate}, brackets={len(form.l_brackets)}")

print()

# Setup calculators (using 2022 for full models due to shelter file issue in 2023)
YEAR_FULL = 2022
YEAR_BARE = 2023
payroll_calc_full = payroll(YEAR_FULL)
payroll_calc_bare = payroll(YEAR_BARE)
fed_form_full = federal.form(YEAR_FULL)
fed_form_bare = federal.form(YEAR_BARE)

# Compare full vs barebones for QC
print(f"=== Comparaison QC: modèle complet ({YEAR_FULL}) vs barebones ({YEAR_BARE}) ===")
p1 = Person(age=45, earn=75000)
hh1 = Hhold(p1, prov='qc')
payroll_calc_full.compute(hh1)
fed_form_full.file(hh1)
quebec.form(YEAR_FULL).file(hh1)
print(f"QC complet ({YEAR_FULL}):   {p1.prov_return['net_tax_liability']:.2f} $")

p2 = Person(age=45, earn=75000)
hh2 = Hhold(p2, prov='qc')
payroll_calc_bare.compute(hh2)
fed_form_bare.file(hh2)
provinces.form('qc', YEAR_BARE).file(hh2)
print(f"QC barebones ({YEAR_BARE}): {p2.prov_return['net_tax_liability']:.2f} $")
print(f"Note: La différence inclut les crédits, contributions santé et variations annuelles")

print()

# Compare full vs barebones for ON
print(f"=== Comparaison ON: modèle complet ({YEAR_FULL}) vs barebones ({YEAR_BARE}) ===")
p3 = Person(age=45, earn=75000)
hh3 = Hhold(p3, prov='on')
payroll_calc_full.compute(hh3)
fed_form_full.file(hh3)
ontario.form(YEAR_FULL).file(hh3)
print(f"ON complet ({YEAR_FULL}):   {p3.prov_return['net_tax_liability']:.2f} $")

p4 = Person(age=45, earn=75000)
hh4 = Hhold(p4, prov='on')
payroll_calc_bare.compute(hh4)
fed_form_bare.file(hh4)
provinces.form('on', YEAR_BARE).file(hh4)
print(f"ON barebones ({YEAR_BARE}): {p4.prov_return['net_tax_liability']:.2f} $")
print(f"Note: La différence inclut la surtaxe, crédits et variations annuelles")

print()

# Compare all provinces (barebones)
print(f"=== Comparaison impôt provincial barebones {YEAR_BARE} (revenu 75000$) ===")
for prov in provinces.PROVINCES:
    p_test = Person(age=45, earn=75000)
    hh_test = Hhold(p_test, prov='qc')
    payroll_calc_bare.compute(hh_test)
    fed_form_bare.file(hh_test)
    prov_form = provinces.form(prov, YEAR_BARE)
    prov_form.file(hh_test)
    print(f"{prov.upper()}: {p_test.prov_return['net_tax_liability']:,.2f} $")

