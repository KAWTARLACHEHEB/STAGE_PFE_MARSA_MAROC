"""
enforce_zone_specialty.py - Force chaque zone a n'accepter qu'un seul type de conteneur.
Principe : aligner la specialite de chaque conteneur sur celle de sa zone.
"""
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# Mapping specialite -> type_iso_detail representatif (pour coherence visuelle)
SPEC_TO_ISO = {
    'NORMAL':       'DRY STANDARD',
    'FRIGO':        'REEFER',
    'DANGEREUX':    'DANGEREUX (IMDG)',
    'CITERNE':      'TANK',
    'HORS_GABARIT': 'OPEN TOP',
}

p = quote_plus("Kawtar@123")
engine = create_engine(f"mysql+mysqlconnector://root:{p}@127.0.0.1:3306/marsa_maroc_db")

with engine.begin() as conn:
    # 1. Verifier les violations actuelles
    violations = conn.execute(text("""
        SELECT c.zone, z.types_admis, c.specialite, COUNT(*) as nb
        FROM conteneurs c
        JOIN zones_stockage z ON c.zone = z.nom AND c.terminal = z.terminal
        WHERE c.specialite != z.types_admis
        GROUP BY c.zone, z.types_admis, c.specialite
        ORDER BY c.zone
    """)).fetchall()

    print(f"=== AUDIT : {len(violations)} groupes en infraction ===")
    for v in violations[:20]:
        print(f"  Zone {v[0]} (attend: {v[1]}) -> trouve: {v[2]} ({v[3]} conteneurs)")

    if not violations:
        print("Aucune infraction ! La base est deja conforme.")
    else:
        # 2. Forcer la conformite : mettre a jour specialite + type_iso_detail
        result = conn.execute(text("""
            UPDATE conteneurs c
            JOIN zones_stockage z ON c.zone = z.nom AND c.terminal = z.terminal
            SET c.specialite = z.types_admis
            WHERE c.specialite != z.types_admis
        """))
        print(f"\n  -> {result.rowcount} conteneurs mis en conformite.")

        # 3. Mettre a jour type_iso_detail pour rester coherent avec la specialite
        for spec, iso in SPEC_TO_ISO.items():
            conn.execute(text("""
                UPDATE conteneurs SET type_iso_detail = :iso WHERE specialite = :spec
            """), {"iso": iso, "spec": spec})

        # 4. Verifier apres correction
        remaining = conn.execute(text("""
            SELECT COUNT(*) FROM conteneurs c
            JOIN zones_stockage z ON c.zone = z.nom AND c.terminal = z.terminal
            WHERE c.specialite != z.types_admis
        """)).scalar()

        print(f"\n=== RESULTAT FINAL ===")
        print(f"  Infractions restantes : {remaining}")
        print("  Chaque zone n'accepte plus qu'UN seul type de conteneur !")
