from sqlalchemy import create_engine, text
import subprocess

engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')

with engine.begin() as conn:
    print("Forcage des zones AE, AF, AG dans TCE pour accepter DANGER et CITERNE...")
    conn.execute(text("""
        UPDATE zones_stockage 
        SET types_admis = 'NORMAL, DANGEREUX, CITERNES' 
        WHERE terminal = 'TCE' AND nom IN ('AE', 'AF', 'AG')
    """))
    print("Mise a jour terminee.")

# On relance le pipeline et le fix
print("Relancement du Pipeline ETL...")
subprocess.run(["python", "app/etl/pipeline.py"], check=True)
print("Relancement du Soft OOG Fix...")
subprocess.run(["python", "scratch/soft_oog_fix.py"], check=True)

print("TERMINE ! Maintenant TCE contient des zones Danger/Citerne.")
