import time
import pandas as pd
from sqlalchemy import create_engine, text
import os
import random
from pathlib import Path

class SmartOptimizer:
    def __init__(self, db_engine):
        self.engine = db_engine
        self.ref_path = Path(__file__).resolve().parent.parent / "data" / "processed" / "referentiel_zones_FINAL.csv"
        self.referentiel = self.load_referentiel()

    def load_referentiel(self):
        """Charge et regroupe le referentiel par Bloc."""
        if self.ref_path.exists():
            df = pd.read_csv(self.ref_path)
            # On regroupe par BLOC pour avoir tous les types admis dans le bloc entier
            # On transforme les listes de types en ensembles (sets) pour une recherche rapide
            ref_grouped = df.groupby('BLOC')['TYPES_ADMIS'].apply(lambda x: set(", ".join(x).replace(" ", "").split(",")))
            return ref_grouped
        return pd.Series()

    def get_dynamic_zones(self, terminal="TC3"):
        print(f"[IA] Recuperation des zones {terminal} depuis MySQL...")
        try:
            with self.engine.connect() as conn:
                query = text("SELECT nom, type_zone, capacite_max, max_z FROM zones_stockage WHERE terminal = :t")
                df = pd.read_sql(query, conn, params={"t": terminal})
                print(f"[IA] {len(df)} zones {terminal} recuperees.")
                return df
        except Exception as e:
            print(f"[IA] ERREUR SQL ZONES: {e}")
            raise e

    def calculate_best_slot(self, new_container, yard_state, occupancy_stats, terminal="TC3"):
        start_time = time.time()
        logs = [f"[IA Marsa] Analyse pour {new_container.get('reference', 'N/A')}"]
        print(f"[IA] Debut du calcul pour {new_container.get('reference')}")
        
        weight = float(new_container.get('weight', 20000))
        c_type = 'PLEIN' if weight > 5000 else 'VIDE'
        c_special = new_container.get('special_type', 'NORMAL')
        
        logs.append(f"[IA Marsa] Type: {c_type} | Special: {c_special}")

        zones_config = self.get_dynamic_zones(terminal)

        # Si c'est un type special, on cherche dans TOUTES les zones compatibles avec ce type
        # sinon on restreint par poids (Plein/Vide)
        if c_special != 'NORMAL':
            compatible_zones = zones_config
        else:
            compatible_zones = zones_config[zones_config['type_zone'] == c_type]
        valid_zone_names = []
        for _, z in compatible_zones.iterrows():
            z_name = z['nom']
            # On verifie les permissions du bloc
            if not self.referentiel.empty and z_name in self.referentiel.index:
                allowed_types = self.referentiel.loc[z_name]
                if c_special in allowed_types:
                    valid_zone_names.append(z_name)
            else:
                if c_special == 'NORMAL':
                    valid_zone_names.append(z_name)

        if not valid_zone_names:
            return {"recommendation": None, "logs": logs + [f"Aucune zone n'accepte le type {c_special}"]}

        zone_max_z = dict(zip(compatible_zones['nom'], compatible_zones['max_z']))
        scores = []
        t_new = pd.to_datetime(new_container.get('departure_time'))

        for stack_key, containers in yard_state.items():
            zone = stack_key.split('-')[0]
            if zone not in valid_zone_names: continue

            z_current = len(containers)
            z_limit = zone_max_z.get(zone, 4)

            if c_special == 'HORS_GABARIT' and z_current > 0:
                continue

            if z_current >= z_limit: continue

            score = 0
            reason = ""
            if z_current == 0:
                score = 100
                reason = "Pile vide"
            else:
                top = containers[-1]
                t_top = pd.to_datetime(top['departure'])
                if t_new <= t_top:
                    score = 200
                    reason = "LIFO Respecte"
                else:
                    score = -500
                    reason = "RISQUE FOUILLE"

            zone_rate = occupancy_stats.get(zone, {}).get('rate', 0)
            if zone_rate > 80:
                score -= 300
                reason += " + CONGESTION"

            scores.append({
                "slot": f"{stack_key}-N{z_current + 1:02d}",
                "score": score,
                "reason": reason
            })

        if not scores:
            # Fallback : Si aucune pile existante n'est trouvee, on propose une nouvelle pile dans une zone valide
            fallback_zone = valid_zone_names[int(time.time()) % len(valid_zone_names)]
            return {
                "recommendation": f"{fallback_zone}-01-A-N01",
                "reasoning": "Creation de nouvelle pile (Zone Optimale)",
                "logs": logs + ["Calcul par defaut"]
            }

        # Tri par score (le plus haut en premier)
        scores.sort(key=lambda x: x['score'], reverse=True)
        
        # On recupere tous les meilleurs scores (ex: tous ceux a 200)
        best_score = scores[0]['score']
        top_candidates = [s for s in scores if s['score'] == best_score]
        
        # On melange les meilleurs candidats pour eviter de toujours donner le meme
        winner = random.choice(top_candidates)

        elapsed = time.time() - start_time
        print(f"[IA] Gagnant trouve en {elapsed:.4f}s : {winner['slot']}")
        
        return {
            "recommendation": winner['slot'],
            "reasoning": winner['reason'],
            "logs": logs + [f"Temps de calcul: {elapsed:.4f}s"]
        }
