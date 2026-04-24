import requests
try:
    r = requests.get('http://127.0.0.1:8000/conteneurs?terminal=TC3&zone=01C')
    data = r.json()
    if data:
        print(f"Keys: {list(data[0].keys())}")
        specs = [c.get('specialite') for c in data]
        print(f"Specs in 01C: {set(specs)}")
    else:
        print("No data returned")
except Exception as e:
    print(f"Error: {e}")
