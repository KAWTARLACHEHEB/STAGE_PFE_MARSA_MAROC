import sys
import json
from data_loader import YardManager
from optimizer import calculate_best_slot

def main():
    try:
        # Lire les données envoyées par Node.js via stdin
        input_data = json.loads(sys.stdin.read())
        new_container = input_data['container']
        
        # 1. Charger l'état actuel depuis la DB (simulé ici par les CSV pour le test)
        # Dans un vrai système, on lirait ici le dernier snapshot MySQL
        loader = YardManager('data/hybrid_arrivals_1k_v2.csv', 'data/hybrid_snapshot_1k_v2.csv')
        loader.load_data()
        loader.build_stack_map()
        
        # 2. Récupérer les stats d'occupation
        occupancy_stats = loader.get_occupancy_stats()
        
        # 3. Calculer l'optimisation
        result = calculate_best_slot(new_container, loader.yard_state, occupancy_stats)
        
        # 4. Renvoyer le résultat complet en JSON à Node.js
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
