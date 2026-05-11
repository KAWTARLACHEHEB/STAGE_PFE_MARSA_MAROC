"""
fix_all_stacking.py - Mise en conformite totale du parc de conteneurs.
Actions:
  1. Aligner la specialite de chaque conteneur sur sa zone
  2. Ramener les niveaux > max_z dans les limites en reassignant un niveau libre
  3. Supprimer les doublons de position (meme allee/pile/niveau)
"""
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

p = quote_plus("Kawtar@123")
engine = create_engine(f"mysql+mysqlconnector://root:{p}@127.0.0.1:3306/marsa_maroc_db")

with engine.begin() as conn:
    # ─── ETAPE 1 : Aligner les specialites ───────────────────────────────────
    print("ETAPE 1 : Alignement des specialites...")
    updated_spec = conn.execute(text("""
        UPDATE conteneurs c
        JOIN zones_stockage z ON c.zone = z.nom AND c.terminal = z.terminal
        SET c.specialite = z.types_admis
        WHERE c.specialite != z.types_admis
    """)).rowcount
    print(f"  -> {updated_spec} conteneurs mis a jour (specialite).")

    # ─── ETAPE 2 : Corriger les niveaux hors limites ─────────────────────────
    print("ETAPE 2 : Correction des niveaux hors limites (max_z)...")
    
    # Recuperer les niveaux en infraction
    infractions = conn.execute(text("""
        SELECT c.reference, c.zone, c.allee, c.pile, c.niveau_z, z.max_z
        FROM conteneurs c
        JOIN zones_stockage z ON c.zone = z.nom AND c.terminal = z.terminal
        WHERE c.niveau_z > z.max_z
    """)).fetchall()
    
    print(f"  -> {len(infractions)} conteneurs en infraction de niveau trouves.")
    
    repaired = 0
    for row in infractions:
        ref, zone, allee, pile, current_z, max_z = row
        
        # Trouver le prochain niveau libre dans la meme pile
        new_z = None
        for try_z in range(1, max_z + 1):
            exists = conn.execute(text("""
                SELECT 1 FROM conteneurs 
                WHERE zone = :z AND allee = :a AND pile = :p AND niveau_z = :n
                LIMIT 1
            """), {"z": zone, "a": allee, "p": pile, "n": try_z}).fetchone()
            if not exists:
                new_z = try_z
                break
        
        if new_z:
            new_slot = f"{zone}-{allee}-{pile}-N{new_z:02d}"
            conn.execute(text("""
                UPDATE conteneurs SET niveau_z = :nz, slot = :s WHERE reference = :ref
            """), {"nz": new_z, "s": new_slot, "ref": ref})
            repaired += 1
        else:
            # Chercher une autre pile dans la meme zone avec de la place
            free_slot = conn.execute(text("""
                SELECT allee, pile, MAX(niveau_z) as top
                FROM conteneurs
                WHERE zone = :z
                GROUP BY allee, pile
                HAVING top < :maxz
                LIMIT 1
            """), {"z": zone, "maxz": max_z}).fetchone()
            
            if free_slot:
                na, np_, nz = free_slot
                new_nz = nz + 1
                new_slot = f"{zone}-{na}-{np_}-N{new_nz:02d}"
                conn.execute(text("""
                    UPDATE conteneurs 
                    SET allee = :a, pile = :p, niveau_z = :nz, slot = :s 
                    WHERE reference = :ref
                """), {"a": na, "p": np_, "nz": new_nz, "s": new_slot, "ref": ref})
                repaired += 1

    print(f"  -> {repaired} conteneurs repositionnes dans les limites autorisees.")

    # ─── ETAPE 3 : Supprimer les doublons de position ────────────────────────
    print("ETAPE 3 : Suppression des doublons de position...")
    
    # Garder seulement le premier (par container_id) pour chaque position unique
    dupes_removed = conn.execute(text("""
        DELETE c1 FROM conteneurs c1
        INNER JOIN conteneurs c2
        WHERE c1.zone = c2.zone
          AND c1.allee = c2.allee
          AND c1.pile = c2.pile
          AND c1.niveau_z = c2.niveau_z
          AND c1.container_id > c2.container_id
    """)).rowcount
    print(f"  -> {dupes_removed} doublons supprimes.")

    print("\nNettoyage complet ! La base de donnees est maintenant conforme.")
