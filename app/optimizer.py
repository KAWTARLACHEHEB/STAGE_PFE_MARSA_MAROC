import time
import pandas as pd


def calculate_best_slot(new_container: dict, yard_state: dict, occupancy_stats: dict) -> dict:
    """
    Algorithme de Stacking Dynamique Marsa Maroc.
    Scores chaque position candidate et retourne le meilleur slot.

    Regles :
        1. Filtrage  : Z < 4 obligatoire
        2. LIFO      : T_new <= T_top => bonus, sinon malus fort (-500)
        3. Congestion: Zone > 85% => malus supplementaire (-300)
        4. Poids     : Nouveau trop lourd par rapport au sommet => malus (-50)

    Retourne : { "recommendation": best_slot, "logs": [...] }
    """
    scores = []
    logs = [f"[IA] Analyse lancee pour {new_container.get('reference', 'N/A')}"]

    t_new = pd.to_datetime(new_container.get("departure_time", pd.Timestamp.now()))
    weight_new = float(new_container.get("weight", 20000))

    start = time.time()

    for stack_key, containers in yard_state.items():
        zone = stack_key.split("-")[0]
        z_current = len(containers)

        # --- Filtre 1 : hauteur max Z=4 ---
        if z_current >= 4:
            continue

        score = 0.0
        reason = ""

        # --- Regle LIFO ---
        if z_current == 0:
            score = 100.0
            reason = "Pile vide (neutre)"
        else:
            top = containers[-1]
            t_top = pd.to_datetime(top["departure"])
            diff_h = (t_top - t_new).total_seconds() / 3600

            if t_new <= t_top:
                score = 200.0 - min(diff_h / 24, 100.0)
                reason = f"LIFO OK | Sommet part dans {diff_h:.1f}h"
            else:
                score = -500.0
                reason = "RISQUE FOUILLE (LIFO viole)"

            # --- Regle Poids ---
            weight_top = float(top.get("weight", 20000))
            if weight_new > weight_top + 5000:
                score -= 50.0
                reason += " | Poids instable"

        # --- Regle Congestion ---
        zone_rate = occupancy_stats.get(zone, {}).get("rate", 0)
        if zone_rate > 85:
            score -= 300.0
            reason += f" | CONGESTION Zone {zone} ({zone_rate:.0f}%)"

        scores.append({
            "slot": f"{stack_key}-{z_current + 1:02d}",
            "score": round(score, 2),
            "reasoning": reason,
            "zone": zone,
            "level": z_current + 1,
        })

    # --- Selection du meilleur ---
    scores.sort(key=lambda x: x["score"], reverse=True)
    best = scores[0] if scores else None

    elapsed_ms = (time.time() - start) * 1000
    if best:
        logs.append(f"[IA] {len(scores)} positions evaluees en {elapsed_ms:.1f}ms")
        logs.append(f"[IA] Meilleur slot : {best['slot']} (Score={best['score']})")
        logs.append(f"[IA] Raison : {best['reasoning']}")
    else:
        logs.append("[IA] Aucune position disponible (parc plein ?)")

    return {"recommendation": best, "logs": logs}


if __name__ == "__main__":
    from data_loader import YardManager

    mock_yard = {
        "A-001-A": [{"id": "C1", "z": 1, "departure": "2026-04-25 08:00", "weight": 15000}],
        "B-002-C": [],
        "C-003-D": [{"id": "C2", "z": 1, "departure": "2026-04-21 06:00", "weight": 22000}],
    }
    mock_stats = {
        "A": {"rate": 20}, "B": {"rate": 90}, "C": {"rate": 10}
    }
    new_c = {
        "reference": "TEST-001",
        "departure_time": "2026-04-23 12:00",
        "weight": 18000,
    }
    result = calculate_best_slot(new_c, mock_yard, mock_stats)
    print("Resultat :", result)
