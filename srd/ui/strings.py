"""
Systeme d'internationalisation pour l'interface SRD.
Toutes les chaines de caracteres visibles par l'utilisateur sont centralisees ici.
"""

_lang = "fr"

STRINGS = {
    # App
    "app_title": {
        "fr": "SRD - Simulateur de Revenu Disponible",
        "en": "SRD - Disposable Income Simulator",
    },
    "sidebar_province": {"fr": "Province", "en": "Province"},
    "sidebar_year": {"fr": "Annee fiscale", "en": "Tax year"},
    "sidebar_lang": {"fr": "Langue", "en": "Language"},
    "nav_manual": {"fr": "Calculateur manuel", "en": "Manual calculator"},
    "nav_batch": {"fr": "Mode batch", "en": "Batch mode"},
    "nav_emtr_profile": {"fr": "Profil TEMI", "en": "EMTR profile"},

    # Province names
    "prov_qc": {"fr": "Quebec (QC)", "en": "Quebec (QC)"},
    "prov_on": {"fr": "Ontario (ON)", "en": "Ontario (ON)"},
    "prov_ab": {"fr": "Alberta (AB)", "en": "Alberta (AB)"},
    "prov_bc": {"fr": "Colombie-Britannique (BC)", "en": "British Columbia (BC)"},
    "prov_sk": {"fr": "Saskatchewan (SK)", "en": "Saskatchewan (SK)"},
    "prov_mb": {"fr": "Manitoba (MB)", "en": "Manitoba (MB)"},
    "prov_nb": {"fr": "Nouveau-Brunswick (NB)", "en": "New Brunswick (NB)"},
    "prov_ns": {"fr": "Nouvelle-Ecosse (NS)", "en": "Nova Scotia (NS)"},
    "prov_pe": {"fr": "Ile-du-Prince-Edouard (PE)", "en": "Prince Edward Island (PE)"},
    "prov_nl": {"fr": "Terre-Neuve-et-Labrador (NL)", "en": "Newfoundland and Labrador (NL)"},
    "prov_nt": {"fr": "Territoires du Nord-Ouest (NT)", "en": "Northwest Territories (NT)"},
    "prov_nu": {"fr": "Nunavut (NU)", "en": "Nunavut (NU)"},
    "prov_yt": {"fr": "Yukon (YT)", "en": "Yukon (YT)"},

    # Manual page
    "manual_title": {"fr": "Calculateur manuel", "en": "Manual calculator"},
    "couple_toggle": {"fr": "Couple", "en": "Couple"},
    "tab_person1": {"fr": "Personne 1", "en": "Person 1"},
    "tab_person2": {"fr": "Personne 2 (conjoint)", "en": "Person 2 (spouse)"},
    "section_dependents": {"fr": "Personnes a charge", "en": "Dependents"},
    "section_household": {"fr": "Menage", "en": "Household"},
    "btn_compute": {"fr": "Calculer", "en": "Calculate"},
    "btn_add_dep": {"fr": "Ajouter un dependant", "en": "Add dependent"},
    "btn_remove_dep": {"fr": "Retirer", "en": "Remove"},

    # Person form groups
    "group_demographics": {"fr": "Demographiques", "en": "Demographics"},
    "group_employment": {"fr": "Revenus d'emploi", "en": "Employment income"},
    "group_pension": {"fr": "Pension et placements", "en": "Pension & investments"},
    "group_other_income": {"fr": "Autres revenus", "en": "Other income"},
    "group_deductions": {"fr": "Deductions et cotisations", "en": "Deductions & contributions"},
    "group_health": {"fr": "Sante et garde d'enfants", "en": "Health & childcare"},
    "group_other": {"fr": "Autres parametres", "en": "Other parameters"},

    # Person fields - Demographics
    "field_age": {"fr": "Age", "en": "Age"},
    "field_male": {"fr": "Homme", "en": "Male"},
    "field_disabled": {"fr": "En situation de handicap", "en": "Disabled"},
    "field_widow": {"fr": "Veuf/veuve", "en": "Widowed"},
    "field_student": {"fr": "Etudiant", "en": "Student"},
    "field_essential_worker": {"fr": "Travailleur essentiel (QC)", "en": "Essential worker (QC)"},
    "field_dep_senior": {"fr": "Aine non autonome", "en": "Dependent senior"},
    "field_long_term_ss": {"fr": "Solidarite sociale long terme (66+ mois)", "en": "Long-term social solidarity (66+ months)"},

    # Person fields - Employment
    "field_earn": {"fr": "Revenu de travail salarie ($)", "en": "Employment earnings ($)"},
    "field_self_earn": {"fr": "Revenu de travail autonome ($)", "en": "Self-employment income ($)"},

    # Person fields - Pension & investments
    "field_rpp": {"fr": "Regime complementaire de retraite ($)", "en": "Registered pension plan ($)"},
    "field_cpp": {"fr": "RRQ/RPC ($)", "en": "CPP/QPP ($)"},
    "field_inc_rrsp": {"fr": "Retrait REER ($)", "en": "RRSP withdrawal ($)"},
    "field_inc_rdsp": {"fr": "Retrait REEI ($)", "en": "RDSP withdrawal ($)"},
    "field_net_cap_gains": {"fr": "Gains nets en capital ($)", "en": "Net capital gains ($)"},
    "field_prev_cap_losses": {"fr": "Pertes en capital d'autres annees ($)", "en": "Prior-year capital losses ($)"},
    "field_cap_gains_exempt": {"fr": "Exoneration gains en capital ($)", "en": "Capital gains exemption ($)"},
    "field_div_elig": {"fr": "Dividendes determines ($)", "en": "Eligible dividends ($)"},
    "field_div_other_can": {"fr": "Dividendes ordinaires ($)", "en": "Other Canadian dividends ($)"},

    # Person fields - Other income
    "field_othtax": {"fr": "Autre revenu imposable ($)", "en": "Other taxable income ($)"},
    "field_othntax": {"fr": "Autre revenu non imposable ($)", "en": "Other non-taxable income ($)"},

    # Person fields - Deductions
    "field_con_rrsp": {"fr": "Cotisation REER ($)", "en": "RRSP contribution ($)"},
    "field_con_rdsp": {"fr": "Cotisation REEI ($)", "en": "RDSP contribution ($)"},
    "field_con_non_rrsp": {"fr": "Autre cotisation (CELI, etc.) ($)", "en": "Other contribution (TFSA, etc.) ($)"},
    "field_con_rpp": {"fr": "Cotisation RPA ($)", "en": "RPP contribution ($)"},
    "field_union_dues": {"fr": "Cotisations syndicales ($)", "en": "Union dues ($)"},
    "field_donation": {"fr": "Dons de bienfaisance ($)", "en": "Charitable donations ($)"},
    "field_gift": {"fr": "Dons de biens culturels ($)", "en": "Cultural property gifts ($)"},

    # Person fields - Health & childcare
    "field_med_exp": {"fr": "Depenses en sante admissibles ($)", "en": "Eligible medical expenses ($)"},
    "field_ndays_chcare_k1": {"fr": "Jours de garde - enfant 1", "en": "Childcare days - child 1"},
    "field_ndays_chcare_k2": {"fr": "Jours de garde - enfant 2", "en": "Childcare days - child 2"},

    # Person fields - Other
    "field_asset": {"fr": "Actifs (avoirs liquides) ($)", "en": "Assets (liquid) ($)"},
    "field_years_can": {"fr": "Annees au Canada (depuis 18 ans)", "en": "Years in Canada (since age 18)"},
    "field_prev_inc_work": {"fr": "Revenu de travail annee precedente ($)", "en": "Prior-year work income ($)"},
    "field_prop_tax": {"fr": "Taxe fonciere ($)", "en": "Property tax ($)"},
    "field_pub_drug_insurance": {"fr": "Assurance medicaments publique (QC)", "en": "Public drug insurance (QC)"},
    "field_tax_shield": {"fr": "Bouclier fiscal (QC)", "en": "Tax shield (QC)"},
    "field_home_support_cost": {"fr": "Depenses maintien a domicile ($)", "en": "Home support expenses ($)"},
    "field_home_access_cost": {"fr": "Depenses accessibilite domiciliaire ($)", "en": "Home accessibility expenses ($)"},
    "field_oas_years_post": {"fr": "Annees de report PSV (apres 65 ans)", "en": "OAS deferral years (after 65)"},
    "field_months_ei": {"fr": "Mois d'assurance-emploi demandes", "en": "EI months claimed"},
    "field_cdsg": {"fr": "Subvention canadienne pour invalidite cumulative ($)", "en": "Cumulative CDSG ($)"},
    "field_cdsb": {"fr": "Bon canadien pour invalidite cumulatif ($)", "en": "Cumulative CDSB ($)"},

    # Dependent fields
    "dep_age": {"fr": "Age", "en": "Age"},
    "dep_disabled": {"fr": "Handicap", "en": "Disabled"},
    "dep_child_care": {"fr": "Frais de garde ($)", "en": "Childcare expenses ($)"},
    "dep_med_exp": {"fr": "Depenses sante ($)", "en": "Medical expenses ($)"},

    # Household fields
    "field_rent": {"fr": "Loyer ($)", "en": "Rent ($)"},
    "field_prev_fam_net_inc_prov": {
        "fr": "Revenu familial net provincial annee precedente ($)",
        "en": "Prior-year provincial family net income ($)",
    },

    # Results
    "results_title": {"fr": "Resultats", "en": "Results"},
    "result_fam_disp_inc": {"fr": "Revenu disponible familial", "en": "Family disposable income"},
    "result_fam_after_tax": {"fr": "Revenu apres impots", "en": "After-tax income"},
    "result_total_tax": {"fr": "Impots total", "en": "Total tax"},
    "result_total_payroll": {"fr": "Cotisations sociales", "en": "Payroll contributions"},
    "result_emtr": {"fr": "Taux effectif marginal d'imposition", "en": "Effective marginal tax rate"},
    "result_emtr_help": {
        "fr": "Fraction d'un 1 000 $ supplementaire de revenu salarial perdu en impots, cotisations et reduction de prestations",
        "en": "Fraction of an additional $1,000 in earnings lost to taxes, contributions, and benefit clawbacks",
    },
    "result_person_detail": {"fr": "Detail - Personne {n}", "en": "Detail - Person {n}"},
    "result_fed_return": {"fr": "Declaration federale", "en": "Federal return"},
    "result_prov_return": {"fr": "Declaration provinciale", "en": "Provincial return"},
    "result_payroll": {"fr": "Cotisations sociales", "en": "Payroll contributions"},
    "result_benefits": {"fr": "Prestations", "en": "Benefits"},

    # Federal return keys
    "ret_gross_income": {"fr": "Revenu brut", "en": "Gross income"},
    "ret_deductions_gross_inc": {"fr": "Deductions du revenu brut", "en": "Gross income deductions"},
    "ret_net_income": {"fr": "Revenu net", "en": "Net income"},
    "ret_deductions_net_inc": {"fr": "Deductions du revenu net", "en": "Net income deductions"},
    "ret_taxable_income": {"fr": "Revenu imposable", "en": "Taxable income"},
    "ret_gross_tax_liability": {"fr": "Impot brut", "en": "Gross tax liability"},
    "ret_non_refund_credits": {"fr": "Credits non remboursables", "en": "Non-refundable credits"},
    "ret_refund_credits": {"fr": "Credits remboursables", "en": "Refundable credits"},
    "ret_net_tax_liability": {"fr": "Impot net", "en": "Net tax liability"},
    "ret_rdsp_benefits": {"fr": "Prestations REEI", "en": "RDSP benefits"},

    # Payroll keys
    "pay_ei": {"fr": "Assurance-emploi (AE)", "en": "Employment insurance (EI)"},
    "pay_cpp": {"fr": "RRQ/RPC", "en": "CPP/QPP"},
    "pay_cpp_supp": {"fr": "RRQ/RPC supplementaire", "en": "CPP/QPP supplementary"},
    "pay_qpip": {"fr": "RQAP", "en": "QPIP"},

    # Benefit labels
    "ben_inc_oas": {"fr": "Pension de securite de la vieillesse (PSV)", "en": "Old Age Security (OAS)"},
    "ben_inc_gis": {"fr": "Supplement de revenu garanti (SRG)", "en": "Guaranteed Income Supplement (GIS)"},
    "ben_allow_couple": {"fr": "Allocation au conjoint", "en": "Spousal allowance"},
    "ben_allow_surv": {"fr": "Allocation au survivant", "en": "Survivor's allowance"},
    "ben_allow_housing": {"fr": "Allocation-logement", "en": "Housing allowance"},
    "ben_inc_ei": {"fr": "Assurance-emploi", "en": "Employment insurance"},
    "ben_inc_sa": {"fr": "Aide sociale", "en": "Social assistance"},
    "ben_inc_ss": {"fr": "Solidarite sociale", "en": "Social solidarity"},

    # Batch page
    "batch_title": {"fr": "Mode batch", "en": "Batch mode"},
    "batch_upload": {"fr": "1. Telecharger un fichier", "en": "1. Upload a file"},
    "batch_upload_help": {
        "fr": "Formats acceptes: CSV, Excel (.xlsx), Stata (.dta)",
        "en": "Accepted formats: CSV, Excel (.xlsx), Stata (.dta)",
    },
    "batch_preview": {"fr": "2. Apercu des donnees", "en": "2. Data preview"},
    "batch_preview_info": {"fr": "{n} lignes x {c} colonnes", "en": "{n} rows x {c} columns"},
    "batch_mapping": {"fr": "3. Correspondance des colonnes", "en": "3. Column mapping"},
    "batch_mapping_none": {"fr": "-- Non assigne --", "en": "-- Unassigned --"},
    "batch_config": {"fr": "4. Configuration", "en": "4. Configuration"},
    "batch_couple_mode": {"fr": "Mode couple", "en": "Couple mode"},
    "batch_couple_all_single": {"fr": "Tous celibataires", "en": "All singles"},
    "batch_couple_column": {"fr": "Colonne indicatrice de couple", "en": "Couple indicator column"},
    "batch_couple_attrs": {"fr": "Colonnes pour personne 2", "en": "Person 2 columns"},
    "batch_dep_mode": {"fr": "Mode dependants", "en": "Dependent mode"},
    "batch_dep_none": {"fr": "Aucun dependant", "en": "No dependents"},
    "batch_dep_simple": {"fr": "Simple (n_kids + age moyen)", "en": "Simple (n_kids + average age)"},
    "batch_dep_multi": {"fr": "Multi-colonnes (kid1_age, kid2_age, ...)", "en": "Multi-column (kid1_age, kid2_age, ...)"},
    "batch_run": {"fr": "Executer", "en": "Run"},
    "batch_results": {"fr": "5. Resultats", "en": "5. Results"},
    "batch_download_csv": {"fr": "Telecharger en CSV", "en": "Download as CSV"},
    "batch_download_xlsx": {"fr": "Telecharger en Excel", "en": "Download as Excel"},
    "batch_success": {"fr": "{n} lignes calculees avec succes", "en": "{n} rows computed successfully"},
    "batch_errors": {"fr": "{n} erreurs", "en": "{n} errors"},
    "batch_prov_source": {"fr": "Source de la province", "en": "Province source"},
    "batch_prov_sidebar": {"fr": "Utiliser la province du panneau lateral", "en": "Use sidebar province"},
    "batch_prov_column": {"fr": "Colonne du fichier", "en": "File column"},
    "batch_year_source": {"fr": "Source de l'annee", "en": "Year source"},
    "batch_year_sidebar": {"fr": "Utiliser l'annee du panneau lateral", "en": "Use sidebar year"},
    "batch_year_column": {"fr": "Colonne du fichier", "en": "File column"},

    # EMTR Profile page
    "emtr_title": {
        "fr": "Profil du taux effectif marginal d'imposition",
        "en": "Effective marginal tax rate profile",
    },
    "emtr_config": {"fr": "Configuration du profil", "en": "Profile configuration"},
    "emtr_vary_field": {"fr": "Variable a faire varier", "en": "Variable to vary"},
    "emtr_vary_earn": {"fr": "Revenu de travail salarie (earn)", "en": "Employment earnings (earn)"},
    "emtr_vary_self_earn": {"fr": "Revenu de travail autonome (self_earn)", "en": "Self-employment income (self_earn)"},
    "emtr_vary_rpp": {"fr": "Regime complementaire de retraite (rpp)", "en": "Registered pension plan (rpp)"},
    "emtr_vary_cpp": {"fr": "RRQ/RPC (cpp)", "en": "CPP/QPP (cpp)"},
    "emtr_vary_inc_rrsp": {"fr": "Retrait REER (inc_rrsp)", "en": "RRSP withdrawal (inc_rrsp)"},
    "emtr_min": {"fr": "Minimum ($)", "en": "Minimum ($)"},
    "emtr_max": {"fr": "Maximum ($)", "en": "Maximum ($)"},
    "emtr_step": {"fr": "Increment ($)", "en": "Step ($)"},
    "emtr_btn_compute": {"fr": "Calculer le profil TEMI", "en": "Compute EMTR profile"},
    "emtr_chart_title": {
        "fr": "Taux effectif marginal d'imposition (%)",
        "en": "Effective marginal tax rate (%)",
    },
    "emtr_col_value": {"fr": "Valeur ($)", "en": "Value ($)"},
    "emtr_col_emtr": {"fr": "TEMI (%)", "en": "EMTR (%)"},
    "emtr_col_disp_inc": {"fr": "Rev. disp. familial ($)", "en": "Family disp. income ($)"},
    "emtr_download_csv": {"fr": "Telecharger en CSV", "en": "Download as CSV"},
    "emtr_download_xlsx": {"fr": "Telecharger en Excel", "en": "Download as Excel"},
    "emtr_note": {
        "fr": "Le TEMI est calcule comme 1 - (variation du revenu disponible familial) / (variation de 1 000 $ du revenu selectionne)",
        "en": "The EMTR is computed as 1 - (change in family disposable income) / ($1,000 change in the selected income)",
    },

    # Errors
    "error_age_range": {"fr": "L'age doit etre entre 0 et 120", "en": "Age must be between 0 and 120"},
    "error_negative_amount": {
        "fr": "Le montant de '{field}' ne peut pas etre negatif",
        "en": "The amount for '{field}' cannot be negative",
    },
    "error_no_file": {"fr": "Veuillez telecharger un fichier", "en": "Please upload a file"},
    "error_computation": {"fr": "Erreur lors du calcul: {msg}", "en": "Computation error: {msg}"},
    "error_no_age_mapping": {"fr": "La colonne 'age' doit etre assignee", "en": "The 'age' column must be mapped"},
    "error_unsupported_format": {"fr": "Format de fichier non supporte", "en": "Unsupported file format"},
    "error_year_not_available": {
        "fr": "L'annee {year} n'est pas disponible pour la province {prov}",
        "en": "Year {year} is not available for province {prov}",
    },
}


def set_lang(lang):
    """Change la langue active."""
    global _lang
    _lang = lang


def t(key):
    """Retourne la chaine traduite pour la cle donnee."""
    entry = STRINGS.get(key, {})
    return entry.get(_lang, key)
