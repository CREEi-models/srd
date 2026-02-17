"""
Page du calculateur manuel.
Permet de remplir un formulaire et calculer les impots pour un cas individuel.
"""
import streamlit as st
from srd.ui.strings import t
from srd.ui.components.person_form import render_person_form
from srd.ui.components.dependent_form import render_dependent_form
from srd.ui.components.hhold_form import render_hhold_form
from srd.ui.components.results_display import render_results
from srd.ui.utils.srd_runner import run_calculation


def render(prov, year):
    """
    Affiche la page du calculateur manuel.

    Parameters
    ----------
    prov : str
        Code de province selectionne dans le sidebar
    year : int
        Annee fiscale selectionnee dans le sidebar
    """
    st.header(t("manual_title"))

    # Couple toggle
    is_couple = st.checkbox(t("couple_toggle"), key="is_couple")

    # Person forms — always render inside tabs so widget keys stay in a
    # stable container context when the couple checkbox is toggled.
    if is_couple:
        tab_labels = [t("tab_person1"), t("tab_person2")]
    else:
        tab_labels = [t("tab_person1")]

    tabs = st.tabs(tab_labels)
    with tabs[0]:
        p1_kwargs = render_person_form("p1")

    if is_couple:
        with tabs[1]:
            p2_kwargs = render_person_form("p2")
    else:
        p2_kwargs = None

    st.divider()

    # Dependents
    dep_kwargs_list = render_dependent_form()

    st.divider()

    # Household
    hhold_kwargs = render_hhold_form()

    st.divider()

    # Compute button
    if st.button(t("btn_compute"), type="primary", use_container_width=True):
        with st.spinner("Calcul en cours..."):
            hh, emtr, errors = run_calculation(
                p1_kwargs, p2_kwargs, dep_kwargs_list, hhold_kwargs, prov, year
            )
        if errors:
            for err in errors:
                st.error(t("error_computation").format(msg=err))
        else:
            st.session_state["results_hh"] = hh
            st.session_state["results_emtr"] = emtr

    # Display results
    if "results_hh" in st.session_state and st.session_state["results_hh"] is not None:
        render_results(st.session_state["results_hh"],
                       emtr=st.session_state.get("results_emtr"))
