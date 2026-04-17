const express = require('express');
const cors = require('cors');
const mysql = require('mysql2/promise');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Configuration de la connexion MySQL
const dbConfig = {
  host: process.env.MYSQL_HOST || 'db',
  user: process.env.MYSQL_USER || 'marsa_user',
  password: process.env.MYSQL_PASSWORD || 'marsa_password',
  database: process.env.MYSQL_DATABASE || 'marsa_maroc_db',
  port: process.env.MYSQL_PORT || 3306,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
};

let pool;

async function connectDB() {
  try {
    pool = mysql.createPool(dbConfig);
    // Test de connexion
    const [rows] = await pool.query('SELECT 1');
    console.log('✅ Connecté à la base de données MySQL Marsa Maroc');
  } catch (error) {
    console.error('❌ Erreur de connexion DB:', error.message);
    setTimeout(connectDB, 5000); // Réessayer dans 5s
  }
}

connectDB();

// Routes
app.get('/', (req, res) => {
  res.json({
    message: "Marsa Maroc Stacking Optimizer API (Node.js) Ready ✅",
    stack: "Node.js, Express, MySQL",
    pfe: "Optimisation du stacking de conteneurs"
  });
});

app.get('/api/conteneurs', async (req, res) => {
  try {
    const [rows] = await pool.query('SELECT * FROM conteneurs');
    res.json(rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/health', async (req, res) => {
  try {
    const start = Date.now();
    await pool.query('SELECT 1');
    const latency = Date.now() - start;
    res.json({ 
      status: 'healthy', 
      database: 'connected', 
      latency: `${latency}ms` 
    });
  } catch (error) {
    res.status(503).json({ status: 'degraded', database: 'unreachable' });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Serveur backend lancé sur http://localhost:${PORT}`);
});
