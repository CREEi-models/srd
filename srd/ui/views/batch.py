"""
Page du mode batch.
Permet de charger un fichier, mapper les colonnes et executer le SRD en lot.
"""
import io
import streamlit as st
import pandas as pd
from srd.ui.strings import t
from srd.ui.config import ALL_PERSON_PARAMS, ALL_HHOLD_PARAMS
from srd.ui.utils.batch_processor import load_file, get_mappable_attributes, run_batch


NONE_OPTION = "-- Non assigne --"


def render(prov, year):
    """
    Affiche la page du mode batch.

    Parameters
    ----------
    prov : str
        Province selectionnee dans le sidebar
    year : int
        Annee selectionnee dans le sidebar
    """
    st.header(t("batch_title"))

    # 1. File upload
    st.subheader(t("batch_upload"))
    uploaded_file = st.file_uploader(
        t("batch_upload_help"),
        type=["csv", "xlsx", "dta"],
        key="batch_file",
    )

    if uploaded_file is None:
        st.info(t("batch_upload_help"))
        return

    # Load data
    try:
        df = load_file(uploaded_file)
    except Exception as e:
        st.error(str(e))
        return

    # 2. Preview
    st.subheader(t("batch_preview"))
    st.caption(t("batch_preview_info").format(n=len(df), c=len(df.columns)))
    st.dataframe(df.head(10), use_container_width=True)

    columns = list(df.columns)
    options = [NONE_OPTION] + columns

    # 3. Province/Year source
    st.subheader(t("batch_config"))

    col_prov_src, col_year_src = st.columns(2)
    with col_prov_src:
        prov_source = st.radio(
            t("batch_prov_source"),
            [t("batch_prov_sidebar"), t("batch_prov_column")],
            key="batch_prov_source",
        )
        prov_col = None
        if prov_source == t("batch_prov_column"):
            prov_col = st.selectbox("Colonne province", columns, key="batch_prov_col")

    with col_year_src:
        year_source = st.radio(
            t("batch_year_source"),
            [t("batch_year_sidebar"), t("batch_year_column")],
            key="batch_year_source",
        )
        year_col = None
        if year_source == t("batch_year_column"):
            year_col = st.selectbox("Colonne annee", columns, key="batch_year_col")

    st.divider()

    # 4. Column mapping
    st.subheader(t("batch_mapping"))

    col_mapping = {}
    mappable = get_mappable_attributes()

    # Try auto-mapping: if a column name exactly matches a param name, pre-select it
    auto_map = {}
    col_lower = {c.lower().strip(): c for c in columns}
    for attr in mappable:
        if attr in col_lower:
            auto_map[attr] = col_lower[attr]

    st.caption(f"Attributs de la personne principale ({len(mappable)} disponibles)")
    n_cols_display = 3
    attr_cols = st.columns(n_cols_display)
    for i, attr in enumerate(mappable):
        with attr_cols[i % n_cols_display]:
            default_idx = 0
            if attr in auto_map:
                try:
                    default_idx = options.index(auto_map[attr])
                except ValueError:
                    default_idx = 0
            selected = st.selectbox(
                attr,
                options,
                index=default_idx,
                key=f"map_{attr}",
            )
            if selected != NONE_OPTION:
                col_mapping[attr] = selected

    # Hhold attributes
    st.caption("Attributs du menage")
    hh_cols = st.columns(n_cols_display)
    for i, param_name in enumerate(ALL_HHOLD_PARAMS):
        with hh_cols[i % n_cols_display]:
            default_idx = 0
            if param_name in col_lower:
                try:
                    default_idx = options.index(col_lower[param_name])
                except ValueError:
                    default_idx = 0
            selected = st.selectbox(
                f"hh: {param_name}",
                options,
                index=default_idx,
                key=f"map_hh_{param_name}",
            )
            if selected != NONE_OPTION:
                col_mapping[f"hh_{param_name}"] = selected

    st.divider()

    # 5. Couple config
    couple_mode_label = st.radio(
        t("batch_couple_mode"),
        [t("batch_couple_all_single"), t("batch_couple_column"), t("batch_couple_attrs")],
        key="batch_couple_mode",
    )

    couple_config = {"mode": "single"}
    if couple_mode_label == t("batch_couple_column"):
        couple_config["mode"] = "column"
        couple_config["flag_col"] = st.selectbox(
            "Colonne indicatrice couple (0/1 ou True/False)",
            columns,
            key="batch_couple_flag_col",
        )
        st.caption("Mapper les colonnes du conjoint:")
        p2_mapping = {}
        p2_cols = st.columns(n_cols_display)
        for i, attr in enumerate(["age", "earn", "self_earn", "rpp", "cpp"]):
            with p2_cols[i % n_cols_display]:
                sel = st.selectbox(
                    f"Conjoint: {attr}",
                    options,
                    key=f"map_p2_{attr}",
                )
                if sel != NONE_OPTION:
                    p2_mapping[attr] = sel
        couple_config["p2_mapping"] = p2_mapping

    elif couple_mode_label == t("batch_couple_attrs"):
        couple_config["mode"] = "attrs"
        st.caption("Mapper les colonnes du conjoint:")
        p2_mapping = {}
        p2_cols = st.columns(n_cols_display)
        for i, attr in enumerate(mappable):
            with p2_cols[i % n_cols_display]:
                sel = st.selectbox(
                    f"Conjoint: {attr}",
                    options,
                    key=f"map_p2a_{attr}",
                )
                if sel != NONE_OPTION:
                    p2_mapping[attr] = sel
        couple_config["p2_mapping"] = p2_mapping

    st.divider()

    # 6. Dependent config
    dep_mode_label = st.radio(
        t("batch_dep_mode"),
        [t("batch_dep_none"), t("batch_dep_simple"), t("batch_dep_multi")],
        key="batch_dep_mode",
    )

    dep_config = {"mode": "none"}
    if dep_mode_label == t("batch_dep_simple"):
        dep_config["mode"] = "simple"
        col_nk, col_age = st.columns(2)
        with col_nk:
            dep_config["n_kids_col"] = st.selectbox(
                "Colonne nombre d'enfants",
                columns,
                key="batch_dep_nkids_col",
            )
        with col_age:
            dep_config["kid_age_col"] = st.selectbox(
                "Colonne age moyen des enfants (optionnel)",
                [NONE_OPTION] + columns,
                key="batch_dep_age_col",
            )
            if dep_config["kid_age_col"] == NONE_OPTION:
                dep_config["kid_age_col"] = None

    elif dep_mode_label == t("batch_dep_multi"):
        dep_config["mode"] = "multi"
        age_cols_str = st.text_input(
            "Colonnes d'age des enfants (separees par des virgules, ex: kid1_age, kid2_age)",
            key="batch_dep_multi_cols",
        )
        dep_config["age_cols"] = [c.strip() for c in age_cols_str.split(",") if c.strip()]

    st.divider()

    # 7. Run button
    if st.button(t("batch_run"), type="primary", use_container_width=True):
        if "age" not in col_mapping:
            st.error(t("error_no_age_mapping"))
            return

        with st.spinner("Execution en cours..."):
            output_df, n_success, n_errors = run_batch(
                df=df,
                col_mapping=col_mapping,
                prov_default=prov,
                year_default=year,
                couple_config=couple_config,
                dep_config=dep_config,
                prov_col=prov_col,
                year_col=year_col,
            )

        st.session_state["batch_results"] = output_df
        st.session_state["batch_n_success"] = n_success
        st.session_state["batch_n_errors"] = n_errors

    # 8. Display results
    if "batch_results" in st.session_state:
        output_df = st.session_state["batch_results"]
        n_success = st.session_state["batch_n_success"]
        n_errors = st.session_state["batch_n_errors"]

        st.subheader(t("batch_results"))
        st.success(t("batch_success").format(n=n_success))
        if n_errors > 0:
            st.warning(t("batch_errors").format(n=n_errors))

        st.dataframe(output_df.head(50), use_container_width=True)

        # Download CSV
        csv_data = output_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            t("batch_download_csv"),
            data=csv_data,
            file_name="srd_resultats.csv",
            mime="text/csv",
        )

        # Download Excel
        excel_buffer = io.BytesIO()
        output_df.to_excel(excel_buffer, index=False, engine="openpyxl")
        excel_buffer.seek(0)
        st.download_button(
            t("batch_download_xlsx"),
            data=excel_buffer,
            file_name="srd_resultats.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
