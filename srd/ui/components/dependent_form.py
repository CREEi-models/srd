"""
Composant de formulaire pour les dependants (enfants).
Permet d'ajouter et retirer dynamiquement des dependants.
"""
import streamlit as st
from srd.ui.config import DEPENDENT_FIELDS, NUMBER, BOOLEAN, INTEGER
from srd.ui.strings import t


def render_dependent_form(prefix=""):
    """
    Affiche la section des dependants avec ajout/retrait dynamique.

    Parameters
    ----------
    prefix : str
        Prefixe pour les cles session_state (ex: "ep_" pour le profil TEMI)

    Returns
    -------
    list[dict]
        Liste de dictionnaires de kwargs pour Dependent.__init__
    """
    st.subheader(t("section_dependents"))

    n_deps_key = f"{prefix}n_deps"
    if n_deps_key not in st.session_state:
        st.session_state[n_deps_key] = 0

    col_add, col_info = st.columns([1, 3])
    with col_add:
        if st.button(t("btn_add_dep"), key=f"{prefix}btn_add_dep"):
            st.session_state[n_deps_key] += 1
            st.rerun()

    deps_kwargs = []
    to_remove = None

    for i in range(st.session_state[n_deps_key]):
        with st.container():
            cols = st.columns([1, 1, 1, 1, 0.5])
            dep_kwargs = {}

            for idx, (param_name, string_key, input_type, default, min_val) in enumerate(DEPENDENT_FIELDS):
                widget_key = f"{prefix}dep_{i}_{param_name}"
                with cols[idx]:
                    if input_type == BOOLEAN:
                        dep_kwargs[param_name] = st.checkbox(
                            t(string_key),
                            value=default,
                            key=widget_key,
                        )
                    elif input_type == INTEGER:
                        dep_kwargs[param_name] = int(st.number_input(
                            t(string_key),
                            value=int(default),
                            min_value=min_val if min_val is not None else None,
                            step=1,
                            key=widget_key,
                        ))
                    elif input_type == NUMBER:
                        dep_kwargs[param_name] = float(st.number_input(
                            t(string_key),
                            value=float(default),
                            min_value=float(min_val) if min_val is not None else None,
                            step=100.0,
                            key=widget_key,
                        ))

            with cols[4]:
                st.write("")  # spacing
                if st.button(t("btn_remove_dep"), key=f"{prefix}btn_rm_dep_{i}"):
                    to_remove = i

            deps_kwargs.append(dep_kwargs)

    if to_remove is not None:
        st.session_state[n_deps_key] -= 1
        # Shift session_state keys for dependents after the removed one
        for i in range(to_remove, st.session_state[n_deps_key]):
            for param_name, _, _, _, _ in DEPENDENT_FIELDS:
                src_key = f"{prefix}dep_{i+1}_{param_name}"
                dst_key = f"{prefix}dep_{i}_{param_name}"
                if src_key in st.session_state:
                    st.session_state[dst_key] = st.session_state[src_key]
        # Clean up last set of keys
        for param_name, _, _, _, _ in DEPENDENT_FIELDS:
            last_key = f"{prefix}dep_{st.session_state[n_deps_key]}_{param_name}"
            if last_key in st.session_state:
                del st.session_state[last_key]
        st.rerun()

    return deps_kwargs
