from sqlalchemy import create_engine, text
import pandas as pd

engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')

def cull_overfilled_stacks():
    with engine.connect() as conn:
        print("[Cull] Checking for overfilled stacks...")
        
        # 1. Get zones limits
        zones = pd.read_sql(text("SELECT nom, max_z FROM zones_stockage"), conn)
        z_limits = dict(zip(zones['nom'], zones['max_z']))
        
        # 2. Get all containers
        df = pd.read_sql(text("SELECT reference, zone, allee, pile, niveau_z, terminal FROM conteneurs"), conn)
        
        # 3. Identify containers to remove
        to_remove = []
        for idx, row in df.iterrows():
            limit = z_limits.get(row['zone'], 4) # Default 4
            if row['niveau_z'] > limit:
                to_remove.append(row['reference'])
        
        print(f"[Cull] Found {len(to_remove)} containers exceeding height limits.")
        
        if to_remove:
            print(f"[Cull] Removing {len(to_remove)} containers...")
            # Delete by reference
            # Note: Using chunks to avoid large query errors
            chunk_size = 100
            for i in range(0, len(to_remove), chunk_size):
                chunk = to_remove[i:i + chunk_size]
                conn.execute(text("DELETE FROM conteneurs WHERE reference = :ref"), [{"ref": r} for r in chunk])
            
            conn.commit()
            print("[Cull] Height limits enforced successfully.")
        else:
            print("[Cull] No containers found above limits.")

if __name__ == "__main__":
    cull_overfilled_stacks()
