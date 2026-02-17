"""
Utilitaires pour le traitement par lot (batch).
Chargement de fichiers, mapping de colonnes, execution batch.
"""
import pandas as pd
import streamlit as st
from srd import Person, Hhold, Dependent, tax
from srd.ui.config import FULL_PROVINCES, ALL_PERSON_PARAMS, ALL_DEPENDENT_PARAMS, ALL_HHOLD_PARAMS
from srd.ui.utils.formatters import safe_value

EMTR_DELTA = 1000.0


def load_file(uploaded_file):
    """
    Charge un fichier telecharge en DataFrame.

    Parameters
    ----------
    uploaded_file : UploadedFile
        Fichier telecharge via st.file_uploader

    Returns
    -------
    pd.DataFrame
    """
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    elif name.endswith(".xlsx"):
        return pd.read_excel(uploaded_file)
    elif name.endswith(".dta"):
        return pd.read_stata(uploaded_file)
    else:
        raise ValueError(f"Format non supporte: {name}")


def get_mappable_attributes():
    """
    Retourne la liste des attributs SRD disponibles pour le mapping.

    Returns
    -------
    list[str]
        Liste triee des noms de parametres
    """
    attrs = list(ALL_PERSON_PARAMS)
    return sorted(set(attrs))


def get_mappable_hhold_attributes():
    """Retourne les attributs menage mappables."""
    return list(ALL_HHOLD_PARAMS)


def build_person_from_row(row, col_mapping, person_prefix=""):
    """
    Construit les kwargs Person a partir d'une ligne et du mapping.

    Parameters
    ----------
    row : pd.Series
        Ligne du DataFrame
    col_mapping : dict
        Mapping {param_name: column_name} ou None si non assigne
    person_prefix : str
        Prefixe pour les colonnes du conjoint (ex: "sp_")

    Returns
    -------
    dict
        kwargs pour Person.__init__
    """
    kwargs = {}
    for param_name in ALL_PERSON_PARAMS:
        key = f"{person_prefix}{param_name}" if person_prefix else param_name
        col = col_mapping.get(key)
        if col and col in row.index:
            val = row[col]
            if pd.notna(val):
                kwargs[param_name] = val
    return kwargs


def build_dependents_from_row(row, dep_config):
    """
    Construit une liste de Dependent a partir d'une ligne selon le mode.

    Parameters
    ----------
    row : pd.Series
    dep_config : dict
        Configuration des dependants: mode, colonnes, etc.

    Returns
    -------
    list[Dependent]
    """
    mode = dep_config.get("mode", "none")

    if mode == "none":
        return []

    elif mode == "simple":
        n_col = dep_config.get("n_kids_col")
        age_col = dep_config.get("kid_age_col")
        if not n_col or n_col not in row.index:
            return []
        n_kids = int(row[n_col]) if pd.notna(row[n_col]) else 0
        kid_age = int(row[age_col]) if (age_col and age_col in row.index and pd.notna(row[age_col])) else 5
        return [Dependent(age=kid_age) for _ in range(n_kids)]

    elif mode == "multi":
        deps = []
        age_cols = dep_config.get("age_cols", [])
        for col in age_cols:
            if col in row.index and pd.notna(row[col]):
                age = int(row[col])
                deps.append(Dependent(age=age))
        return deps

    return []


def extract_results(hh):
    """
    Extrait les resultats d'un menage calcule en un dictionnaire plat.

    Parameters
    ----------
    hh : Hhold
        Menage avec resultats

    Returns
    -------
    dict
        Resultats aplatis
    """
    result = {}
    p = hh.sp[0]

    result["fam_disp_inc"] = hh.fam_disp_inc
    result["fam_after_tax_inc"] = hh.fam_after_tax_inc

    # Federal return
    if p.fed_return:
        for key, val in p.fed_return.items():
            result[f"fed_{key}"] = val

    # Provincial return
    if p.prov_return:
        for key, val in p.prov_return.items():
            result[f"prov_{key}"] = val

    # Payroll
    if p.payroll:
        for key, val in p.payroll.items():
            result[f"payroll_{key}"] = val

    # Benefits
    result["inc_oas"] = p.inc_oas
    result["inc_gis"] = p.inc_gis
    result["inc_ei"] = p.inc_ei
    result["inc_sa"] = safe_value(p.inc_sa, 0)

    # Person 2 if couple
    if hh.couple:
        p2 = hh.sp[1]
        result["p2_disp_inc"] = p2.disp_inc
        if p2.fed_return:
            result["p2_fed_net_tax"] = p2.fed_return.get("net_tax_liability", 0)
        if p2.prov_return:
            result["p2_prov_net_tax"] = p2.prov_return.get("net_tax_liability", 0)

    return result


