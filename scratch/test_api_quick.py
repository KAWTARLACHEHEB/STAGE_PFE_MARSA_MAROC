import requests

# Test TCE
r = requests.get('http://127.0.0.1:8000/occupancy?terminal=TCE')
d = r.json()
zones = d.get('zones', {})
print(f"TCE: {len(zones)} zones")
for k, v in list(zones.items())[:3]:
    print(f"  {k}: type={v['type']}, occ={v['occupancy']}")

# Test TC3
r2 = requests.get('http://127.0.0.1:8000/occupancy?terminal=TC3')
d2 = r2.json()
z2 = d2.get('zones', {})
print(f"\nTC3: {len(z2)} zones")
for k, v in list(z2.items())[:3]:
    print(f"  {k}: type={v['type']}, occ={v['occupancy']}")

# Test conteneurs (vérifie les nouvelles colonnes)
r3 = requests.get('http://127.0.0.1:8000/conteneurs?terminal=TCE&zone=AE')
data = r3.json()
print(f"\nConteneurs AE: {len(data)}")
if data:
    c = data[0]
    print(f"  Colonnes disponibles: {list(c.keys())}")
    has_flux = 'flux' in c
    print(f"  Colonne 'flux' présente: {has_flux}")
    if has_flux:
        print(f"  Exemple: flux={c.get('flux')}, statut={c.get('statut_import')}, navire={c.get('navire_id')}")
