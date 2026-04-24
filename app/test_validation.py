import sys
import os
from pathlib import Path
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent))
from smart_optimizer import SmartOptimizer

load_dotenv()

def run_validation_tests():
    print("--- DEMARRAGE DES TESTS DE VALIDATION MARSA MAROC (V5) ---\n")
    
    db_pass = quote_plus(os.getenv("MYSQL_PASSWORD", "Kawtar@123"))
    engine = create_engine(f"mysql+mysqlconnector://root:{db_pass}@127.0.0.1/marsa_maroc_db")
    
    optimizer = SmartOptimizer(engine)
    
    # F = ZONE PLEINE (verifiee en DB)
    # AE = ZONE VIDE / FRIGO (verifiee en DB)
    # 02F = ZONE VIDE / DANGEREUSE (verifiee en DB)
    yard_state = {
        'F-001': [{'departure': '2026-05-01'}], # Pile Plein occupee
        'F-002': [], # Pile vide pour l'OOG
        'AE-116': [], # Pile Frigo vide
        '02F-001': [] # Pile Dangereuse vide
    }
    occupancy_stats = {'F': {'rate': 10}, 'AE': {'rate': 5}, '02F': {'rate': 2}}

    scenarios = [
        {
            "name": "NORMAL (PLEIN)",
            "data": {"reference": "NORM-123", "weight": 22000, "special_type": "NORMAL", "departure_time": "2026-04-30"}
        },
        {
            "name": "FRIGO (VIDE)",
            "data": {"reference": "FRIG-456", "weight": 3000, "special_type": "FRIGO", "departure_time": "2026-05-05"}
        },
        {
            "name": "DANGEREUX (VIDE)",
            "data": {"reference": "DANG-789", "weight": 4000, "special_type": "DANGEREUX", "departure_time": "2026-05-10"}
        },
        {
            "name": "HORS-GABARIT (OOG)",
            "data": {"reference": "OOG-999", "weight": 35000, "special_type": "HORS_GABARIT", "departure_time": "2026-04-25"}
        }
    ]

    for sc in scenarios:
        print(f"Testing: {sc['name']}...")
        result = optimizer.calculate_best_slot(sc['data'], yard_state, occupancy_stats)
        
        if result['recommendation']:
            rec = result['recommendation']
            print(f"SUCCES : Slot Recommande : {rec['slot']} (Zone: {rec['zone']}, Niveau: {rec['level']})")
            print(f"Raison : {rec['reasoning']}")
        else:
            # Recuperation du log d'erreur reel
            reason = next((l for l in reversed(result['logs']) if "Aucune zone" in l or "Decision" not in l), "Inconnue")
            print(f"ECHEC : {reason}")
        
        print("-" * 50)

if __name__ == "__main__":
    run_validation_tests()
