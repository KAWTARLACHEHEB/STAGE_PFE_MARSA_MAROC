from data_loader import YardManager
import pandas as pd
import os

def run_test():
    print("--- TEST DU MODULE DATA_LOADER MARSA MAROC ---")
    
    # 1. Test unitaire du parsing de Slot
    slot_test = "C-012-I-04"
    parsed = YardManager.parse_slot(slot_test)
    print(f"\n1. Test Parsing Slot '{slot_test}':")
    if parsed and parsed['zone'] == 'C' and parsed['niveau'] == 4:
        print(f"   SUCCESS: {parsed}")
    else:
        print(f"   FAILED: {parsed}")

    # 2. Création de données de test (si fichiers manquants)
    arrivals_path = 'data/hybrid_arrivals_1k_v2.csv'
    snapshot_path = 'data/hybrid_snapshot_1k_v2.csv'
    
    if not os.path.exists(arrivals_path):
        print("\n2. Creation de fichiers CSV temporaires pour le test...")
        # Création dossier data si besoin
        os.makedirs('data', exist_ok=True)
        
        # Données fictives
        df_mock = pd.DataFrame({
            'container_id': ['CONT001', 'CONT002', 'CONT003', 'CONT004'],
            'slot': ['A-001-A-01', 'A-001-A-02', 'B-005-C-01', 'C-010-F-01'],
            'departure_time': ['2026-04-20 10:00:00', '2026-04-20 12:00:00', '2026-04-21 08:00:00', '2026-04-22 14:00:00']
        })
        df_mock.to_csv(arrivals_path, index=False)
        df_mock.to_csv(snapshot_path, index=False)
        print("   SUCCESS: Fichiers crees.")

    # 3. Test de chargement et statistiques
    manager = YardManager(arrivals_path, snapshot_path)
    manager.load_data()
    
    print("\n3. Calcul des statistiques d'occupation :")
    stats = manager.get_occupancy_stats()
    for zone, data in stats.items():
        print(f"   - Zone {zone} : {data['count']} conteneurs ({data['rate']}%)")

    print("\n4. Test de la structure LIFO (Stack Map) :")
    manager.build_stack_map()
    # Vérifier la pile A-001-A
    stack_key = 'A-001-A'
    if stack_key in manager.yard_state:
        stack = manager.yard_state[stack_key]
        print(f"   SUCCESS: Pile {stack_key} : {len(stack)} conteneurs detectes.")
        for item in stack:
            print(f"      - Niveau {item['z']} : {item['id']}")
    
    print("\n--- FIN DES TESTS ---")

if __name__ == "__main__":
    run_test()
