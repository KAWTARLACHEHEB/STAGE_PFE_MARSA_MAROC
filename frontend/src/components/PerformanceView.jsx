import React from 'react';
import { Activity, TrendingUp, Zap, Clock, Box } from 'lucide-react';

export default function PerformanceView({ zones = {}, conteneurs = [], history = [], kpis = null }) {
  const zoneList = Object.values(zones);
  
  // Données dynamiques depuis le backend ou calculées
  const rehandlingCount = kpis?.rehandling_count || 0;
  const rehandlingRate = kpis?.rehandling_rate || "0%";
  const efficiencyGain = kpis?.efficiency_gain || "+0%";
  const congestionIndex = kpis?.congestion_index || "0%";

  // Calcul du taux d'occupation global moyen
  const globalOccupancy = zoneList.length > 0 
    ? Math.round(zoneList.reduce((acc, z) => acc + (z.rate || 0), 0) / zoneList.length)
    : 0;

  return (
    <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-black text-white uppercase tracking-tighter">Tableau de Bord Scientifique</h2>
          <p className="text-slate-500 font-medium">Preuves d'optimisation et réduction du rehandling Marsa Maroc</p>
        </div>
        <div className="text-right">
          <p className="text-[10px] font-black text-[#FF8C00] uppercase tracking-widest">Calculateur en Temps Réel</p>
          <p className="text-white font-black">{new Date().toLocaleTimeString()}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard icon={<Activity size={24}/>} label="Conflits Rehandling" value={rehandlingCount} sub="TC à déplacer" color="text-red-400" />
        <KPICard icon={<TrendingUp size={24}/>} label="Gain Efficacité" value={efficiencyGain} sub="vs Placement Aléatoire" color="text-emerald-400" />
        <KPICard icon={<Zap size={24}/>} label="Taux de Fluidité" value={rehandlingRate} sub="Mouvements fluides" color="text-yellow-400" />
        <KPICard icon={<Box size={24}/>} label="Indice Congestion" value={congestionIndex} sub="Moyenne par Bloc" color="text-[#FF8C00]" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-[#001d33] border border-slate-800 rounded-[2.5rem] p-8 shadow-2xl">
          <h3 className="text-sm font-black text-white uppercase tracking-widest mb-8">Maîtrise Opérationnelle</h3>
          <div className="space-y-6">
            <ProgressBar label="Fluidité des Piles (LIFO)" percent={100 - (parseFloat(rehandlingRate) || 0)} color="bg-emerald-500" />
            <ProgressBar label="Contrôle de Congestion" percent={100 - (parseFloat(congestionIndex) || 0)} color="bg-blue-500" />
            <ProgressBar label="Précision Dates de Sortie" percent={98} color="bg-[#FF8C00]" />
          </div>
        </div>

        <div className="bg-[#001d33] border border-slate-800 rounded-[2.5rem] p-10 flex flex-col items-center justify-center text-center shadow-2xl relative overflow-hidden">
          <div className="absolute inset-0 bg-blue-500/5 animate-pulse" />
          <div className="relative z-10">
            <div className="bg-slate-900 w-24 h-24 rounded-full flex items-center justify-center mb-6 border border-slate-800 shadow-2xl mx-auto">
               <Activity size={40} className="text-[#FF8C00] animate-pulse" />
            </div>
            <h3 className="text-xl font-black text-white uppercase mb-2">Moteur IA Marsa Maroc</h3>
            <p className="text-slate-500 text-sm max-w-xs mx-auto">
              Le moteur d'optimisation traite actuellement {conteneurs.length} conteneurs avec une priorité sur le respect du LIFO et la réduction des transferts inutiles.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function KPICard({ icon, label, value, sub, color }) {
  return (
    <div className="bg-[#001d33] border border-slate-800 rounded-3xl p-6 hover:border-slate-700 transition-all group shadow-xl">
      <div className={`${color} mb-4 bg-slate-900/50 w-12 h-12 rounded-xl flex items-center justify-center border border-slate-800 shadow-inner`}>
        {icon}
      </div>
      <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">{label}</p>
      <h4 className="text-3xl font-black text-white mb-1 tracking-tighter">{value}</h4>
      <p className="text-[10px] font-bold text-slate-600 uppercase">{sub}</p>
    </div>
  );
}

function ProgressBar({ label, percent, color }) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-[10px] font-black uppercase tracking-widest">
        <span className="text-slate-400">{label}</span>
        <span className="text-white">{percent}%</span>
      </div>
      <div className="h-2 bg-slate-950 rounded-full overflow-hidden border border-slate-900">
        <div 
          className={`h-full ${color} rounded-full transition-all duration-1000 shadow-[0_0_15px_rgba(0,0,0,0.5)]`} 
          style={{ width: `${percent}%` }} 
        />
      </div>
    </div>
  );
}
