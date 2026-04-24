import os
import csv
from pathlib import Path

def repair_marsa_pipeline(input_path, output_path):
    print(f"Demarrage de la reparation (Retour Approche 1 - Niveaux) : {input_path}")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    repaired_count = 0
    final_data = []
    
    try:
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            if i == 0 and "TERMINAL" in line: continue
            
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 3: continue
            
            # --- ANCRES ---
            terminal = parts[0]
            bloc = parts[1]
            travee = parts[2]
            
            # Extraction des chiffres
            nums = []
            for p in parts:
                try: nums.append(float(p))
                except: pass
            
            # Approche 1 : Niveau et Occurrences depuis les derniers chiffres
            niveau_raw = int(nums[-2]) if len(nums) >= 2 else 1
            occurrences = str(int(nums[-1])) if len(nums) >= 1 else "0"
            
            # --- REGLE APPROCHE 1 (DEMANDEE) ---
            # Si le niveau est entre 1 et 4 -> PLEIN
            # Si le niveau est 5 ou 6 (ou plus) -> VIDE
            if niveau_raw >= 5:
                niveau_final = min(niveau_raw, 6) # Plafonnement a 6
                type_zone = "VIDE"
            else:
                niveau_final = max(1, niveau_raw)
                type_zone = "PLEIN"

            cellule = parts[3] if (len(parts) > 3 and parts[3] != "") else "ZONE_C"
            
            final_data.append({
                "TERMINAL": terminal,
                "BLOC": bloc,
                "TRAVEE": travee,
                "CELLULE": cellule,
                "NIVEAU": niveau_final,
                "OCCURRENCES": occurrences,
                "TYPE_ZONE": type_zone
            })
            
            if niveau_raw != niveau_final:
                repaired_count += 1

        # EXPORT
        headers = ["TERMINAL", "BLOC", "TRAVEE", "CELLULE", "NIVEAU", "OCCURRENCES", "TYPE_ZONE"]
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(final_data)
            
        print(f"Exportation terminee : {output_path}")
        print(f"Audit : Classification par Niveau (1-4:Plein, 5-6:Vide) terminee.")
        return True

    except Exception as e:
        print(f"Erreur : {str(e)}")
        return False

if __name__ == "__main__":
    repair_marsa_pipeline("data/raw/positions_parc_marsa_CLEAN.csv", "data/processed/positions_finales_reparees.csv")
