"""
Composant d'affichage des resultats du calcul SRD.
Affiche un resume et des details par personne.
"""
import pandas as pd
import streamlit as st
from srd.ui.config import RETURN_KEYS, FED_EXTRA_KEYS, PAYROLL_KEYS, BENEFIT_ATTRS
from srd.ui.strings import t
from srd.ui.utils.formatters import fmt_currency, safe_value


def render_results(hh, emtr=None):
    """
    Affiche les resultats d'un calcul SRD.

    Parameters
    ----------
    hh : Hhold
        Menage avec resultats calcules
    emtr : float or None
        Taux effectif marginal d'imposition
    """
    st.header(t("results_title"))

    # Resume
    _render_summary(hh, emtr)

    st.divider()

    # Detail par personne
    for idx, person in enumerate(hh.sp):
        label = t("result_person_detail").format(n=idx + 1)
        with st.expander(label, expanded=(idx == 0)):
            _render_person_detail(person)


def _render_summary(hh, emtr=None):
    """Affiche les metriques principales."""
    total_tax = 0
    total_payroll = 0
    for p in hh.sp:
        if p.fed_return:
            total_tax += p.fed_return.get("net_tax_liability", 0)
        if p.prov_return:
            total_tax += p.prov_return.get("net_tax_liability", 0)
        if p.payroll:
            total_payroll += sum(p.payroll.values())

    cols = st.columns(5)
    cols[0].metric(t("result_fam_disp_inc"), fmt_currency(hh.fam_disp_inc))
    cols[1].metric(t("result_fam_after_tax"), fmt_currency(hh.fam_after_tax_inc))
    cols[2].metric(t("result_total_tax"), fmt_currency(total_tax))
    cols[3].metric(t("result_total_payroll"), fmt_currency(total_payroll))
    if emtr is not None:
        cols[4].metric(
            t("result_emtr"),
            f"{emtr * 100:.1f} %",
            help=t("result_emtr_help"),
        )
    else:
        cols[4].metric(t("result_emtr"), "N/A")


def _render_person_detail(person):
    """Affiche les details pour une personne."""
    tab_fed, tab_prov, tab_payroll, tab_benefits = st.tabs([
        t("result_fed_return"),
        t("result_prov_return"),
        t("result_payroll"),
        t("result_benefits"),
    ])

    with tab_fed:
        _render_return_table(person.fed_return, include_extra=True)

    with tab_prov:
        _render_return_table(person.prov_return, include_extra=False)

    with tab_payroll:
        _render_payroll_table(person.payroll)

    with tab_benefits:
        _render_benefits_table(person)


def _render_return_table(return_dict, include_extra=False):
    """Affiche un dictionnaire de declaration fiscale comme tableau."""
    if return_dict is None:
        st.info("Non calcule")
        return

    keys = RETURN_KEYS + (FED_EXTRA_KEYS if include_extra else [])
    rows = []
    for key in keys:
        label = t(f"ret_{key}")
        value = return_dict.get(key, 0)
        rows.append({"Element": label, "Montant ($)": fmt_currency(value)})

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def _render_payroll_table(payroll_dict):
    """Affiche les cotisations sociales."""
    if payroll_dict is None:
        st.info("Non calcule")
        return

    rows = []
    for key in PAYROLL_KEYS:
        label = t(f"pay_{key}")
        value = payroll_dict.get(key, 0)
        rows.append({"Element": label, "Montant ($)": fmt_currency(value)})

    total = sum(payroll_dict.values())
    rows.append({"Element": "Total", "Montant ($)": fmt_currency(total)})

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def _render_benefits_table(person):
    """Affiche les prestations recues."""
    rows = []
    for attr_name, string_key in BENEFIT_ATTRS:
        value = getattr(person, attr_name, 0)
        value = safe_value(value, 0)
        rows.append({"Prestation": t(string_key), "Montant ($)": fmt_currency(value)})

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
