"""
Interface entre l'UI et le moteur SRD.
Construit les objets Person/Hhold/Dependent et execute le calcul.
"""
import pandas as pd
import streamlit as st
from srd import Person, Hhold, Dependent, tax
from srd.ui.config import FULL_PROVINCES


@st.cache_resource
def get_tax_object(year, prov):
    """
    Cree et cache un objet tax() pour eviter de recharger les parametres CSV.
    Pour les provinces sans modele d'aide sociale, iass=False.
    """
    iass = prov in FULL_PROVINCES
    return tax(year, iass=iass)


def validate_person_kwargs(kwargs):
    """
    Valide les parametres d'une personne. Retourne une liste d'erreurs.
    """
    errors = []
    age = kwargs.get("age", 50)
    if not (0 <= age <= 120):
        errors.append("L'age doit etre entre 0 et 120")
    return errors


def build_person(kwargs):
    """Construit un objet Person a partir des kwargs du formulaire."""
    clean = {}
    for k, v in kwargs.items():
        if v is not None:
            clean[k] = v
    return Person(**clean)


def build_dependent(kwargs):
    """Construit un objet Dependent a partir des kwargs du formulaire."""
    return Dependent(**{k: v for k, v in kwargs.items() if v is not None})


def build_hhold(p1, p2, prov, hhold_kwargs, dep_list):
    """Construit un objet Hhold avec les personnes, dependants et parametres."""
    rent = hhold_kwargs.get("rent", 0) or 0
    prev_fam = hhold_kwargs.get("prev_fam_net_inc_prov", None)
    hh = Hhold(p1, p2, prov=prov, rent=rent, prev_fam_net_inc_prov=prev_fam)
    if dep_list:
        hh.add_dependent(*dep_list)
    return hh


def run_calculation(p1_kwargs, p2_kwargs, dep_kwargs_list, hhold_kwargs, prov, year):
    """
    Execute un calcul SRD complet.

    Returns
    -------
    tuple: (hhold, emtr, errors)
        hhold est l'objet Hhold avec resultats,
        emtr est le taux effectif marginal d'imposition (float ou None),
        errors est une liste de messages.
    """
    errors = validate_person_kwargs(p1_kwargs)
    if p2_kwargs:
        errors.extend(validate_person_kwargs(p2_kwargs))
    if errors:
        return None, None, errors

    try:
        p1 = build_person(p1_kwargs)
        p2 = build_person(p2_kwargs) if p2_kwargs else None
        deps = [build_dependent(d) for d in dep_kwargs_list] if dep_kwargs_list else []
        hh = build_hhold(p1, p2, prov, hhold_kwargs, deps)
        t = get_tax_object(year, prov)
        t.compute(hh)
        base_disp = hh.fam_disp_inc

        # EMTR: re-run with person 1 earning +1000$
        emtr = compute_emtr(p1_kwargs, p2_kwargs, dep_kwargs_list, hhold_kwargs,
                            prov, year, base_disp)

        return hh, emtr, []
    except Exception as e:
        return None, None, [str(e)]


EMTR_DELTA = 1000.0


def compute_emtr(p1_kwargs, p2_kwargs, dep_kwargs_list, hhold_kwargs,
                 prov, year, base_disp):
    """
    Calcule le taux effectif marginal d'imposition.

    EMTR = 1 - (disp_inc(earn + delta) - disp_inc(earn)) / delta

    Parameters
    ----------
    base_disp : float
        fam_disp_inc du cas de base

    Returns
    -------
    float
        EMTR entre 0 et 1 (ou >1 si clawbacks exceeding marginal income)
    """
    p1_high = dict(p1_kwargs)
    p1_high["earn"] = p1_high.get("earn", 0) + EMTR_DELTA

    p1 = build_person(p1_high)
    p2 = build_person(p2_kwargs) if p2_kwargs else None
    deps = [build_dependent(d) for d in dep_kwargs_list] if dep_kwargs_list else []
    hh = build_hhold(p1, p2, prov, hhold_kwargs, deps)
    t = get_tax_object(year, prov)
    t.compute(hh)

    high_disp = hh.fam_disp_inc
    emtr = 1.0 - (high_disp - base_disp) / EMTR_DELTA
    return emtr


def _run_single(p1_kwargs, p2_kwargs, dep_kwargs_list, hhold_kwargs, prov, year):
    """Execute un calcul SRD et retourne fam_disp_inc."""
    p1 = build_person(p1_kwargs)
    p2 = build_person(p2_kwargs) if p2_kwargs else None
    deps = [build_dependent(d) for d in dep_kwargs_list] if dep_kwargs_list else []
    hh = build_hhold(p1, p2, prov, hhold_kwargs, deps)
    t = get_tax_object(year, prov)
    t.compute(hh)
    return hh.fam_disp_inc


def compute_emtr_profile(p1_kwargs, p2_kwargs, dep_kwargs_list, hhold_kwargs,
                         prov, year, vary_field, min_val, max_val, step):
    """
    Calcule le TEMI pour chaque valeur du champ variable.

    Parameters
    ----------
    vary_field : str
        Nom du champ Person a faire varier (earn, self_earn, rpp, cpp, inc_rrsp)
    min_val, max_val, step : int
        Plage et increment

    Returns
    -------
    pd.DataFrame
        Colonnes: vary_field, fam_disp_inc, emtr
    """
    values = list(range(int(min_val), int(max_val) + 1, int(step)))
    results = []
    progress = st.progress(0)

    for i, val in enumerate(values):
        p1_base = dict(p1_kwargs)
        p1_base[vary_field] = float(val)
        base_disp = _run_single(p1_base, p2_kwargs, dep_kwargs_list,
                                hhold_kwargs, prov, year)

        p1_high = dict(p1_base)
        p1_high[vary_field] = float(val) + EMTR_DELTA
        high_disp = _run_single(p1_high, p2_kwargs, dep_kwargs_list,
                                hhold_kwargs, prov, year)

        emtr = 1.0 - (high_disp - base_disp) / EMTR_DELTA
        results.append({
            vary_field: val,
            "fam_disp_inc": round(base_disp, 2),
            "emtr": round(emtr, 4),
        })

        progress.progress((i + 1) / len(values))

    progress.empty()
    return pd.DataFrame(results)
