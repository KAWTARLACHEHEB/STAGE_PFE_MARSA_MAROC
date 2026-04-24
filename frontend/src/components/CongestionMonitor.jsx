import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export default function CongestionMonitor() {
  const [zones, setZones] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOccupancy = async () => {
      try {
        const res = await axios.get(`${API_URL}/occupancy`);
        setZones(res.data.zones);
      } catch (err) {
        console.error("Erreur Gold View:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchOccupancy();
    const interval = setInterval(fetchOccupancy, 10000); // Sync toutes les 10s
    return () => clearInterval(interval);
  }, []);

  if (loading && Object.keys(zones).length === 0) {
    return (
      <div className="bg-[#001d33] border border-slate-800 rounded-3xl p-8 flex items-center justify-center">
         <div className="text-slate-500 animate-pulse text-xs uppercase font-black tracking-widest">Initialisation des donnees Gold...</div>
      </div>
    );
  }

  // Tri des zones par taux de congestion (les plus critiques en premier)
  const sortedZoneIds = Object.keys(zones).sort((a, b) => zones[b].rate - zones[a].rate);

  return (
    <div className="bg-[#001d33] border border-slate-800 rounded-3xl p-8 shadow-2xl overflow-hidden">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="font-bold text-white uppercase tracking-widest text-xs">
            Analyse de Congestion en Temps Reel
          </h3>
          <p className="text-[10px] text-slate-500 mt-1 uppercase font-bold tracking-tighter">
             Surveillance de 46 Blocs (Couche Medallion Gold)
          </p>
        </div>
        <span className="text-[10px] text-emerald-400 font-bold uppercase flex items-center gap-1 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse inline-block" />
          Synchronise MySQL
        </span>
      </div>

      {/* Zone de Scroll horizontale ou grille limitee */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-h-[400px] overflow-y-auto pr-4 custom-scrollbar">
        {sortedZoneIds.map(zoneId => {
          const zoneData = zones[zoneId];
          const percent = zoneData.rate;
          
          // Couleurs dynamiques Premium
          const colorClass = percent > 85 ? 'bg-gradient-to-r from-red-600 to-orange-500 shadow-[0_0_10px_rgba(239,68,68,0.4)]' 
                           : percent > 50 ? 'bg-gradient-to-r from-amber-500 to-yellow-400' 
                           : 'bg-gradient-to-r from-blue-600 to-cyan-400';
                           
          const label = percent > 85 ? 'CRITIQUE' : percent > 50 ? 'MODERE' : 'FLUIDE';
          const textColor = percent > 85 ? 'text-red-400' : percent > 50 ? 'text-amber-400' : 'text-blue-400';

          return (
            <div key={zoneId} className="space-y-4 bg-slate-950/40 p-5 rounded-2xl border border-slate-800/50 hover:border-[#FF8C00]/30 transition-all group">
              <div className="flex justify-between items-start">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-black text-white group-hover:text-[#FF8C00] transition-colors">{zoneId}</span>
                    <span className="text-[8px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-bold uppercase">
                      {zoneData.type} (Z={zoneData.max_z})
                    </span>
                  </div>
                  <p className={`text-[9px] font-black tracking-widest ${textColor}`}>
                    {label}
                  </p>
                </div>
                <div className="text-right">
                   <span className="text-xl font-black text-white">{Math.round(percent)}%</span>
                </div>
              </div>

              <div className="h-1.5 bg-slate-900 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-1000 ${colorClass}`}
                  style={{ width: `${percent}%` }}
                />
              </div>

              <div className="flex justify-between text-[10px] text-slate-500 font-bold uppercase tracking-tighter">
                <span>{zoneData.count} / {zoneData.capacity} TC</span>
                <span className="text-slate-700">|</span>
                <span>ID: {zoneId}</span>
              </div>
            </div>
          );
        })}
      </div>
      
      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: #001529; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #FF8C00; }
      `}</style>
    </div>
  );
}
