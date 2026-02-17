#!/usr/bin/env python3
"""
Script to fix l_constant values in provincial schedule CSV files.
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
    constants = [0.0]
    for i in range(1, len(brackets)):
        prev_constant = constants[i-1]
        bracket_width = brackets[i] - brackets[i-1]
        tax_in_bracket = rates[i-1] * bracket_width
        constants.append(round(prev_constant + tax_in_bracket, 2))
    return constants

def write_schedule(filepath, brackets, rates, constants):
    """Write corrected schedule to CSV file."""
    with open(filepath, 'w') as f:
        # l_brackets
        brackets_str = ';'.join([str(int(b) if b == int(b) else b) for b in brackets])
        f.write(f"l_brackets;{brackets_str}\n")
        
        # l_rates
        rates_str = ';'.join([str(r) for r in rates])
        f.write(f"l_rates;{rates_str}\n")
        
        # l_constant
        constants_str = ';'.join([f"{c:.2f}" for c in constants])
        f.write(f"l_constant;{constants_str}\n")

def main():
    print("Correction des constantes (l_constant)")
    print("=" * 60)
    
    for prov in PROVINCES:
        filepath = os.path.join(PARAMS_DIR, f'{prov}_schedule_{YEAR}.csv')
        
        if not os.path.exists(filepath):
            print(f"{prov.upper()}: Fichier non trouvé")
            continue
        
        brackets, rates, constants = load_schedule(filepath)
        calculated = calculate_constants(brackets, rates)
        
        # Check if correction needed
        needs_fix = False
        for i in range(len(calculated)):
            if i >= len(constants) or abs(constants[i] - calculated[i]) >= 0.01:
                needs_fix = True
                break
        
        if needs_fix:
            write_schedule(filepath, brackets, rates, calculated)
            print(f"{prov.upper()}: CORRIGÉ")
            for i in range(len(brackets)):
                old = constants[i] if i < len(constants) else 0
                new = calculated[i]
                if abs(old - new) >= 0.01:
                    print(f"  Palier {i+1}: {old:.2f} → {new:.2f}")
        else:
            print(f"{prov.upper()}: OK (pas de correction nécessaire)")
    
    print("\n" + "=" * 60)
    print("Terminé! Relancez verify_constants.py pour vérifier.")

if __name__ == '__main__':
    main()
