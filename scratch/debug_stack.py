import mysql.connector

try:
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Kawtar@123",
        database="marsa_maroc_db"
    )
    cursor = conn.cursor(dictionary=True)
    
    # Query all levels for a specific stack that had holes
    cursor.execute("SELECT reference, zone, allee, pile, niveau_z FROM conteneurs WHERE zone='01A' AND allee='5' AND pile='ZONE_C' ORDER BY niveau_z")
    rows = cursor.fetchall()
    
    print(f"Results for Zone 01A, Allee 5, Pile ZONE_C:")
    for row in rows:
        print(row)
        
    cursor.close()
    conn.close()
except Exception as e:
    print("Error:", e)
