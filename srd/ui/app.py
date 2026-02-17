"""
SRD - Simulateur de Revenu Disponible
Point d'entree de l'application Streamlit.

Lancer avec: streamlit run srd/ui/app.py
"""
import streamlit as st
from srd.ui.strings import t, set_lang
from srd.ui.config import ALL_PROVINCES, PROVINCE_LABELS, get_available_years


def main():
    st.set_page_config(
        page_title="SRD - Simulateur de Revenu Disponible",
        page_icon=":moneybag:",
        layout="wide",
    )

    # Sidebar
    # Language selector -- must come before any t() calls
    lang = st.sidebar.selectbox(
        "Langue / Language",
        ["fr", "en"],
        format_func=lambda x: "Francais" if x == "fr" else "English",
        key="sidebar_lang_select",
    )
    set_lang(lang)

    st.sidebar.title(t("app_title"))

    # Province selector
    prov_options = ALL_PROVINCES
    prov_labels = [t(PROVINCE_LABELS[p]) for p in prov_options]
    prov_idx = st.sidebar.selectbox(
        t("sidebar_province"),
        range(len(prov_options)),
        format_func=lambda i: prov_labels[i],
        key="sidebar_prov_idx",
    )
    prov = prov_options[prov_idx]

    # Year selector (filtered by province)
    available_years = get_available_years(prov)
    year = st.sidebar.selectbox(
        t("sidebar_year"),
        available_years,
        index=len(available_years) - 1,  # default to most recent
        key="sidebar_year",
    )

    st.sidebar.divider()

    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        [t("nav_manual"), t("nav_batch"), t("nav_emtr_profile")],
        key="nav_page",
        label_visibility="collapsed",
    )

    # Route to page
    if page == t("nav_manual"):
        from srd.ui.views.manual import render
        render(prov, year)
    elif page == t("nav_batch"):
        from srd.ui.views.batch import render
        render(prov, year)
    else:
        from srd.ui.views.emtr_profile import render
        render(prov, year)


if __name__ == "__main__":
    main()
