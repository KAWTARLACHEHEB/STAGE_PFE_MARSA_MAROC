import requests

try:
    print("Test de l'API /occupancy...")
    r_occ = requests.get('http://127.0.0.1:8000/occupancy?terminal=TC3')
    print('Status /occupancy:', r_occ.status_code)
    
    print("\nTest de l'API /conteneurs...")
    r_cont = requests.get('http://127.0.0.1:8000/conteneurs?terminal=TC3')
    print('Status /conteneurs:', r_cont.status_code)
    
    d = r_cont.json()
    print(f'Nombre de conteneurs renvoyés: {len(d)}')
    
    if len(d) > 0:
        c = d[0]
        print("\nExemple de données du premier conteneur:")
        print(f"  Reference: {c.get('reference')}")
        print(f"  Flux: {c.get('flux')}")
        print(f"  Statut Import: {c.get('statut_import')}")
        print(f"  Navire: {c.get('navire_id')}")
        print(f"  POD: {c.get('pod')}")
        print("Le JSON a été sérialisé avec succès (pas de plantage sur les NaN) ! ✅")
except Exception as e:
    print(f"Erreur lors du test: {e}")