def run_batch(df, col_mapping, prov_default, year_default, couple_config, dep_config,
              prov_col=None, year_col=None):
    """
    Execute le calcul SRD sur toutes les lignes du DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Donnees d'entree
    col_mapping : dict
        Mapping des colonnes pour Person 1
    prov_default : str
        Province par defaut
    year_default : int
        Annee par defaut
    couple_config : dict
        Configuration couple
    dep_config : dict
        Configuration dependants
    prov_col : str or None
        Colonne province dans le fichier
    year_col : str or None
        Colonne annee dans le fichier

    Returns
    -------
    pd.DataFrame
        DataFrame avec colonnes originales + resultats
    """
    results = []
    n_success = 0
    n_errors = 0
    tax_cache = {}
    progress = st.progress(0)
    status = st.empty()

    for i, (idx, row) in enumerate(df.iterrows()):
        # Determine province and year
        prov = prov_default
        if prov_col and prov_col in row.index and pd.notna(row[prov_col]):
            prov = str(row[prov_col]).lower().strip()

        year = year_default
        if year_col and year_col in row.index and pd.notna(row[year_col]):
            year = int(row[year_col])

        try:
            # Build Person 1
            p1_kwargs = build_person_from_row(row, col_mapping)
            p1 = Person(**p1_kwargs)

            # Build Person 2 if couple
            p2 = None
            couple_mode = couple_config.get("mode", "single")
            if couple_mode == "column":
                flag_col = couple_config.get("flag_col")
                if flag_col and flag_col in row.index and row[flag_col]:
                    p2_mapping = couple_config.get("p2_mapping", {})
                    p2_kwargs = build_person_from_row(row, p2_mapping, person_prefix="")
                    if p2_kwargs:
                        p2 = Person(**p2_kwargs)
                    else:
                        p2 = Person()
            elif couple_mode == "attrs":
                p2_mapping = couple_config.get("p2_mapping", {})
                p2_kwargs = build_person_from_row(row, p2_mapping, person_prefix="")
                has_p2 = any(v is not None and (not isinstance(v, (int, float)) or v != 0)
                            for v in p2_kwargs.values())
                if has_p2:
                    p2 = Person(**p2_kwargs)

            # Build Hhold
            hh_kwargs = {}
            for param_name in ALL_HHOLD_PARAMS:
                col = col_mapping.get(f"hh_{param_name}")
                if col and col in row.index and pd.notna(row[col]):
                    hh_kwargs[param_name] = row[col]

            rent = hh_kwargs.pop("rent", 0) or 0
            prev_fam = hh_kwargs.pop("prev_fam_net_inc_prov", None)
            hh = Hhold(p1, p2, prov=prov, rent=rent, prev_fam_net_inc_prov=prev_fam)

            # Build dependents
            deps = build_dependents_from_row(row, dep_config)
            if deps:
                hh.add_dependent(*deps)

            # Get or create tax object
            cache_key = (year, prov)
            if cache_key not in tax_cache:
                iass = prov in FULL_PROVINCES
                tax_cache[cache_key] = tax(year, iass=iass)
            t = tax_cache[cache_key]

            t.compute(hh)
            base_disp = hh.fam_disp_inc
            row_result = extract_results(hh)

            # EMTR: re-run with person 1 earn + 1000$
            p1_high = dict(p1_kwargs)
            p1_high["earn"] = p1_high.get("earn", 0) + EMTR_DELTA
            p1h = Person(**p1_high)
            p2h = None
            if p2 is not None:
                p2h_kwargs = {}
                if couple_mode == "column":
                    p2h_kwargs = build_person_from_row(row, couple_config.get("p2_mapping", {}), person_prefix="")
                elif couple_mode == "attrs":
                    p2h_kwargs = build_person_from_row(row, couple_config.get("p2_mapping", {}), person_prefix="")
                p2h = Person(**p2h_kwargs) if p2h_kwargs else Person()
            hh_high = Hhold(p1h, p2h, prov=prov, rent=rent, prev_fam_net_inc_prov=prev_fam)
            deps_high = build_dependents_from_row(row, dep_config)
            if deps_high:
                hh_high.add_dependent(*deps_high)
            t.compute(hh_high)
            row_result["emtr"] = 1.0 - (hh_high.fam_disp_inc - base_disp) / EMTR_DELTA

            row_result["_error"] = ""
            n_success += 1

        except Exception as e:
            row_result = {"_error": str(e)}
            n_errors += 1

        results.append(row_result)
        progress.progress((i + 1) / len(df))
        status.text(f"{i + 1}/{len(df)} lignes traitees...")

    progress.empty()
    status.empty()

    result_df = pd.DataFrame(results)
    output = pd.concat([df.reset_index(drop=True), result_df], axis=1)

    return output, n_success, n_errors
