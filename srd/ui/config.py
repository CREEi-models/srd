"""
Configuration des attributs et constantes pour l'interface SRD.
Source unique de verite pour les champs du formulaire, les provinces et les annees.
"""

# Provinces avec modele complet (toutes les annees 2016-2023)
FULL_PROVINCES = ["qc", "on"]

# Toutes les provinces (barebones = 2023 seulement)
ALL_PROVINCES = ["qc", "on", "ab", "bc", "sk", "mb", "nb", "ns", "pe", "nl", "nt", "nu", "yt"]

YEARS_FULL = list(range(2016, 2024))
YEARS_BAREBONES = [2023]

# Noms affichables des provinces (cles pour strings.py)
PROVINCE_LABELS = {code: f"prov_{code}" for code in ALL_PROVINCES}


def get_available_years(prov):
    """Retourne les annees disponibles pour une province donnee."""
    if prov in FULL_PROVINCES:
        return YEARS_FULL
    return YEARS_BAREBONES


# Types de champs
NUMBER = "number"
BOOLEAN = "boolean"
INTEGER = "integer"

# Metadata des attributs Person pour le formulaire.
# Chaque tuple: (param_name, string_key, input_type, default, min_value)
# param_name correspond exactement aux kwargs de Person.__init__

PERSON_FIELDS = {
    "group_demographics": [
        ("age", "field_age", INTEGER, 50, 0),
        ("male", "field_male", BOOLEAN, True, None),
        ("disabled", "field_disabled", BOOLEAN, False, None),
        ("widow", "field_widow", BOOLEAN, False, None),
        ("student", "field_student", BOOLEAN, False, None),
        ("essential_worker", "field_essential_worker", BOOLEAN, False, None),
        ("dep_senior", "field_dep_senior", BOOLEAN, False, None),
        ("long_term_ss", "field_long_term_ss", BOOLEAN, False, None),
    ],
    "group_employment": [
        ("earn", "field_earn", NUMBER, 0, 0),
        ("self_earn", "field_self_earn", NUMBER, 0, 0),
    ],
    "group_pension": [
        ("rpp", "field_rpp", NUMBER, 0, 0),
        ("cpp", "field_cpp", NUMBER, 0, 0),
        ("inc_rrsp", "field_inc_rrsp", NUMBER, 0, 0),
        ("inc_rdsp", "field_inc_rdsp", NUMBER, 0, 0),
        ("net_cap_gains", "field_net_cap_gains", NUMBER, 0, None),
        ("prev_cap_losses", "field_prev_cap_losses", NUMBER, 0, 0),
        ("cap_gains_exempt", "field_cap_gains_exempt", NUMBER, 0, 0),
        ("div_elig", "field_div_elig", NUMBER, 0, 0),
        ("div_other_can", "field_div_other_can", NUMBER, 0, 0),
    ],
    "group_other_income": [
        ("othtax", "field_othtax", NUMBER, 0, 0),
        ("othntax", "field_othntax", NUMBER, 0, 0),
    ],
    "group_deductions": [
        ("con_rrsp", "field_con_rrsp", NUMBER, 0, 0),
        ("con_rdsp", "field_con_rdsp", NUMBER, 0, 0),
        ("con_non_rrsp", "field_con_non_rrsp", NUMBER, 0, 0),
        ("con_rpp", "field_con_rpp", NUMBER, 0, 0),
        ("union_dues", "field_union_dues", NUMBER, 0, 0),
        ("donation", "field_donation", NUMBER, 0, 0),
        ("gift", "field_gift", NUMBER, 0, 0),
    ],
    "group_health": [
        ("med_exp", "field_med_exp", NUMBER, 0, 0),
        ("ndays_chcare_k1", "field_ndays_chcare_k1", NUMBER, 0, 0),
        ("ndays_chcare_k2", "field_ndays_chcare_k2", NUMBER, 0, 0),
    ],
    "group_other": [
        ("asset", "field_asset", NUMBER, 0, 0),
        ("years_can", "field_years_can", INTEGER, None, 0),
        ("prev_inc_work", "field_prev_inc_work", NUMBER, None, 0),
        ("prop_tax", "field_prop_tax", NUMBER, 0, 0),
        ("pub_drug_insurance", "field_pub_drug_insurance", BOOLEAN, False, None),
        ("tax_shield", "field_tax_shield", BOOLEAN, False, None),
        ("home_support_cost", "field_home_support_cost", NUMBER, 0, 0),
        ("home_access_cost", "field_home_access_cost", NUMBER, 0, 0),
        ("oas_years_post", "field_oas_years_post", INTEGER, 0, 0),
        ("months_ei", "field_months_ei", INTEGER, 0, 0),
        ("cdsg", "field_cdsg", NUMBER, 0, 0),
        ("cdsb", "field_cdsb", NUMBER, 0, 0),
    ],
}

# Dependent fields
# (param_name, string_key, input_type, default, min_value)
DEPENDENT_FIELDS = [
    ("age", "dep_age", INTEGER, 5, 0),
    ("disabled", "dep_disabled", BOOLEAN, False, None),
    ("child_care", "dep_child_care", NUMBER, 0, 0),
    ("med_exp", "dep_med_exp", NUMBER, 0, 0),
]

# Household-level fields
HHOLD_FIELDS = [
    ("rent", "field_rent", NUMBER, 0, 0),
    ("prev_fam_net_inc_prov", "field_prev_fam_net_inc_prov", NUMBER, None, 0),
]

# Cles du dictionnaire fed_return / prov_return pour l'affichage
RETURN_KEYS = [
    "gross_income",
    "deductions_gross_inc",
    "net_income",
    "deductions_net_inc",
    "taxable_income",
    "gross_tax_liability",
    "non_refund_credits",
    "refund_credits",
    "net_tax_liability",
]

# fed_return a aussi rdsp_benefits
FED_EXTRA_KEYS = ["rdsp_benefits"]

# Cles du dictionnaire payroll
PAYROLL_KEYS = ["ei", "cpp", "cpp_supp", "qpip"]

# Attributs de prestations sur Person
BENEFIT_ATTRS = [
    ("inc_oas", "ben_inc_oas"),
    ("inc_gis", "ben_inc_gis"),
    ("allow_couple", "ben_allow_couple"),
    ("allow_surv", "ben_allow_surv"),
    ("allow_housing", "ben_allow_housing"),
    ("inc_ei", "ben_inc_ei"),
    ("inc_sa", "ben_inc_sa"),
    ("inc_ss", "ben_inc_ss"),
]

# Liste plate de tous les noms de parametres Person pour le mapping batch
ALL_PERSON_PARAMS = []
for fields in PERSON_FIELDS.values():
    for param_name, _, _, _, _ in fields:
        ALL_PERSON_PARAMS.append(param_name)

ALL_DEPENDENT_PARAMS = [name for name, _, _, _, _ in DEPENDENT_FIELDS]
ALL_HHOLD_PARAMS = [name for name, _, _, _, _ in HHOLD_FIELDS]
