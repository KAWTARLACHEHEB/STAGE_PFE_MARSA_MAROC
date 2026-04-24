"""
main.py - API FastAPI pour le systeme d'optimisation de stacking Marsa Maroc
Routes : /optimize, /predict-tdt, /occupancy, /health
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uvicorn

import pandas as pd
from sqlalchemy import text
from data_loader import YardManager
from smart_optimizer import SmartOptimizer
from ai_logic import get_predictor

# ─── App FastAPI ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Marsa Maroc Stacking Optimizer API",
    description="API d'optimisation intelligente du stacking de conteneurs - PFE",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Chargement au démarrage ────────────────────────────────────────────────────
yard_manager: Optional[YardManager] = None

@app.on_event("startup")
async def startup_event():
    global yard_manager
    print("[API] Chargement du Yard Manager (MySQL mode)...")
    yard_manager = YardManager(db_engine)
    yard_manager.load_data()
    yard_manager.build_stack_map()
    print("[API] Yard Manager pret.")

# ─── Modeles Pydantic ───────────────────────────────────────────────────────────
class ContainerIn(BaseModel):
    reference: str
    dimension: str = "20"
    categorie: str = "import"
    special_type: str = "NORMAL"
    weight: float = 20000.0
    departure_time: str = str(datetime.now().isoformat())


class OptimizeResponse(BaseModel):
    success: bool
    recommendation: str
    reasoning: str
    logs: list[str]
    tdt_prediction: Optional[dict]


from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration DB Gold
db_host = os.getenv("MYSQL_HOST", "127.0.0.1")
db_port = os.getenv("MYSQL_PORT", "3307")
db_user = os.getenv("MYSQL_USER", "root")
db_pass = quote_plus(os.getenv("MYSQL_PASSWORD", "rootpassword"))
db_name = os.getenv("MYSQL_DATABASE", "marsa_maroc_db")
db_engine = create_engine(f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")

# ─── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "Marsa Maroc Stacking Optimizer API v2",
        "docs": "/docs",
        "status": "running",
        "layer": "Medallion Gold Connected"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "yard_piles": len(yard_manager.yard_state) if yard_manager else 0,
        "timestamp": datetime.now().isoformat(),
    }


from smart_optimizer import SmartOptimizer

# Instance de l'optimiseur intelligent
smart_opt = SmartOptimizer(db_engine)

@app.get("/conteneurs")
def get_conteneurs(terminal: str = "TC3", zone: Optional[str] = None):
    try:
        manager = YardManager(db_engine)
        manager.load_data()
        df = manager.df_snapshot
        
        if df.empty:
            return []

        # Nettoyage
        if 'terminal' in df.columns:
            df['terminal'] = df['terminal'].str.strip()
        if 'zone' in df.columns:
            df['zone'] = df['zone'].str.strip()

        # Filtre par Terminal
        df = df[df['terminal'] == terminal]
        
        # Filtre par Zone (optionnel)
        if zone:
            df = df[df['zone'] == zone]
            
        return df.to_dict(orient='records')
    except Exception as e:
        print(f"[API] Erreur conteneurs: {e}")
        return []


@app.get("/occupancy")
def get_occupancy(terminal: str = "TC3"):
    try:
        with db_engine.connect() as conn:
            # On recupere tout, y compris les types admis
            query = text("SELECT nom, type_zone, current_occ, capacite_max, max_z, rate, terminal, min_allee, max_allee, types_admis FROM view_yard_congestion WHERE terminal = :t")
            result = conn.execute(query, {"t": terminal})
            zones_data = {}
            for row in result:
                zones_data[row[0]] = {
                    "type": row[1],
                    "occupancy": row[2],
                    "capacity": row[3],
                    "max_z": row[4],
                    "rate": float(row[5]),
                    "terminal": row[6],
                    "range_allee": f"{row[7]}-{row[8]}" if row[7] is not None else "N/A",
                    "types_admis": row[9] if row[9] else "NORMAL"
                }
            return {"zones": zones_data}
    except Exception as e:
        print(f"[API] Error in occupancy: {e}")
        if yard_manager:
            return {"zones": yard_manager.get_occupancy_stats(), "source": "fallback"}
        return {"zones": {}}


@app.post("/optimize", response_model=OptimizeResponse)
def optimize(container: ContainerIn, terminal: str = "TC3"):
    """
    Calcule la meilleure position via SmartOptimizer (100% Dynamique).
    """
    print(f"[API] Requete d'optimisation recue pour {container.reference}")
    try:
        if not yard_manager:
            print("[API] Erreur: Yard Manager non initialise")
            raise HTTPException(status_code=503, detail="Yard Manager non initialise")

        container_dict = container.dict()

        # 1. Prediction TDT (IA)
        predictor = get_predictor()
        tdt = predictor.predict_tdt(container_dict)
        if tdt["confidence"] != "low - modele non entraine":
            container_dict["departure_time"] = tdt["departure_time_predicted"]

        # 2. Optimisation via la logique SQL Dynamique
        occupancy_res = get_occupancy()
        occupancy = occupancy_res.get("zones", {})
        
        result = smart_opt.calculate_best_slot(container_dict, yard_manager.yard_state, occupancy, terminal=terminal)

        # 3. Enregistrement dans l'historique
        if result["recommendation"]:
            try:
                with db_engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO historique_mouvements (reference, action, slot, terminal, status) 
                        VALUES (:ref, :act, :slot, :term, :stat)
                    """), {
                        "ref": container.reference,
                        "act": "ENTRÉE",
                        "slot": result["recommendation"],
                        "term": terminal,
                        "stat": "SUCCESS"
                    })
                    conn.commit()
            except Exception as e:
                print(f"[API] Erreur log historique: {e}")

        return OptimizeResponse(
            success=result["recommendation"] is not None,
            recommendation=str(result["recommendation"]),
            reasoning=str(result.get("reasoning", "Optimisation standard")),
            logs=result["logs"],
            tdt_prediction=tdt,
        )
    except Exception as e:
        print(f"[API] ERREUR CRITIQUE: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur Interne: {str(e)}")

@app.get("/history")
def get_history(terminal: str = "TC3"):
    try:
        with db_engine.connect() as conn:
            query = text("SELECT * FROM historique_mouvements WHERE terminal = :t ORDER BY horodatage DESC LIMIT 100")
            df = pd.read_sql(query, conn, params={"t": terminal})
            # Conversion des dates pour le JSON
            if not df.empty:
                df['horodatage'] = df['horodatage'].astype(str)
            return df.to_dict(orient="records")
    except Exception as e:
        print(f"[API] Erreur recuperation historique: {e}")
        return []


@app.post("/predict-tdt")
def predict_tdt(container: ContainerIn):
    """Predit uniquement le True Departure Time sans optimiser le slot."""
    predictor = get_predictor()
    return predictor.predict_tdt(container.dict())


@app.post("/train-ai")
def train_ai():
    """Entraine le modele IA sur les donnees disponibles et le sauvegarde."""
    if not yard_manager or yard_manager.df_arrivals is None:
        raise HTTPException(status_code=503, detail="Donnees non chargees")

    predictor = get_predictor()
    metrics = predictor.train(yard_manager.df_arrivals)
    predictor.save()

    return {"success": True, "metrics": metrics}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
