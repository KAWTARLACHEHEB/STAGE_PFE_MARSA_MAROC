import mysql.connector

try:
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Kawtar@123",
        database="marsa_maroc_db"
    )
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT allee FROM conteneurs")
    rows = cursor.fetchall()
    
    print("Distinct Allee values:")
    for row in rows:
        print(f"'{row[0]}'")
        
    cursor.close()
    conn.close()
except Exception as e:
    print("Error:", e)
