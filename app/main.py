import os
import json
import random
import time
import uvicorn
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List
from contextlib import asynccontextmanager
from urllib.parse import quote_plus
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, text

load_dotenv()

# Configuration DB Gold
db_host = os.getenv("MYSQL_HOST", "127.0.0.1")
db_port = os.getenv("MYSQL_PORT", "3306")
db_user = os.getenv("MYSQL_USER", "root")
db_pass = quote_plus(os.getenv("MYSQL_PASSWORD", "Kawtar@123"))
db_name = os.getenv("MYSQL_DATABASE", "marsa_maroc_db")
db_engine = create_engine(f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}", pool_pre_ping=True)

from data_loader import YardManager
from smart_optimizer import SmartOptimizer
from ai_logic import get_predictor

yard_manager: Optional[YardManager] = None
smart_opt = SmartOptimizer(db_engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global yard_manager
    try:
        yard_manager = YardManager(db_engine)
        yard_manager.load_data()
        yard_manager.build_stack_map()
        print("✅ Yard Manager prêt.")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    yield

app = FastAPI(title="Marsa Maroc API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ContainerIn(BaseModel):
    reference: str
    dimension: str = "20"
    categorie: str = "import"
    special_type: str = "NORMAL"
    weight: float = 20000.0
    departure_time: str = str(datetime.now().isoformat())
    flux: str = "IMPORT"
    statut_import: Optional[str] = None

class OptimizeResponse(BaseModel):
    success: bool
    recommendation: str
    reasoning: str
    logs: List[str]

@app.get("/")
def root(): return {"status": "online", "version": "Gold"}

@app.get("/health")
def health(terminal: str = "TC3"):
    return {"status": "healthy", "yard_piles": len(yard_manager.yard_state) if yard_manager else 0}

@app.get("/conteneurs")
def get_conteneurs(terminal: str = "TC3", zone: Optional[str] = None):
    try:
        terminal = str(terminal).strip().upper()
        with db_engine.connect() as conn:
            query = "SELECT * FROM conteneurs WHERE terminal = :t"
            params = {"t": terminal}
            if zone and zone != "ALL":
                query += " AND zone = :z"
                params["z"] = zone.strip().upper()
            
            res = conn.execute(text(query), params).fetchall()
            df = pd.DataFrame([dict(r._mapping) for r in res])
            if df.empty: return []
            df = df.where(pd.notnull(df), None)
            return json.loads(df.to_json(orient='records'))
    except Exception as e:
        print(f"Error containers API: {e}")
        return []

@app.get("/occupancy")
def get_occupancy(terminal: str = "TC3"):
    try:
        with db_engine.connect() as conn:
            # Reconstruction sécurisée avec accès par nom de colonne pour éviter les décalages
            res = conn.execute(text("SELECT * FROM view_yard_congestion WHERE terminal = :t"), {"t": terminal}).fetchall()
            zones = {}
            for r in res:
                m = r._mapping
                zones[m['nom']] = {
                    "type": m['type_zone'],
                    "current_occ": m['current_occ'],
                    "capacity": m['capacite_max'],
                    "max_z": m['max_z'],
                    "range_allee": f"{m['min_allee']}-{m['max_allee']}" if m['min_allee'] is not None else "1-75",
                    "rate": float(m['rate']) if m['rate'] is not None else 0.0,
                    "types_admis": m['types_admis'] if m['types_admis'] else "NORMAL"
                }
            return {"zones": zones}
    except Exception as e:
        print(f"Error occupancy: {e}")
        return {"zones": {}}

@app.get("/kpi")
def get_kpi(terminal: str = "TC3"):
    try:
        with db_engine.connect() as conn:
            total = conn.execute(text("SELECT COUNT(*) FROM conteneurs WHERE terminal = :t"), {"t": terminal}).scalar() or 0
            avg_occ = conn.execute(text("SELECT AVG(rate) FROM view_yard_congestion WHERE terminal = :t"), {"t": terminal}).scalar() or 0
            
            # Calcul du rehandling réel : un conteneur au-dessus d'un autre qui doit partir plus tôt
            rehandling = conn.execute(text("""
                SELECT COUNT(*) 
                FROM conteneurs c1
                JOIN conteneurs c2 
                  ON c1.zone = c2.zone AND c1.allee = c2.allee 
                 AND c1.pile = c2.pile AND c1.terminal = c2.terminal 
                 AND c1.niveau_z > c2.niveau_z
                WHERE c1.departure_time > c2.departure_time
                  AND c1.terminal = :t
            """), {"t": terminal}).scalar() or 0

            # Calcul du gain de fluidité (inverse du rehandling)
            rehandling_rate = (rehandling / max(total, 1)) * 100
            efficiency = 100 - rehandling_rate
            
            return {
                "total_containers": total,
                "total_tc": total,
                "congestion_index": f"{round(avg_occ, 1)}%",
                "efficiency_gain": f"{round(efficiency, 1)}%",
                "rehandling_count": rehandling,
                "rehandling_rate": f"{round(rehandling_rate, 2)}%"
            }
    except Exception as e:
        print("KPI Error:", e)
        return {}

@app.get("/api/container/{reference}")
def search_container(reference: str):
    """Recherche un conteneur par sa reference et retourne sa localisation complete."""
    try:
        ref = reference.strip().upper()
        with db_engine.connect() as conn:
            row = conn.execute(text("""
                SELECT c.reference, c.zone, c.allee, c.pile, c.niveau_z,
                       c.terminal, c.flux, c.specialite, c.type_iso_detail,
                       c.weight, c.size, c.departure_time,
                       c.status_douane, c.nom_navire, c.pod, c.slot
                FROM conteneurs c
                WHERE UPPER(c.reference) = :ref
                   OR UPPER(c.reference) LIKE :ref_like
                LIMIT 1
            """), {"ref": ref, "ref_like": f"%{ref}%"}).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail=f"Conteneur '{reference}' non trouvé en base de données.")

        m = row._mapping
        niv = int(m['niveau_z']) if m['niveau_z'] else 1

        return {
            "reference":    m['reference'],
            "terminal":     m['terminal'],
            "slot":         m['slot'] or f"{m['zone']}-{m['allee']}-{m['pile']}-N{niv:02d}",
            "flux":         m['flux'],
            "specialite":   m['specialite'],
            "type_iso":     m['type_iso_detail'],
            "statut_import": m['status_douane'],
            "navire_id":    m['nom_navire'],
            "pod":          m['pod'],
            "coords": {
                "bloc":    m['zone'],
                "travee":  str(m['allee']),
                "cellule": str(m['pile']),
                "niveau":  niv,
            },
            "safety_status": "Conforme - Niveau dans les limites" if niv <= 5 else "Attention - Niveau élevé"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def get_history(terminal: str = "TC3"):
    try:
        with db_engine.connect() as conn:
            df = pd.read_sql(text("SELECT * FROM historique_mouvements WHERE terminal = :t ORDER BY horodatage DESC LIMIT 50"), conn, params={"t": terminal})
            return json.loads(df.to_json(orient="records", date_format="iso")) if not df.empty else []
    except: return []

@app.post("/optimize", response_model=OptimizeResponse)
def optimize(container: ContainerIn, terminal: str = "TC3"):
    try:
        res = smart_opt.calculate_best_slot(container.dict(), yard_manager.yard_state if yard_manager else {}, {}, terminal)
        if res["recommendation"]:
            p = res["recommendation"].split('-')
            with db_engine.begin() as conn:
                conn.execute(text("INSERT INTO historique_mouvements (reference, action, slot, terminal, status) VALUES (:ref, 'ENTRÉE', :slot, :term, 'SUCCESS')"), {"ref": container.reference, "slot": res["recommendation"], "term": terminal})
                conn.execute(text("INSERT INTO conteneurs (container_id, reference, type_conteneur, weight, departure_time, terminal, zone, allee, pile, niveau_z, flux, status_douane, size, slot) VALUES (:id, :ref, :type, :weight, :dep, :term, :zone, :allee, :pile, :niv, :flux, :statut, :size, :slot)"), {"id": container.reference, "ref": container.reference, "type": "PLEIN" if container.weight > 5000 else "VIDE", "weight": container.weight, "dep": container.departure_time, "term": terminal, "zone": p[0], "allee": p[1], "pile": p[2], "niv": int(p[3].replace('N','')), "flux": container.flux, "statut": "MAIN_LEVEE", "size": container.dimension, "slot": res["recommendation"]})
            if yard_manager: yard_manager.add_container(container.dict(), res["recommendation"], terminal)
        return OptimizeResponse(success=True, recommendation=res["recommendation"], reasoning=res["reasoning"], logs=res["logs"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/batch_add")
def batch_add(count: int = 10, terminal: str = "TC3"):
    try:
        import random
        from datetime import datetime, timedelta
        
        reasons = []
        specs = ["NORMAL", "FRIGO", "DANGEREUX", "CITERNE", "HORS_GABARIT"]
        isos = {
            "NORMAL": "DRY STANDARD", 
            "FRIGO": "REEFER", 
            "DANGEREUX": "DANGEREUX (IMDG)", 
            "CITERNE": "TANK", 
            "HORS_GABARIT": "OOG / FLAT RACK"
        }
        
        success_count = 0
        with db_engine.begin() as conn:
            for i in range(count):
                ref = f"SIMU-{random.randint(100000, 999999)}"
                spec = random.choices(specs, weights=[0.6, 0.15, 0.1, 0.05, 0.1])[0]
                flux = random.choice(["IMPORT", "EXPORT"])
                weight = random.randint(2000, 30000)
                dep = (datetime.now() + timedelta(days=random.randint(1, 14))).isoformat()
                iso = isos[spec]
                
                c_data = {
                    "reference": ref,
                    "dimension": "20" if random.random() > 0.3 else "40",
                    "special_type": spec,
                    "weight": weight,
                    "departure_time": dep,
                    "flux": flux
                }
                
                res = smart_opt.calculate_best_slot(c_data, yard_manager.yard_state if yard_manager else {}, {}, terminal)
                if res["recommendation"]:
                    p = res["recommendation"].split('-')
                    if len(p) >= 4:
                        zone, allee, pile, niv_str = p[0], p[1], p[2], p[3]
                        niv = int(niv_str.replace('N',''))
                        
                        conn.execute(text("INSERT INTO historique_mouvements (reference, action, slot, terminal, status) VALUES (:ref, 'ENTRÉE', :slot, :term, 'SUCCESS')"), {"ref": ref, "slot": res["recommendation"], "term": terminal})
                        
                        conn.execute(text("""
                            INSERT INTO conteneurs 
                            (container_id, reference, type_conteneur, weight, departure_time, terminal, zone, allee, pile, niveau_z, flux, status_douane, size, slot, specialite, type_iso_detail) 
                            VALUES (:id, :ref, :type, :weight, :dep, :term, :zone, :allee, :pile, :niv, :flux, :statut, :size, :slot, :spec, :iso)
                        """), {
                            "id": ref, "ref": ref, "type": "PLEIN" if weight > 5000 else "VIDE", 
                            "weight": weight, "dep": dep, "term": terminal, "zone": zone, 
                            "allee": allee, "pile": pile, "niv": niv, "flux": flux, 
                            "statut": "MAIN_LEVEE", "size": c_data["dimension"], 
                            "slot": res["recommendation"], "spec": spec, "iso": iso
                        })
                        
                        if yard_manager:
                            yard_manager.add_container(c_data, res["recommendation"], terminal)
                        
                        reasons.append(f"✅ {ref} ({spec}) -> {res['recommendation']}")
                        success_count += 1
                else:
                    reasons.append(f"❌ {ref} ({spec}): Pas de place disponible")
                    
        return {
            "batchCount": success_count,
            "reasoning": "\\n".join(reasons)
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
