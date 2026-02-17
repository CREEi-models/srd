"""
Composant de formulaire pour les parametres du menage (Hhold).
"""
import streamlit as st
from srd.ui.config import HHOLD_FIELDS, NUMBER
from srd.ui.strings import t


def render_hhold_form(prefix=""):
    """
    Affiche les champs du menage.

    Parameters
    ----------
    prefix : str
        Prefixe pour les cles session_state (ex: "ep_" pour le profil TEMI)

    Returns
    -------
    dict
        Dictionnaire des kwargs pour Hhold (rent, prev_fam_net_inc_prov)
    """
    st.subheader(t("section_household"))
    kwargs = {}

    for param_name, string_key, input_type, default, min_val in HHOLD_FIELDS:
        widget_key = f"{prefix}hh_{param_name}"

        if default is None:
            use_key = f"{widget_key}_use"
            use = st.checkbox(
                t(string_key),
                value=False,
                key=use_key,
                help="Cocher pour specifier une valeur (sinon valeur par defaut)",
            )
            if use:
                val = st.number_input(
                    t(string_key),
                    value=0.0,
                    min_value=float(min_val) if min_val is not None else None,
                    step=100.0,
                    key=widget_key,
                )
                kwargs[param_name] = float(val)
            else:
                kwargs[param_name] = None
        else:
            val = st.number_input(
                t(string_key),
                value=float(default),
                min_value=float(min_val) if min_val is not None else None,
                step=100.0,
                key=widget_key,
            )
            kwargs[param_name] = float(val)

    return kwargs
