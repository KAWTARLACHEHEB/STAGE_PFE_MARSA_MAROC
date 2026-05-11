from sqlalchemy import create_engine, text
import pandas as pd

engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')

def repair_stack_gravity_fast():
    with engine.connect() as conn:
        print("[Repair] Fetching data...")
        df = pd.read_sql(text("SELECT reference, zone, allee, pile, niveau_z, terminal FROM conteneurs"), conn)
        
        # Sort and recalculate
        df = df.sort_values(['terminal', 'zone', 'allee', 'pile', 'niveau_z'])
        df['new_niveau_z'] = df.groupby(['terminal', 'zone', 'allee', 'pile']).cumcount() + 1
        
        # Identify changes
        changed = df[df['niveau_z'] != df['new_niveau_z']]
        print(f"[Repair] Found {len(changed)} containers to adjust.")
        
        if not changed.empty:
            # Batch update using a temporary table approach for speed
            print("[Repair] Creating temp table...")
            conn.execute(text("CREATE TEMPORARY TABLE temp_levels (ref VARCHAR(50), z VARCHAR(20), a INT, p VARCHAR(20), t VARCHAR(20), new_n INT)"))
            
            # Prepare data for batch insert
            batch_data = [
                {"ref": r.reference, "z": r.zone, "a": r.allee, "p": r.pile, "t": r.terminal, "new_n": r.new_niveau_z}
                for r in changed.itertuples()
            ]
            
            # Insert into temp table
            print("[Repair] Loading batch data into temp table...")
            conn.execute(text("""
                INSERT INTO temp_levels (ref, z, a, p, t, new_n) 
                VALUES (:ref, :z, :a, :p, :t, :new_n)
            """), batch_data)
            
            # Perform JOIN update
            print("[Repair] Executing batch update JOIN...")
            conn.execute(text("""
                UPDATE conteneurs c
                JOIN temp_levels tl ON c.reference = tl.ref AND c.zone = tl.z AND c.allee = tl.a AND c.pile = tl.p AND c.terminal = tl.t
                SET c.niveau_z = tl.new_n
            """))
            
            conn.commit()
            print("[Repair] Done! Stacks are now compact (No gaps).")
        else:
            print("[Repair] No gaps found.")

if __name__ == "__main__":
    repair_stack_gravity_fast()
