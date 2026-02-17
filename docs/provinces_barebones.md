# Module provincial simplifié (Barebones)

## Description

Ce module permet de calculer l'impôt provincial pour toutes les provinces et territoires canadiens avec un modèle simplifié.

Le modèle simplifié inclut uniquement:
- **Paliers d'imposition** (tax brackets)
- **Montant personnel de base** (basic personal amount)

Pour le Québec et l'Ontario, vous pouvez choisir entre:
- Le **modèle complet** (modules `srd.quebec` et `srd.ontario`) avec tous les crédits, contributions et surtaxes
- Le **modèle barebones** (module `srd.provinces`) avec seulement les paliers et le montant de base

## Structure des fichiers

```
srd/provinces/
├── __init__.py
├── template.py          # Gabarit de calcul simplifié
├── forms.py             # Fonction factory pour créer les formulaires
└── params/
    ├── {prov}_measures_{year}.csv   # Montant personnel de base
    └── {prov}_schedule_{year}.csv   # Paliers d'imposition
```

## Codes des provinces et territoires

| Code | Province/Territoire | Notes |
|------|---------------------|-------|
| `qc` | Québec | Modèle complet aussi disponible via `srd.quebec` |
| `on` | Ontario | Modèle complet aussi disponible via `srd.ontario` |
| `ab` | Alberta | |
| `bc` | Colombie-Britannique | |
| `sk` | Saskatchewan | |
| `mb` | Manitoba | |
| `nb` | Nouveau-Brunswick | |
| `ns` | Nouvelle-Écosse | |
| `pe` | Île-du-Prince-Édouard | |
| `nl` | Terre-Neuve-et-Labrador | |
| `nt` | Territoires du Nord-Ouest | |
| `nu` | Nunavut | |
| `yt` | Yukon | |

## Paramètres 2023

### Montant personnel de base et taux

| Province | Montant personnel de base | Taux du crédit |
|----------|---------------------------|----------------|
| Québec | 17 183 $ | 14,00% |
| Ontario | 11 865 $ | 5,05% |
| Alberta | 21 003 $ | 10,00% |
| Colombie-Britannique | 11 981 $ | 5,06% |
| Saskatchewan | 15 000 $ | 10,50% |
| Manitoba | 15 000 $ | 10,80% |
| Nouveau-Brunswick | 12 458 $ | 9,40% |
| Nouvelle-Écosse | 8 481 $ | 8,79% |
| Île-du-Prince-Édouard | 12 500 $ | 9,80% |
| Terre-Neuve-et-Labrador | 10 382 $ | 8,70% |
| Territoires du Nord-Ouest | 16 593 $ | 5,90% |
| Nunavut | 17 925 $ | 4,00% |
| Yukon | 15 000 $ | 6,40% |

### Paliers d'imposition

#### Québec (4 paliers)
| Revenu imposable | Taux |
|------------------|------|
| 0 $ - 49 275 $ | 14,00% |
| 49 275 $ - 98 540 $ | 19,00% |
| 98 540 $ - 119 910 $ | 24,00% |
| Plus de 119 910 $ | 25,75% |

#### Ontario (5 paliers)
| Revenu imposable | Taux |
|------------------|------|
| 0 $ - 49 231 $ | 5,05% |
| 49 231 $ - 98 463 $ | 9,15% |
| 98 463 $ - 150 000 $ | 11,16% |
| 150 000 $ - 220 000 $ | 12,16% |
| Plus de 220 000 $ | 13,16% |

#### Alberta (5 paliers)
| Revenu imposable | Taux |
|------------------|------|
| 0 $ - 142 292 $ | 10% |
| 142 292 $ - 170 751 $ | 12% |
| 170 751 $ - 227 668 $ | 13% |
| 227 668 $ - 341 502 $ | 14% |
| Plus de 341 502 $ | 15% |

#### Colombie-Britannique (7 paliers)
| Revenu imposable | Taux |
|------------------|------|
| 0 $ - 45 654 $ | 5,06% |
| 45 654 $ - 91 310 $ | 7,70% |
| 91 310 $ - 104 835 $ | 10,50% |
| 104 835 $ - 127 299 $ | 12,29% |
| 127 299 $ - 172 602 $ | 14,70% |
| 172 602 $ - 240 716 $ | 16,80% |
| Plus de 240 716 $ | 20,50% |

