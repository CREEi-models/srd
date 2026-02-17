"""
Page du profil TEMI (taux effectif marginal d'imposition).
Permet de faire varier un champ de revenu et de visualiser le TEMI.
"""
import io
import pandas as pd
import streamlit as st
from srd.ui.strings import t
from srd.ui.components.person_form import render_person_form
from srd.ui.components.dependent_form import render_dependent_form
from srd.ui.components.hhold_form import render_hhold_form
from srd.ui.utils.srd_runner import compute_emtr_profile

# Champs Person que l'utilisateur peut faire varier
VARY_FIELDS = {
    "earn": "emtr_vary_earn",
    "self_earn": "emtr_vary_self_earn",
    "rpp": "emtr_vary_rpp",
    "cpp": "emtr_vary_cpp",
    "inc_rrsp": "emtr_vary_inc_rrsp",
}


def render(prov, year):
    """
    Affiche la page du profil TEMI.

    Parameters
    ----------
    prov : str
        Code de province selectionne dans le sidebar
    year : int
        Annee fiscale selectionnee dans le sidebar
    """
    st.header(t("emtr_title"))
    st.caption(t("emtr_note"))

    # Couple toggle
    is_couple = st.checkbox(t("couple_toggle"), key="ep_is_couple")

    # Person forms with "ep" prefix to avoid collision with manual mode
    if is_couple:
        tab_labels = [t("tab_person1"), t("tab_person2")]
    else:
        tab_labels = [t("tab_person1")]

    tabs = st.tabs(tab_labels)
    with tabs[0]:
        p1_kwargs = render_person_form("ep1")

    if is_couple:
        with tabs[1]:
            p2_kwargs = render_person_form("ep2")
    else:
        p2_kwargs = None

    st.divider()

    # Dependents
    dep_kwargs_list = render_dependent_form(prefix="ep_")

    st.divider()

    # Household
    hhold_kwargs = render_hhold_form(prefix="ep_")

    st.divider()

    # EMTR configuration
    st.subheader(t("emtr_config"))

    field_keys = list(VARY_FIELDS.keys())
    field_labels = [t(VARY_FIELDS[k]) for k in field_keys]
    col_field, col_min, col_max, col_step = st.columns(4)

    with col_field:
        field_idx = st.selectbox(
            t("emtr_vary_field"),
            range(len(field_keys)),
            format_func=lambda i: field_labels[i],
            key="ep_vary_field_idx",
        )
        vary_field = field_keys[field_idx]

    with col_min:
        min_val = st.number_input(
            t("emtr_min"),
            value=0,
            min_value=0,
            step=5000,
            key="ep_min_val",
        )

    with col_max:
        max_val = st.number_input(
            t("emtr_max"),
            value=100000,
            min_value=0,
            step=5000,
            key="ep_max_val",
        )

    with col_step:
        step = st.number_input(
            t("emtr_step"),
            value=5000,
            min_value=500,
            step=500,
            key="ep_step_val",
        )

    st.divider()

    # Compute button
    if st.button(t("emtr_btn_compute"), type="primary", use_container_width=True):
        if max_val <= min_val:
            st.error("Le maximum doit etre superieur au minimum.")
            return

        with st.spinner("Calcul en cours..."):
            try:
                df = compute_emtr_profile(
                    p1_kwargs, p2_kwargs, dep_kwargs_list, hhold_kwargs,
                    prov, year, vary_field, min_val, max_val, step,
                )
                st.session_state["ep_results"] = df
                st.session_state["ep_vary_field_name"] = vary_field
            except Exception as e:
                st.error(str(e))
                return

    # Display results
    if "ep_results" in st.session_state and st.session_state["ep_results"] is not None:
        df = st.session_state["ep_results"]
        vf = st.session_state.get("ep_vary_field_name", "earn")

        # Chart: EMTR curve
        st.subheader(t("emtr_chart_title"))
        chart_df = df.set_index(vf)
        emtr_pct = chart_df["emtr"] * 100
        emtr_pct.name = "TEMI (%)"
        st.line_chart(emtr_pct)

        # Display table
        display_df = df.rename(columns={
            vf: t("emtr_col_value"),
            "fam_disp_inc": t("emtr_col_disp_inc"),
            "emtr": t("emtr_col_emtr"),
        })
        display_df[t("emtr_col_emtr")] = (display_df[t("emtr_col_emtr")] * 100).round(2)
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Download buttons
        col_csv, col_xlsx = st.columns(2)
        with col_csv:
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                t("emtr_download_csv"),
                data=csv_data,
                file_name="emtr_profile.csv",
                mime="text/csv",
            )
        with col_xlsx:
            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False, engine="openpyxl")
            excel_buffer.seek(0)
            st.download_button(
                t("emtr_download_xlsx"),
                data=excel_buffer,
                file_name="emtr_profile.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
