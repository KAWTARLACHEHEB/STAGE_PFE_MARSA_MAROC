import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Ship, Database, Activity, Package, LayoutDashboard, Settings, LogOut, CheckCircle2, AlertCircle } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

function App() {
  const [conteneurs, setConteneurs] = useState([]);
  const [dbStatus, setDbStatus] = useState('checking');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const healthRes = await axios.get(`${API_URL}/health`);
        setDbStatus(healthRes.data.status === 'healthy' ? 'connected' : 'error');
        
        const conteneursRes = await axios.get(`${API_URL}/api/conteneurs`);
        setConteneurs(conteneursRes.data);
      } catch (err) {
        console.error("Erreur API:", err);
        setDbStatus('error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-200 font-sans">
      {/* Sidebar */}
      <div className="fixed left-0 top-0 h-full w-64 bg-[#1e293b] border-r border-slate-700 p-6 hidden lg:block">
        <div className="flex items-center gap-3 mb-12">
          <div className="bg-blue-600 p-2 rounded-lg">
            <Ship size={24} className="text-white" />
          </div>
          <h1 className="text-xl font-bold tracking-tight text-white">Marsa Maroc</h1>
        </div>
        
        <nav className="space-y-2">
          <NavItem icon={<LayoutDashboard size={20}/>} label="Dashboard" active />
          <NavItem icon={<Package size={20}/>} label="Stockage IA" />
          <NavItem icon={<Activity size={20}/>} label="Simulations" />
          <NavItem icon={<Database size={20}/>} label="Données" />
          <div className="pt-8 mt-8 border-t border-slate-700">
            <NavItem icon={<Settings size={20}/>} label="Paramètres" />
            <NavItem icon={<LogOut size={20}/>} label="Déconnexion" />
          </div>
        </nav>
      </div>

      {/* Main Content */}
      <main className="lg:ml-64 p-8">
        {/* Top Header */}
        <header className="flex justify-between items-center mb-10">
          <div>
            <h2 className="text-3-xl font-bold text-white mb-2">Optimisation du Stacking</h2>
            <p className="text-slate-400">Système intelligent de gestion des conteneurs (PFE)</p>
          </div>
          
          <div className="flex items-center gap-4">
            <div className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium ${
              dbStatus === 'connected' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 
              dbStatus === 'checking' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
              'bg-red-500/10 text-red-400 border border-red-500/20'
            }`}>
              {dbStatus === 'connected' ? <CheckCircle2 size={16}/> : <AlertCircle size={16}/>}
              DB: {dbStatus === 'connected' ? 'Connecté' : dbStatus === 'checking' ? 'Vérification...' : 'Erreur'}
            </div>
          </div>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          <StatCard title="Total Conteneurs" value={conteneurs.length} icon={<Package className="text-blue-500"/>} trend="+12% ce mois" />
          <StatCard title="Optimisation IA" value="94.2%" icon={<Activity className="text-purple-500"/>} trend="Score efficacité" />
          <StatCard title="Zones Libres" value="28" icon={<LayoutDashboard className="text-emerald-500"/>} trend="Capacité restante" />
        </div>

        {/* Table Section */}
        <div className="bg-[#1e293b] rounded-2xl border border-slate-700 overflow-hidden shadow-xl">
          <div className="p-6 border-b border-slate-700 flex justify-between items-center">
            <h3 className="font-semibold text-lg text-white">Inventaire Temps Réel</h3>
            <button className="text-sm bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors">
              Nouvelle Simulation
            </button>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-[#161e2e] text-slate-400 text-sm uppercase tracking-wider">
                  <th className="px-6 py-4 font-medium">Référence</th>
                  <th className="px-6 py-4 font-medium">Type</th>
                  <th className="px-6 py-4 font-medium">Poids (kg)</th>
                  <th className="px-6 py-4 font-medium">Destination</th>
                  <th className="px-6 py-4 font-medium">Statut</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {loading ? (
                  <tr>
                    <td colSpan="5" className="px-6 py-10 text-center text-slate-500">Chargement des données...</td>
                  </tr>
                ) : conteneurs.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="px-6 py-10 text-center text-slate-500">Aucun conteneur trouvé</td>
                  </tr>
                ) : (
                  conteneurs.map((c) => (
                    <tr key={c.id} className="hover:bg-slate-800/50 transition-colors">
                      <td className="px-6 py-4 font-mono text-blue-400">{c.reference}</td>
                      <td className="px-6 py-4">{c.type}</td>
                      <td className="px-6 py-4">{parseFloat(c.poids_kg).toLocaleString()}</td>
                      <td className="px-6 py-4">{c.destination}</td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          c.statut === 'en_attente' ? 'bg-amber-500/10 text-amber-400' : 
                          c.statut === 'stacke' ? 'bg-blue-500/10 text-blue-400' :
                          'bg-emerald-500/10 text-emerald-400'
                        }`}>
                          {c.statut}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}

function NavItem({ icon, label, active = false }) {
  return (
    <a href="#" className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
      active ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20' : 'text-slate-400 hover:bg-slate-800 hover:text-white'
    }`}>
      {icon}
      <span className="font-medium">{label}</span>
    </a>
  );
}

function StatCard({ title, value, icon, trend }) {
  return (
    <div className="bg-[#1e293b] p-6 rounded-2xl border border-slate-700 shadow-lg">
      <div className="flex justify-between items-start mb-4">
        <div className="p-3 bg-slate-800 rounded-xl">{icon}</div>
      </div>
      <h4 className="text-slate-400 text-sm font-medium mb-1">{title}</h4>
      <div className="text-2xl font-bold text-white mb-2">{value}</div>
      <div className="text-xs text-slate-500 font-medium">{trend}</div>
    </div>
  );
}

export default App;