#### Saskatchewan (3 paliers)
| Revenu imposable | Taux |
|------------------|------|
| 0 $ - 49 720 $ | 10,50% |
| 49 720 $ - 142 058 $ | 12,50% |
| Plus de 142 058 $ | 14,50% |

#### Manitoba (3 paliers)
| Revenu imposable | Taux |
|------------------|------|
| 0 $ - 36 842 $ | 10,80% |
| 36 842 $ - 79 625 $ | 12,75% |
| Plus de 79 625 $ | 17,40% |

#### Nouveau-Brunswick (4 paliers)
| Revenu imposable | Taux |
|------------------|------|
| 0 $ - 47 715 $ | 9,40% |
| 47 715 $ - 95 431 $ | 14,00% |
| 95 431 $ - 176 756 $ | 16,00% |
| Plus de 176 756 $ | 19,50% |

#### Nouvelle-Écosse (5 paliers)
| Revenu imposable | Taux |
|------------------|------|
| 0 $ - 29 590 $ | 8,79% |
| 29 590 $ - 59 180 $ | 14,95% |
| 59 180 $ - 93 000 $ | 16,67% |
| 93 000 $ - 150 000 $ | 17,50% |
| Plus de 150 000 $ | 21,00% |

#### Île-du-Prince-Édouard (3 paliers)
| Revenu imposable | Taux |
|------------------|------|
| 0 $ - 31 984 $ | 9,80% |
| 31 984 $ - 63 969 $ | 13,80% |
| Plus de 63 969 $ | 16,70% |

#### Terre-Neuve-et-Labrador (8 paliers)
| Revenu imposable | Taux |
|------------------|------|
| 0 $ - 41 457 $ | 8,70% |
| 41 457 $ - 82 913 $ | 14,50% |
| 82 913 $ - 148 027 $ | 15,80% |
| 148 027 $ - 207 239 $ | 17,80% |
| 207 239 $ - 264 750 $ | 19,80% |
| 264 750 $ - 529 500 $ | 20,80% |
| 529 500 $ - 1 059 000 $ | 21,30% |
| Plus de 1 059 000 $ | 21,80% |

#### Territoires du Nord-Ouest (4 paliers)
| Revenu imposable | Taux |
|------------------|------|
| 0 $ - 48 326 $ | 5,90% |
| 48 326 $ - 96 655 $ | 8,60% |
| 96 655 $ - 157 139 $ | 12,20% |
| Plus de 157 139 $ | 14,05% |

#### Nunavut (4 paliers)
| Revenu imposable | Taux |
|------------------|------|
| 0 $ - 50 877 $ | 4,00% |
| 50 877 $ - 101 754 $ | 7,00% |
| 101 754 $ - 165 429 $ | 9,00% |
| Plus de 165 429 $ | 11,50% |

#### Yukon (5 paliers)
| Revenu imposable | Taux |
|------------------|------|
| 0 $ - 53 359 $ | 6,40% |
| 53 359 $ - 106 717 $ | 9,00% |
| 106 717 $ - 165 430 $ | 10,90% |
| 165 430 $ - 500 000 $ | 12,80% |
| Plus de 500 000 $ | 15,00% |

## Utilisation

### Chargement direct d'un formulaire provincial

```python
from srd import provinces

# Charger le formulaire Alberta 2023
ab_form = provinces.form('ab', 2023)

# Voir les paramètres
print(ab_form.nrtc_base)    # 21003.0
print(ab_form.nrtc_rate)    # 0.10
print(ab_form.l_brackets)   # [0.0, 142292.0, ...]
```

### Calcul complet avec impôt provincial

```python
from srd import Person, Hhold, provinces, federal
from srd.payroll import payroll

# Créer une personne
p = Person(age=45, earn=75000)
hh = Hhold(p, prov='qc')  # Province initiale (pour payroll)

# Calculer les cotisations sociales (requis pour le fédéral)
payroll(2023).compute(hh)

# Calculer l'impôt fédéral
federal.form(2023).file(hh)

# Calculer l'impôt provincial (Alberta)
provinces.form('ab', 2023).file(hh)

# Résultats
print(f"Impôt fédéral: {p.fed_return['net_tax_liability']:.2f} $")
print(f"Impôt provincial (AB): {p.prov_return['net_tax_liability']:.2f} $")
```

