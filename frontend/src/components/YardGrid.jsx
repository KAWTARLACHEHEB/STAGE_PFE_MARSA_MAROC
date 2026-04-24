import React from 'react';
import { motion } from 'framer-motion';
import { Box, Thermometer, AlertTriangle, Zap, CheckCircle2 } from 'lucide-react';

export default function YardGrid({ zones = {}, filterType = 'ALL', category = 'NORMAL', loading = false, onOpen3D }) {
  const zoneEntries = Object.entries(zones || {});
  
  // Filtrage intelligent
  const filteredZones = zoneEntries.filter(([name, data]) => {
    if (filterType === 'ALL') return true;
    // Les types dans la DB sont PLEIN et VIDE
    return data.type === filterType;
  });

  return (
    <div className="relative">
      {loading && (
        <div className="absolute inset-0 bg-slate-950/50 backdrop-blur-sm z-50 flex items-center justify-center rounded-3xl">
          <div className="flex flex-col items-center gap-4">
            <div className="w-12 h-12 border-4 border-[#FF8C00] border-t-transparent rounded-full animate-spin" />
            <p className="text-[#FF8C00] font-black uppercase tracking-widest text-xs">Synchronisation Live...</p>
          </div>
        </div>
      )}
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {filteredZones.length > 0 ? (
          filteredZones.map(([name, data]) => {
            const admittedTypes = (data.types_admis || "NORMAL").toUpperCase();
            let searchType = category.toUpperCase();
            if (searchType === 'OOG') searchType = 'HORS_GABARIT';
            
            const isMatch = admittedTypes.includes(searchType) || admittedTypes.includes('TOUS');
            
            return (
              <ZoneCard 
                key={name} 
                name={name} 
                data={data} 
                isDimmed={!isMatch}
                onOpen3D={() => onOpen3D(name)}
              />
            );
          })
        ) : (
          <div className="col-span-full h-64 flex items-center justify-center border-2 border-dashed border-slate-800 rounded-[2.5rem] bg-slate-900/20">
            <p className="text-slate-500 font-black uppercase tracking-widest text-sm">Aucune zone de type {filterType} trouvée.</p>
          </div>
        )}
      </div>
    </div>
  );
}

function ZoneCard({ name, data, isDimmed, onOpen3D }) {
  const isFull = data.rate >= 90;
  const isSpecial = name.includes('01') || name.includes('02');

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: isDimmed ? 0.3 : 1, y: 0 }}
      whileHover={{ y: isDimmed ? 0 : -5, scale: isDimmed ? 1 : 1.02 }}
      className={`relative group bg-[#001d33] border ${isFull ? 'border-red-900/50' : 'border-slate-800'} rounded-[2.5rem] p-6 transition-all shadow-xl hover:shadow-orange-500/5 overflow-hidden ${isDimmed ? 'grayscale-[0.5]' : ''}`}
    >
      {/* Background Glow */}
      <div className="absolute -right-4 -top-4 w-24 h-24 bg-[#FF8C00]/5 rounded-full blur-3xl group-hover:bg-[#FF8C00]/10 transition-colors" />

      {/* Hover Info Overlay */}
      <div className="absolute inset-0 bg-slate-950/90 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center p-6 text-center backdrop-blur-sm z-20">
        <p className="text-[#FF8C00] text-[10px] font-black uppercase tracking-widest mb-2">Détails du Bloc</p>
        <div className="grid grid-cols-2 gap-4 w-full text-[9px] font-bold text-white uppercase">
          <div className="bg-slate-900 p-2 rounded-lg border border-slate-800">Travees: {data.range_allee}</div>
          <div className="bg-slate-900 p-2 rounded-lg border border-slate-800">Max Z: {data.max_z}</div>
          <div className="col-span-2 bg-slate-900 p-2 rounded-lg border border-slate-800">Types: {data.types_admis}</div>
        </div>
        <button 
          onClick={(e) => { e.stopPropagation(); onOpen3D(); }}
          className="mt-4 px-6 py-2 bg-[#FF8C00] text-white text-[9px] font-black uppercase rounded-xl hover:bg-orange-600 transition-colors"
        >
          Ouvrir Plan 3D
        </button>
      </div>

      <div className="flex justify-between items-start mb-6">
        <div className="flex items-center gap-3">
          <div className={`p-3 rounded-2xl ${data.type === 'PLEIN' ? 'bg-blue-500/10 text-blue-400' : 'bg-emerald-500/10 text-emerald-400'} border border-white/5`}>
            {data.type === 'PLEIN' ? <Box size={18} /> : <Zap size={18} />}
          </div>
          <div>
            <h4 className="text-xl font-black text-white tracking-tighter uppercase">{name}</h4>
            <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest">{data.type} ZONE</p>
          </div>
        </div>
        {isSpecial && (
          <div className="bg-[#FF8C00]/10 border border-[#FF8C00]/20 p-1.5 rounded-lg">
            <Thermometer size={14} className="text-[#FF8C00]" />
          </div>
        )}
      </div>

      <div className="space-y-4">
        <div className="flex justify-between items-end mb-1">
          <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Occupation</span>
          <span className={`text-sm font-black ${isFull ? 'text-red-400' : 'text-white'}`}>{Math.round(data.rate)}%</span>
        </div>
        
        <div className="h-1.5 w-full bg-slate-950 rounded-full overflow-hidden border border-slate-900">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: `${data.rate}%` }}
            transition={{ duration: 1, delay: 0.5 }}
            className={`h-full rounded-full ${
              data.rate > 85 ? 'bg-gradient-to-r from-red-600 to-red-400' : 
              data.rate > 50 ? 'bg-gradient-to-r from-[#FF8C00] to-orange-400' : 
              'bg-gradient-to-r from-emerald-600 to-emerald-400'
            } shadow-[0_0_10px_rgba(0,0,0,0.5)]`}
          />
        </div>

        <div className="flex justify-between items-center pt-2">
          <div className="flex -space-x-2">
            {[1, 2, 3].map(j => (
              <div key={j} className="w-5 h-5 rounded-full bg-slate-800 border-2 border-[#001d33] flex items-center justify-center text-[7px] font-bold text-slate-500">
                {j}
              </div>
            ))}
          </div>
          <div className="flex items-center gap-1.5">
             <CheckCircle2 size={12} className="text-emerald-500" />
             <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">{data.occupancy} / {data.capacity} TC</span>
          </div>
        </div>
      </div>

      {/* Hover Info Overlay */}
      <div className="absolute inset-0 bg-slate-950/90 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center p-6 text-center backdrop-blur-sm">
        <p className="text-[#FF8C00] text-[10px] font-black uppercase tracking-widest mb-2">Détails du Bloc</p>
        <div className="grid grid-cols-2 gap-4 w-full text-[9px] font-bold text-white uppercase">
          <div className="bg-slate-900 p-2 rounded-lg border border-slate-800">Travees: {data.range_allee}</div>
          <div className="bg-slate-900 p-2 rounded-lg border border-slate-800">Max Z: {data.max_z}</div>
          <div className="col-span-2 bg-slate-900 p-2 rounded-lg border border-slate-800">Types: NORMAL, FRIGO</div>
        </div>
        <button className="mt-4 text-[9px] font-black text-white bg-[#FF8C00] px-4 py-2 rounded-full uppercase tracking-widest shadow-lg shadow-orange-900/40">
          Ouvrir Plan 3D
        </button>
      </div>
    </motion.div>
  );
}
