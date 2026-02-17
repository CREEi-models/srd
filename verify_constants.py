#!/usr/bin/env python3
"""
Script to verify l_constant values in provincial schedule CSV files.

l_constant[i] represents the cumulative tax paid at the threshold of bracket i.
Formula: l_constant[i] = l_constant[i-1] + l_rates[i-1] * (l_brackets[i] - l_brackets[i-1])
"""
import os

PROVINCES = ['qc', 'on', 'ab', 'bc', 'sk', 'mb', 'nb', 'ns', 'pe', 'nl', 'nt', 'nu', 'yt']
YEAR = 2023
PARAMS_DIR = 'srd/provinces/params'

def load_schedule(filepath):
    """Load schedule CSV and return l_brackets, l_rates, l_constant as lists."""
    data = {}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(';')
            if len(parts) >= 2:
                var_name = parts[0]
                values = [float(v) for v in parts[1:]]
                data[var_name] = values
    return data.get('l_brackets', []), data.get('l_rates', []), data.get('l_constant', [])

def calculate_constants(brackets, rates):
    """Calculate what l_constant should be based on brackets and rates."""
    constants = [0.0]  # First constant is always 0
    for i in range(1, len(brackets)):
        prev_constant = constants[i-1]
        bracket_width = brackets[i] - brackets[i-1]
        tax_in_bracket = rates[i-1] * bracket_width
        constants.append(prev_constant + tax_in_bracket)
    return constants

def main():
    print("=" * 80)
    print("Vérification des constantes (l_constant) dans les fichiers schedule")
    print("=" * 80)
    
    all_ok = True
    
    for prov in PROVINCES:
        filepath = os.path.join(PARAMS_DIR, f'{prov}_schedule_{YEAR}.csv')
        
        if not os.path.exists(filepath):
            print(f"\n{prov.upper()}: Fichier non trouvé - {filepath}")
            continue
        
        brackets, rates, constants = load_schedule(filepath)
        
        if not brackets or not rates:
            print(f"\n{prov.upper()}: Données manquantes")
            continue
        
        calculated = calculate_constants(brackets, rates)
        
        print(f"\n{'='*40}")
        print(f"{prov.upper()} - {len(brackets)} paliers")
        print(f"{'='*40}")
        
        print(f"\n{'Palier':<8} {'Seuil':>12} {'Taux':>8} {'Constant (fichier)':>20} {'Constant (calculé)':>20} {'Diff':>10} {'Status':<6}")
        print("-" * 90)
        
        prov_ok = True
        for i in range(len(brackets)):
            file_const = constants[i] if i < len(constants) else 0
            calc_const = calculated[i]
            diff = abs(file_const - calc_const)
            status = "✓" if diff < 0.01 else "✗"
            
            if diff >= 0.01:
                prov_ok = False
                all_ok = False
            
            rate_str = f"{rates[i]*100:.2f}%" if i < len(rates) else "-"
            print(f"{i+1:<8} {brackets[i]:>12,.0f} {rate_str:>8} {file_const:>20,.2f} {calc_const:>20,.2f} {diff:>10,.2f} {status:<6}")
        
        # Show tax calculation example at a sample income
        sample_income = 75000
        tax = 0
        for i in range(len(brackets)):
            if i == len(brackets) - 1:
                # Last bracket
                if sample_income > brackets[i]:
                    tax = constants[i] + rates[i] * (sample_income - brackets[i])
                break
            elif sample_income <= brackets[i+1]:
                tax = constants[i] + rates[i] * (sample_income - brackets[i])
                break
        
        print(f"\nExemple: Impôt sur {sample_income:,} $ = {tax:,.2f} $")
        
        if prov_ok:
            print(f"\n✓ {prov.upper()}: Toutes les constantes sont correctes")
        else:
            print(f"\n✗ {prov.upper()}: ERREURS DÉTECTÉES dans les constantes")
    
    print("\n" + "=" * 80)
    if all_ok:
        print("✓ SUCCÈS: Toutes les provinces ont des constantes correctes")
    else:
        print("✗ ÉCHEC: Certaines provinces ont des erreurs dans les constantes")
    print("=" * 80)

if __name__ == '__main__':
    main()