### Exemple de comparaison interprovinciale

```python
from srd import Person, Hhold, provinces, federal
from srd.payroll import payroll

revenu = 75000

print(f"Comparaison de l'impôt provincial pour un revenu de {revenu} $")
print("-" * 50)

for prov in provinces.PROVINCES:
    p = Person(age=45, earn=revenu)
    hh = Hhold(p, prov='qc')
    payroll(2023).compute(hh)
    federal.form(2023).file(hh)
    provinces.form(prov, 2023).file(hh)
    print(f"{prov.upper()}: {p.prov_return['net_tax_liability']:,.2f} $")
```

**Résultat pour un revenu de 75 000 $ (barebones 2023):**

| Province | Impôt provincial |
|----------|------------------|
| QC | 9 753 $ |
| NS | 8 811 $ |
| PE | 8 064 $ |
| NL | 7 475 $ |
| MB | 7 143 $ |
| NB | 7 045 $ |
| SK | 6 726 $ |
| AB | 5 336 $ |
| YT | 4 346 $ |
| ON | 4 187 $ |
| NT | 4 112 $ |
| BC | 3 915 $ |
| NU | 2 962 $ |

### Comparaison modèle complet vs barebones (QC et ON)

Pour un revenu de 75 000 $:

| Province | Modèle complet (2022) | Barebones (2023) | Différence |
|----------|----------------------|------------------|------------|
| Québec | 9 525 $ | 9 753 $ | -228 $ |
| Ontario | 4 590 $ | 4 188 $ | +402 $ |

**Note**: La différence s'explique par:
- Les crédits d'impôt additionnels non inclus dans barebones
- La contribution santé du Québec (modèle complet)
- La surtaxe de l'Ontario (modèle complet)
- Les variations des paramètres entre années

## Ajout d'une nouvelle année

Pour ajouter une nouvelle année fiscale:

1. Créer `{prov}_measures_{year}.csv`:
```csv
variable;value;type;definition
nrtc_base;21003;float;montant personnel de base
nrtc_rate;0.10;float;taux du crédit non-remboursable
```

2. Créer `{prov}_schedule_{year}.csv`:
```csv
l_brackets;0;142292;170751;227668;341502
l_rates;0.10;0.12;0.13;0.14;0.15
l_constant;0;14229.20;17637.28;25036.49;30973.25
```

3. Mettre à jour `YEARS_AVAILABLE` dans `srd/provinces/forms.py`:
```python
YEARS_AVAILABLE = {
    'qc': [2023, 2024],  # Ajouter la nouvelle année
    'on': [2023, 2024],
    'ab': [2023, 2024],
    ...
}
```

## Choix entre modèle complet et barebones

Pour le Québec et l'Ontario, vous pouvez utiliser soit le modèle complet, soit le barebones:

```python
from srd import provinces, quebec, ontario

# Modèle barebones (paliers + montant de base seulement)
form_qc_bare = provinces.form('qc', 2023)
form_on_bare = provinces.form('on', 2023)

# Modèle complet (tous les crédits, contributions, surtaxes)
form_qc_full = quebec.form(2022)
form_on_full = ontario.form(2022)
```

## Limites du modèle simplifié

Ce modèle **n'inclut pas**:
- Les crédits d'impôt non-remboursables autres que le montant personnel de base
- Les crédits d'impôt remboursables
- Les surtaxes provinciales
- Les réductions d'impôt pour faible revenu
- Les contributions santé ou autres
- Les prestations provinciales (allocations familiales, etc.)

Pour un modèle complet, voir les modules `srd/quebec/` et `srd/ontario/`.

## Sources

Les paramètres fiscaux proviennent de:
- Agence du revenu du Canada (ARC)
- Sites gouvernementaux provinciaux
- Publications fiscales officielles

**Note**: Les valeurs doivent être vérifiées annuellement contre les sources officielles.

---

*Document généré le 2 février 2026*
