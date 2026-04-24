import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Ship, Package, Activity, Settings, 
  Search, Filter, Database, Clock, 
  Map as MapIcon, LayoutDashboard,
  Thermometer, AlertTriangle, Truck
} from 'lucide-react';

// Import des nouveaux composants (que nous allons creer juste apres)
import Header from './components/Header';
import FilterBar from './components/FilterBar';
import YardGrid from './components/YardGrid';
import OptimizationPanel from './components/OptimizationPanel';
import InventoryTable from './components/InventoryTable';
import HistoryView from './components/HistoryView';
import PerformanceView from './components/PerformanceView';
import StackView3D from './components/StackView3D';

const API_URL = 'http://127.0.0.1:8000';

function App() {
  const [activeTab, setActiveTab] = useState('Supervision');
  const [terminal, setTerminal] = useState('TC3');
  const [filterType, setFilterType] = useState('ALL'); 
  const [containerCategory, setContainerCategory] = useState('NORMAL');
  const [zones, setZones] = useState({});
  const [conteneurs, setConteneurs] = useState([]);
  const [dbStatus, setDbStatus] = useState('checking');
  const [loading, setLoading] = useState(true);
  const [simulationResult, setSimulationResult] = useState(null);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [terminal]);

  const fetchData = async () => {
    try {
      const [health, occupancy, containers, historyRes] = await Promise.all([
        axios.get(`${API_URL}/health`),
        axios.get(`${API_URL}/occupancy?terminal=${terminal}`),
        axios.get(`${API_URL}/conteneurs?terminal=${terminal}`),
        axios.get(`${API_URL}/history?terminal=${terminal}`)
      ]);
      
      setDbStatus(health.data.status === 'healthy' ? 'connected' : 'error');
      setZones(occupancy.data.zones || {});
      setConteneurs(containers.data || []);
      setHistory(historyRes.data || []);
    } catch (err) {
      setDbStatus('error');
      console.error("API Error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleOptimize = async (formData) => {
    setIsOptimizing(true);
    try {
      const res = await axios.post(`${API_URL}/optimize?terminal=${terminal}`, formData);
      setSimulationResult({
        slot: res.data.recommendation,
        reasoning: res.data.reasoning
      });
      fetchData();
    } catch (err) {
      alert("Erreur d'optimisation: " + (err.response?.data?.detail || err.message));
    } finally {
      setIsOptimizing(false);
    }
  };

  const [selectedZone3D, setSelectedZone3D] = useState(null);

  return (
    <div className="min-h-screen bg-[#020617] text-slate-300 font-sans flex overflow-hidden selection:bg-[#FF8C00]/30">
      
      {/* 3D View Modal Overlay */}
      {selectedZone3D && (
        <StackView3D 
          zoneName={selectedZone3D} 
          terminal={terminal} 
          onClose={() => setSelectedZone3D(null)} 
        />
      )}

      {/* Sidebar Strategique */}
      <aside className="w-20 lg:w-64 bg-[#001529] border-r border-white/5 flex flex-col transition-all duration-500">
        <div className="p-6 flex items-center gap-3">
          <div className="bg-[#0066cc] p-2 rounded-xl shadow-lg shadow-blue-500/20">
            <Ship size={24} className="text-white" />
          </div>
          <span className="hidden lg:inline text-lg font-black text-white tracking-tighter uppercase">
            Marsa <span className="text-[#0066cc]">Maroc</span>
          </span>
        </div>

        <nav className="flex-1 px-4 py-8 space-y-4">
          <NavItem 
            icon={<LayoutDashboard size={20}/>} 
            label="Supervision" 
            active={activeTab === 'Supervision'} 
            onClick={() => setActiveTab('Supervision')}
          />
          <NavItem 
            icon={<MapIcon size={20}/>} 
            label="Inventaire" 
            active={activeTab === 'Inventaire'} 
            onClick={() => setActiveTab('Inventaire')}
          />
          <NavItem 
            icon={<Database size={20}/>} 
            label="Historique" 
            active={activeTab === 'Historique'} 
            onClick={() => setActiveTab('Historique')}
          />
          <NavItem 
            icon={<Activity size={20}/>} 
            label="Performances" 
            active={activeTab === 'Performances'} 
            onClick={() => setActiveTab('Performances')}
          />
        </nav>

        <div className="p-6 border-t border-slate-800">
          <div className="flex items-center gap-3 mb-4">
            <div className={`w-2 h-2 rounded-full ${dbStatus === 'connected' ? 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.8)]' : 'bg-red-500'}`} />
            <span className="hidden lg:inline text-[10px] font-bold uppercase tracking-widest text-slate-500">Systeme Live</span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col relative h-screen overflow-hidden">
        <Header terminal={terminal} setTerminal={setTerminal} />
        
        <div className="flex-1 overflow-y-auto p-4 lg:p-10 space-y-10 bg-gradient-to-br from-[#020617] via-[#001529] to-[#001d33]">
          {activeTab === 'Supervision' && (
            <div className="grid grid-cols-12 gap-8 animate-in fade-in duration-500">
              <div className="col-span-12 xl:col-span-8 space-y-8">
                <FilterBar 
                  filterType={filterType} 
                  setFilterType={setFilterType}
                  containerCategory={containerCategory}
                  setContainerCategory={setContainerCategory}
                  zones={zones}
                />
                <YardGrid 
                  zones={zones} 
                  filterType={filterType} 
                  category={containerCategory} 
                  loading={loading} 
                  onOpen3D={setSelectedZone3D}
                />
              </div>
              <div className="col-span-12 xl:col-span-4 space-y-6">
                <OptimizationPanel 
                  onOptimize={handleOptimize} 
                  isOptimizing={isOptimizing} 
                  simulationResult={simulationResult} 
                />
                <div className="bg-[#001d33]/50 border border-slate-800 rounded-3xl p-6 backdrop-blur-sm">
                  <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-4">Global Kpis</h4>
                  <div className="grid grid-cols-2 gap-4">
                     <StatMini label="Taux Moyen" value={`${Math.round(Object.values(zones).reduce((acc, z) => acc + (z.rate || 0), 0) / (Object.keys(zones).length || 1))}%`} color="text-blue-400" />
                     <StatMini label="Stock Actuel" value={conteneurs.length} color="text-orange-400" />
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'Inventaire' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-left-4 duration-500">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-3xl font-black text-white uppercase tracking-tighter">Inventaire National</h2>
                  <p className="text-slate-500">Registre en temps réel des conteneurs sur le parc Marsa Maroc</p>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl px-6 py-3 text-sm font-black text-[#FF8C00] shadow-xl">
                  TOTAL: {conteneurs.length.toLocaleString()} TC
                </div>
              </div>
              <InventoryTable conteneurs={conteneurs} />
            </div>
          )}

          {activeTab === 'Historique' && <HistoryView history={history} />}
          {activeTab === 'Performances' && <PerformanceView zones={zones} conteneurs={conteneurs} history={history} />}
        </div>
      </main>
    </div>
  );
}

function NavItem({ icon, label, active = false, onClick }) {
  return (
    <button 
      onClick={onClick}
      className={`w-full flex items-center gap-4 px-4 py-3 rounded-xl transition-all group ${
        active ? 'bg-gradient-to-r from-[#FF8C00] to-orange-600 text-white shadow-xl shadow-orange-900/20' : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/50'
      }`}
    >
      {icon}
      <span className="hidden lg:inline font-black uppercase tracking-tighter text-[10px]">{label}</span>
    </button>
  );
}

function StatMini({ label, value, color }) {
  return (
    <div className="bg-slate-900/50 p-3 rounded-2xl border border-slate-800">
      <p className="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-1">{label}</p>
      <p className={`text-xl font-black ${color}`}>{value}</p>
    </div>
  );
}

export default App;
