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
            ref_grouped = df.groupby('BLOC')['TYPES_ADMIS'].apply(lambda x: set(", ".join(x).replace(" ", "").split(",")))
            return ref_grouped
        return pd.Series()

    def get_dynamic_zones(self, terminal="TC3"):
        print(f"[IA] Recuperation des zones {terminal} depuis MySQL...")
        try:
            with self.engine.connect() as conn:
                query = text("SELECT nom, type_zone, capacite_max, max_z, types_admis FROM zones_stockage WHERE terminal = :t")
                df = pd.read_sql(query, conn, params={"t": terminal})
                print(f"[IA] {len(df)} zones {terminal} recuperees.")
                return df
        except Exception as e:
            print(f"[IA] ERREUR SQL ZONES: {e}")
            raise e

    # ==========================================================================
    # RÈGLE MÉTIER : Vérification de compatibilité Import/Export/Navire/POD
    # ==========================================================================
    def check_compatibility(self, new_container, stack_content):
        """
        Vérifie si un nouveau conteneur peut être posé sur une pile existante.
        Retourne (compatible: bool, raison: str)
        
        Règles :
        1. Interdiction de mélanger Import et Export dans la même pile.
        2. Pour l'Export : interdiction de mélanger deux navires différents.
        3. Pour l'Export : interdiction de mélanger deux POD différents.
        """
        if not stack_content:
            return True, "Pile vide - Compatible"

        new_flux = new_container.get('flux', 'IMPORT').upper()
        
        # Vérifier le flux de la pile existante (on prend le premier conteneur comme référence)
        stack_flux = stack_content[0].get('flux', 'IMPORT').upper()
        
        # Règle 1 : Pas de mélange Import/Export
        if new_flux != stack_flux:
            return False, f"INTERDIT: Mélange {new_flux}/{stack_flux}"
        
        # Règles Export uniquement
        if new_flux == "EXPORT":
            new_navire = new_container.get('navire_id', '')
            new_pod = new_container.get('pod', '')
            stack_navire = stack_content[0].get('navire_id', '')
            stack_pod = stack_content[0].get('pod', '')
            
            # Règle 2 : Même navire obligatoire
            if new_navire and stack_navire and new_navire != stack_navire:
                return False, f"INTERDIT: Navire {new_navire} != {stack_navire}"
            
            # Règle 3 : Même POD obligatoire
            if new_pod and stack_pod and new_pod != stack_pod:
                return False, f"INTERDIT: POD {new_pod} != {stack_pod}"
        
        return True, "Compatible"

    # ==========================================================================
    # SCORE DOUANIER : Priorité de placement pour l'Import
    # ==========================================================================
    def get_customs_score(self, new_container):
        """
        Calcule le score de priorité basé sur le statut douanier.
        MAL_LEVE  = +200 (part bientôt, doit être au sommet)
        FACTURE   = +100 (priorité moyenne)
        EN_COURS  = -100 (reste longtemps, doit aller en bas)
        """
        statut = str(new_container.get('statut_import', '')).upper()
        if statut in ['MAL_LEVE', 'MAIN_LEVEE']:
            return 200, "Main Levée - Priorité HAUTE"
        elif statut == 'FACTURE':
            return 100, "Facturé - Priorité MOYENNE"
        elif statut == 'EN_COURS':
            return -100, "En cours - Priorité BASSE"
        return 0, ""

    def calculate_best_slot(self, new_container, yard_state, occupancy_stats, terminal="TC3"):
        start_time = time.time()
        logs = [f"[IA Marsa] Analyse pour {new_container.get('reference', 'N/A')}"]
        print(f"[IA] Debut du calcul pour {new_container.get('reference')}")
        
        weight = float(new_container.get('weight', 20000))
        c_type = 'PLEIN' if weight > 5000 else 'VIDE'
        c_special = new_container.get('special_type', 'NORMAL').upper().strip()
        # Normalisation
        if c_special == 'CITERNES': c_special = 'CITERNE'
        if c_special == 'DANGER': c_special = 'DANGEREUX'
        
        c_flux = new_container.get('flux', 'IMPORT').upper()
        
        logs.append(f"[IA Marsa] Type: {c_type} | Special: {c_special} | Flux: {c_flux}")

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
            types_admis_str = z.get('types_admis', 'NORMAL')
            if pd.isna(types_admis_str):
                types_admis_str = 'NORMAL'
            
            allowed_types = set([t.strip().upper() for t in types_admis_str.split(',')])
            
            # Match si le type special est accepte, ou si la zone accepte 'TOUS'
            if c_special in allowed_types or 'TOUS' in allowed_types:
                valid_zone_names.append(z_name)
            elif c_special == 'NORMAL' and 'NORMAL' in allowed_types:
                valid_zone_names.append(z_name)

        if not valid_zone_names:
            return {"recommendation": None, "reasoning": f"Aucune zone {terminal} n'accepte le type {c_special}", "logs": logs + [f"Aucune zone n'accepte le type {c_special}"]}

        zone_max_z = dict(zip(compatible_zones['nom'], compatible_zones['max_z']))
        scores = []
        t_new = pd.to_datetime(new_container.get('departure_time'))

        # Score douanier (Import uniquement)
        customs_score, customs_reason = self.get_customs_score(new_container)

        for stack_key, containers in yard_state.items():
            zone = stack_key.split('-')[0]
            if zone not in valid_zone_names: continue

            z_current = len(containers)
            z_limit = zone_max_z.get(zone, 4)

            if z_current >= z_limit: continue
            
            # === RÈGLES DE SÉCURITÉ OOG ===
            # Règle A : Un nouveau conteneur OOG ne peut être posé que sur le sol (Niveau 1)
            if c_special == 'HORS_GABARIT' and z_current > 0:
                continue
                
            # Règle B : Aucun conteneur ne peut être posé sur un OOG existant
            if z_current > 0:
                top_container = containers[-1]
                if top_container.get('special_type') in ['HORS_GABARIT', 'OOG']:
                    continue

            # === VÉRIFICATION DE COMPATIBILITÉ MÉTIER ===
            compatible, compat_reason = self.check_compatibility(new_container, containers)
            if not compatible:
                continue  # On saute cette pile, elle est incompatible

            score = 0
            reason = ""
            if z_current == 0:
                score = 100
                reason = "Pile vide"
            else:
                top = containers[-1]
                # Securite : Fallback si la date est manquante dans la pile
                t_top_raw = top.get('departure_time')
                t_top = pd.to_datetime(t_top_raw) if t_top_raw else pd.to_datetime('2100-01-01')
                
                if t_new <= t_top:
                    score = 200
                    reason = "LIFO Respecte"
                else:
                    score = -500
                    reason = "RISQUE FOUILLE"

            # Ajout du score douanier (Import)
            if customs_score != 0:
                score += customs_score
                reason += f" + {customs_reason}"

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
        print(f"[IA] Gagnant trouve en {elapsed:.4f}s : {winner['slot']} (Flux: {c_flux})")
        
        return {
            "recommendation": winner['slot'],
            "reasoning": winner['reason'],
            "logs": logs + [f"Temps de calcul: {elapsed:.4f}s", f"Flux: {c_flux}"]
        }

    def get_best_slot(self, new_container, terminal="TC3"):
        """Méthode de haut niveau pour main.py"""
        try:
            # 1. Recuperation du yard_state depuis MySQL
            yard_state = {}
            with self.engine.connect() as conn:
                # On recupere les conteneurs triés par niveau
                res = conn.execute(text("""
                    SELECT zone, allee, pile, departure_time, flux 
                    FROM conteneurs 
                    WHERE terminal = :t
                    ORDER BY zone, allee, pile, niveau_z ASC
                """), {"t": terminal}).fetchall()
                
                for r in res:
                    key = f"{r[0]}-{r[1]}-{r[2]}"
                    if key not in yard_state: yard_state[key] = []
                    yard_state[key].append({
                        "departure_time": r[3],
                        "flux": r[4]
                    })
            
            # 2. Recuperation des stats d'occupation
            occupancy_stats = {}
            with self.engine.connect() as conn:
                res = conn.execute(text("""
                    SELECT zone, (COUNT(*)/2000)*100 as rate 
                    FROM conteneurs 
                    WHERE terminal = :t 
                    GROUP BY zone
                """), {"t": terminal}).fetchall()
                for r in res:
                    occupancy_stats[r[0]] = {"rate": r[1]}

            # 3. Calcul
            result = self.calculate_best_slot(new_container, yard_state, occupancy_stats, terminal)
            
            return {
                "success": result["recommendation"] is not None,
                "slot": result["recommendation"],
                "reasoning": result["reasoning"]
            }
        except Exception as e:
            print(f"[IA] ERREUR get_best_slot: {e}")
            return {"success": False, "reasoning": str(e)}
