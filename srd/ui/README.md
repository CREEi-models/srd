# SRD UI - Implementation Summary

## Overview

Streamlit web app with two features:
1. **Manual Calculator** -- fill a form, compute taxes, see detailed results
2. **Batch Mode** -- upload CSV/Excel/Stata, map columns to SRD attributes, run on all rows, download results

## How to Run

```bash
streamlit run srd/ui/app.py
```

Dependencies: `streamlit`, `openpyxl` (both already installed).

## File Structure

```
srd/ui/
├── app.py                          # Entry point, sidebar, page routing
├── strings.py                      # French strings dict (bilingual-ready via t(key))
├── config.py                       # Attribute metadata, province/year constants
├── components/
│   ├── person_form.py              # Renders ~30 Person fields in grouped expanders
│   ├── dependent_form.py           # Dynamic add/remove dependent children
│   ├── hhold_form.py               # Household-level fields (rent, prev income)
│   └── results_display.py          # Summary metrics + detailed per-person tables
├── pages/
│   ├── manual.py                   # Feature 1: form + compute + results
│   └── batch.py                    # Feature 2: upload, map, run, download
└── utils/
    ├── srd_runner.py               # Wraps SRD API with validation and caching
    ├── batch_processor.py          # File loading, column mapping, batch execution
    └── formatters.py               # Currency formatting helpers
```

## Architecture

```
Browser <-> Streamlit (Python) <-> SRD (direct import)
```

No subprocess, no IPC, no JavaScript. The UI imports `srd` directly.

## Feature 1: Manual Calculator

### Layout
- **Sidebar**: province selector, year selector (filtered by province), page navigation
- **Main area**:
  - Couple toggle checkbox
  - Person tabs (1 or 2) with grouped expanders (demographics, employment, pension, deductions, etc.)
  - Dynamic dependents section (add/remove children)
  - Household section (rent, previous family income)
  - "Calculer" button
  - Results: 4 summary metrics + expandable per-person detail (federal, provincial, payroll, benefits)

### Person Fields (~30)
| Group | Fields |
|-------|--------|
| Demographics | age, male, disabled, widow, student, essential_worker, dep_senior, long_term_ss |
| Employment | earn, self_earn |
| Pension & investments | rpp, cpp, inc_rrsp, inc_rdsp, net_cap_gains, prev_cap_losses, cap_gains_exempt, div_elig, div_other_can |
| Other income | othtax, othntax |
| Deductions | con_rrsp, con_rdsp, con_non_rrsp, con_rpp, union_dues, donation, gift |
| Health & childcare | med_exp, ndays_chcare_k1, ndays_chcare_k2 |
| Other | asset, years_can, prev_inc_work, prop_tax, pub_drug_insurance, tax_shield, home_support_cost, home_access_cost, oas_years_post, months_ei, cdsg, cdsb |

### Results Display
- **Summary row**: fam_disp_inc, fam_after_tax_inc, total_tax, total_payroll
- **Per-person tabs**: federal return table, provincial return table, payroll table, benefits table

## Feature 2: Batch Mode

### Steps
1. **Upload**: CSV, Excel (.xlsx), or Stata (.dta)
2. **Preview**: first 10 rows
3. **Province/year source**: use sidebar value or map to a file column
4. **Column mapping**: for each SRD attribute, select a file column (auto-maps matching names)
5. **Couple config**: all singles / flag column / map person 2 attributes
6. **Dependent config**: none / simple (n_kids + age) / multi-column (kid1_age, kid2_age, ...)
7. **Run**: progress bar, per-row error handling
8. **Results**: preview table + download as CSV or Excel

### Output Columns
Original input columns + fam_disp_inc, fam_after_tax_inc, fed_* (full federal return), prov_* (full provincial return), payroll_*, inc_oas, inc_gis, inc_ei, inc_sa, _error

## Key Design Decisions

- **i18n**: all user-visible strings live in `strings.py` as `{"key": {"fr": "..."}}`. Adding English = add `"en": "..."` to each entry + a language toggle in sidebar.
- **Config-driven forms**: `config.py` defines each field's metadata (name, label key, type, default, min_value). The form component iterates over this list -- no hardcoded rendering.
- **Session state**: widget values keyed with prefixes (`p1_age`, `p2_earn`, `dep_0_age`). Results stored in `st.session_state` to survive Streamlit reruns.
- **Province-aware**: barebones provinces use `iass=False` (no social assistance model). Year selector filtered by province.
- **rent vs prop_tax**: `rent` is a Hhold parameter; `prop_tax` is a Person parameter.
- **tax() caching**: `@st.cache_resource` avoids reloading CSV params on every rerun.
- **Batch error handling**: per-row try/except, errors in `_error` column, summary count at top.

## Verification

Test case: age=45, earn=50000, prov=qc, year=2023 produces `fam_disp_inc = 38,848.62 $`.
