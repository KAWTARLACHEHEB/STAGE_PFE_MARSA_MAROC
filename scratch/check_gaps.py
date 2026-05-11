from sqlalchemy import create_engine, text
import pandas as pd

engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')

with engine.connect() as conn:
    print("Checking for gaps in stacks...")
    query = text("""
        SELECT terminal, zone, allee, pile, GROUP_CONCAT(niveau_z ORDER BY niveau_z ASC) as levels, COUNT(*) as count
        FROM conteneurs
        GROUP BY terminal, zone, allee, pile
    """)
    df = pd.read_sql(query, conn)
    
    def find_gaps(levels_str):
        levels = [int(l) for l in str(levels_str).split(',')]
        if not levels: return None
        expected = list(range(min(levels), max(levels) + 1))
        gaps = set(expected) - set(levels)
        return list(gaps) if gaps else None

    df['gaps'] = df['levels'].apply(find_gaps)
    gaps_df = df[df['gaps'].notnull()]
    
    if gaps_df.empty:
        print("No gaps found in any stacks.")
    else:
        print(f"Found {len(gaps_df)} stacks with gaps:")
        print(gaps_df[['terminal', 'zone', 'allee', 'pile', 'levels', 'gaps']].head(20))
