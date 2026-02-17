"""
Composant de formulaire pour les attributs d'une personne.
Genere les champs a partir de la configuration dans config.py.
"""
import streamlit as st
from srd.ui.config import PERSON_FIELDS, NUMBER, BOOLEAN, INTEGER
from srd.ui.strings import t


def render_person_form(person_key):
    """
    Affiche le formulaire pour une personne.

    Parameters
    ----------
    person_key : str
        Prefixe pour les cles session_state ("p1" ou "p2")

    Returns
    -------
    dict
        Dictionnaire des kwargs pour Person.__init__
    """
    kwargs = {}

    for group_key, fields in PERSON_FIELDS.items():
        with st.expander(t(group_key), expanded=(group_key == "group_demographics")):
            for param_name, string_key, input_type, default, min_val in fields:
                widget_key = f"{person_key}_{param_name}"

                if input_type == BOOLEAN:
                    val = st.checkbox(
                        t(string_key),
                        value=default,
                        key=widget_key,
                    )
                    kwargs[param_name] = val

                elif input_type == INTEGER:
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
                                value=0,
                                min_value=min_val if min_val is not None else None,
                                step=1,
                                key=widget_key,
                            )
                            kwargs[param_name] = int(val)
                        else:
                            kwargs[param_name] = None
                    else:
                        val = st.number_input(
                            t(string_key),
                            value=int(default),
                            min_value=min_val if min_val is not None else None,
                            step=1,
                            key=widget_key,
                        )
                        kwargs[param_name] = int(val)

                elif input_type == NUMBER:
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
