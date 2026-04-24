import pandas as pd
from datetime import datetime, timedelta

def calculate_best_slot(new_container, yard_state, occupancy_stats):
    """
    Algorithme de Stacking Dynamique Marsa Maroc avec logs de raisonnement.
    """
    scores = []
    logs = [f"Analyse IA lancée pour {new_container['reference']}..."]
    
    t_new = pd.to_datetime(new_container['departure_time'])
    weight_new = new_container.get('weight', 20000)
    
    start_time = time.time()

    for stack_key, containers in yard_state.items():
        zone = stack_key.split('-')[0]
        z_current = len(containers)
        
        if z_current >= 4:
            continue
            
        score = 0
        reason = ""

        if z_current == 0:
            score = 100
            reason = "Pile vide (Position neutre)"
        else:
            top_container = containers[-1]
            t_top = pd.to_datetime(top_container['departure'])
            diff_hours = (t_top - t_new).total_seconds() / 3600
            
            if t_new <= t_top:
                score = 200 - min(diff_hours / 24, 100)
                reason = f"LIFO Respecté (Sommet part dans {diff_hours:.1f}h)"
            else:
                score = -500
                reason = "RISQUE DE FOUILLE (LIFO Violé)"

        # Malus Congestion
        zone_stats = occupancy_stats.get(zone, {'rate': 0})
        if zone_stats['rate'] > 85:
            score -= 300
            reason += " + MALUS CONGESTION (>85%)"

        scores.append({
            'slot': f"{stack_key}-{z_current + 1:02d}",
            'score': round(score, 2),
            'reasoning': reason,
            'zone': zone,
            'level': z_current + 1
        })

    scores.sort(key=lambda x: x['score'], reverse=True)
    best = scores[0] if scores else None
    
    calc_time = (time.time() - start_time) * 1000
    if best:
        logs.append(f"Analyse terminée en {calc_time:.1f}ms")
        logs.append(f"Meilleur choix : {best['slot']} (Score: {best['score']})")
        logs.append(f"Raison : {best['reasoning']}")

    return {"recommendation": best, "logs": logs}

# --- Test rapide de l'algorithme ---
if __name__ == "__main__":
    # État simulé
    mock_yard = {
        'A-001-A': [{'id': 'C1', 'z': 1, 'departure': '2026-04-20 18:00:00', 'weight': 15000}],
        'B-002-C': [{'id': 'C2', 'z': 1, 'departure': '2026-04-20 08:00:00', 'weight': 25000}],
        'C-003-D': [] # Pile vide
    }
    
    mock_stats = {'A': {'rate': 20}, 'B': {'rate': 90}, 'C': {'rate': 10}}
    
    new_c = {'container_id': 'NEW', 'departure_time': '2026-04-20 12:00:00', 'weight': 22000}
    
    import time
    start = time.time()
    best = calculate_best_slot(new_c, mock_yard, mock_stats)
    end = time.time()
    
    print(f"Meilleur emplacement trouvé : {best['slot']} avec un score de {best['score']}")
    print(f"Calcul effectué en {(end-start)*1000:.2f}ms")
