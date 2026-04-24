import mysql.connector
from mysql.connector import errorcode
import sys

# --- CONFIGURATION ROOT (A modifier selon votre mot de passe) ---
ROOT_CONFIG = {
    'user': 'root',
    'password': 'Kawtar@123', # LAISSEZ VIDE OU METTEZ VOTRE MOT DE PASSE ROOT
    'host': '127.0.0.1',
}

DB_NAME = 'marsa_maroc_db'

def setup_marsa_db():
    try:
        print("Connexion a MySQL en tant que root...")
        cnx = mysql.connector.connect(**ROOT_CONFIG)
        cursor = cnx.cursor()

        # 1. Création de la base
        print(f"Creation de la base de données {DB_NAME}...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
        
        # 2. Création de l'utilisateur
        print("Creation de l'utilisateur marsa_user...")
        try:
            cursor.execute("CREATE USER 'marsa_user'@'localhost' IDENTIFIED BY 'marsa_password'")
        except:
            print("   (L'utilisateur existe deja)")
            
        print("Attribution des droits...")
        cursor.execute(f"GRANT ALL PRIVILEGES ON {DB_NAME}.* TO 'marsa_user'@'localhost'")
        cursor.execute("FLUSH PRIVILEGES")

        # 3. Création des tables
        cnx.database = DB_NAME
        
        TABLES = {}
        TABLES['conteneurs'] = (
            "CREATE TABLE IF NOT EXISTS `conteneurs` ("
            "  `id` int AUTO_INCREMENT PRIMARY KEY,"
            "  `reference` varchar(50) NOT NULL UNIQUE,"
            "  `dimension` enum('20','40') NOT NULL,"
            "  `categorie` enum('import','export','transit') NOT NULL,"
            "  `poids_kg` decimal(10,2),"
            "  `zone` enum('A','B','C','D'),"
            "  `niveau_z` int DEFAULT 0,"
            "  `statut` enum('en_attente','stacke','expedie') DEFAULT 'en_attente',"
            "  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP"
            ") ENGINE=InnoDB"
        )
        
        TABLES['zones'] = (
            "CREATE TABLE IF NOT EXISTS `zones_stockage` ("
            "  `id` int AUTO_INCREMENT PRIMARY KEY,"
            "  `nom` enum('A','B','C','D') NOT NULL,"
            "  `capacite_max` int NOT NULL,"
            "  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP"
            ") ENGINE=InnoDB"
        )

        for table_name in TABLES:
            print(f"Creation de la table {table_name}...")
            cursor.execute(TABLES[table_name])

        # 4. Données de test
        print("Insertion des zones et donnees de test...")
        cursor.execute("INSERT IGNORE INTO zones_stockage (nom, capacite_max) VALUES ('A', 500), ('B', 500), ('C', 300), ('D', 300)")
        cursor.execute("INSERT IGNORE INTO conteneurs (reference, dimension, categorie, zone, niveau_z, statut) VALUES ('TEST-001', '20', 'import', 'A', 1, 'stacke')")

        cnx.commit()
        print("\nBASE DE DONNEES MARSA MAROC PRETE !")
        
        cursor.close()
        cnx.close()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("❌ Erreur : Mauvais mot de passe root.")
        else:
            print(f"❌ Erreur : {err}")

if __name__ == "__main__":
    setup_marsa_db()
