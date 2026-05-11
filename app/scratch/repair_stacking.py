import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

def repair_stacking():
    p = quote_plus("Kawtar@123")
    engine = create_engine(f"mysql+mysqlconnector://root:{p}@127.0.0.1:3306/marsa_maroc_db")
    
    print("Début de la réparation du stacking...")
    
    with engine.begin() as conn:
        # 1. Récupérer les limites de chaque zone
        zones = conn.execute(text("SELECT nom, max_z, terminal FROM zones_stockage")).fetchall()
        zone_limits = {row[0]: row[1] for row in zones}
        
        repaired_total = 0
        
        for zone_name, max_z in zone_limits.items():
            # 2. Trouver les conteneurs en infraction dans cette zone
            infractions = conn.execute(text(
                "SELECT reference, niveau_z FROM conteneurs WHERE zone = :z AND niveau_z > :maxz"
            ), {"z": zone_name, "maxz": max_z}).fetchall()
            
            if not infractions:
                continue
                
            print(f"Zone {zone_name}: {len(infractions)} infractions trouvées (Max Z={max_z})")
            
            # 3. Trouver des slots libres dans cette même zone (Niveau <= Max Z)
            # On va chercher les combinaisons Allee/Pile/Niveau qui ne sont pas dans la table conteneurs
            # Pour simplifier, on va chercher les piles qui ont de la place
            
            for container in infractions:
                ref = container[0]
                
                # Chercher une pile avec de la place (Niveau < Max Z)
                # On essaie de trouver une allée/pile au hasard qui n'est pas pleine
                target_slot = conn.execute(text("""
                    SELECT allee, pile, MAX(niveau_z) as current_max
                    FROM conteneurs 
                    WHERE zone = :z 
                    GROUP BY allee, pile
                    HAVING current_max < :maxz
                    LIMIT 1
                """), {"z": zone_name, "maxz": max_z}).fetchone()
                
                if target_slot:
                    new_allee = target_slot[0]
                    new_pile = target_slot[1]
                    new_z = target_slot[2] + 1
                    
                    new_slot_str = f"{zone_name}-{new_allee}-{new_pile}-N{new_z:02d}"
                    
                    conn.execute(text("""
                        UPDATE conteneurs 
                        SET allee = :a, pile = :p, niveau_z = :z, slot = :s 
                        WHERE reference = :ref
                    """), {"a": new_allee, "p": new_pile, "z": new_z, "s": new_slot_str, "ref": ref})
                    
                    repaired_total += 1
                else:
                    # Si aucune pile n'a de place, on cherche une nouvelle allée/pile vide
                    # (Hypothèse: il reste de la place dans la zone)
                    print(f"  [!] Attention: Zone {zone_name} semble pleine ou saturée pour redistribuer {ref}")

        print(f"Réparation terminée. {repaired_total} conteneurs ont été repositionnés sans suppression.")

if __name__ == "__main__":
    repair_stacking()
