const express = require('express');
const cors = require('cors');
const mysql = require('mysql2/promise');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5001;

app.use(cors());
app.use(express.json());

// Configuration de la connexion MySQL (Root Local)
const pool = mysql.createPool({
  host: process.env.MYSQL_HOST || '127.0.0.1',
  port: 3306,
  user: process.env.MYSQL_USER || 'root',
  password: process.env.MYSQL_PASSWORD || 'Kawtar@123',
  database: process.env.MYSQL_DATABASE || 'marsa_maroc_db',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

async function connectDB() {
  try {
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

const { spawn } = require('child_process');
const path = require('path');

// Route d'optimisation IA
app.post('/api/optimize', (req, res) => {
  const containerData = req.body; // { reference, dimension, categorie, weight, departure_time }

  // Appeler le script Python
  const pythonProcess = spawn('python', [path.join(__dirname, 'bridge.py')]);

  let resultData = '';

  // Envoyer les données au script Python
  pythonProcess.stdin.write(JSON.stringify({ container: containerData }));
  pythonProcess.stdin.end();

  // Récupérer la réponse
  pythonProcess.stdout.on('data', (data) => {
    resultData += data.toString();
  });

  pythonProcess.on('close', (code) => {
    try {
      const result = JSON.parse(resultData);
      res.json({
        success: true,
        recommendation: result, // Contient best_slot ET logs
        logs: result.logs
      });
    } catch (e) {
      res.status(500).json({ success: false, error: "Erreur IA", details: resultData });
    }
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
