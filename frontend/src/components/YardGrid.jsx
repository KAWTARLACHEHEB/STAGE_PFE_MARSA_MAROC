import React from 'react';
import { motion } from 'framer-motion';
import { Box, Thermometer, AlertTriangle, Zap, CheckCircle2 } from 'lucide-react';

export default function YardGrid({ zones = {}, filterType = 'ALL', category = 'NORMAL', fluxFilter = 'ALL', statsMapping = {}, loading = false, onOpen3D, highlightedSlot = null }) {
  const zoneEntries = Object.entries(zones || {});
  
  // StatsMapping est maintenant reçu via les props pour une synchronisation parfaite avec les compteurs du header

  // Auto-scroll vers la zone mise en evidence
  React.useEffect(() => {
    if (highlightedSlot) {
        const [bloc] = highlightedSlot.split('-');
        const element = document.getElementById(`zone-card-${bloc}`);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
  }, [highlightedSlot]);

  // Filtrage intelligent des zones : On masque les zones qui n'ont aucune activité pour le flux sélectionné
  const filteredZones = zoneEntries.filter(([name, data]) => {
    const zoneStats = statsMapping[name] || { IMPORT: 0, EXPORT: 0, total: 0 };
    const currentFluxCount = fluxFilter === 'ALL' ? zoneStats.total : (zoneStats[fluxFilter] || 0);
    
    // Si on filtre par IMPORT ou EXPORT, on cache les zones vides pour ce flux spécifique
    if (fluxFilter !== 'ALL' && currentFluxCount === 0) return false;
    
    return true;
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
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 lg:gap-6">
        {filteredZones.length > 0 ? (
          filteredZones.map(([name, data]) => {
            const admittedType = (data.types_admis || "NORMAL").trim().toUpperCase();
            const searchType = category.toUpperCase().trim();
            
            // === LOGIQUE DE FILTRAGE : valeurs identiques à la DB ===
            // 1. Filtre Spécialité : Robuste
            const isCategoryMatch = admittedType === 'TOUS' || admittedType.includes(searchType) || searchType.includes(admittedType);
            
            // 2. Filtre Plein/Vide : STRICT
            const isTypeMatch = filterType === 'ALL' || data.type === filterType;
            
            // 3. Filtre Flux : Calcul précis pour l'affichage
            const zoneStats = statsMapping[name] || { IMPORT: 0, EXPORT: 0, total: 0 };
            const currentFluxCount = fluxFilter === 'ALL' ? zoneStats.total : (zoneStats[fluxFilter] || 0);
            
            // La zone est "dimmed" si elle ne correspond pas à la spécialité ou au type (Plein/Vide)
            // Le flux a déjà filtré la liste au-dessus
            const isDimmed = !(isCategoryMatch && isTypeMatch);
            
            // On clone les données pour injecter l'occupation filtrée sans toucher à l'original
            const displayData = { 
                ...data, 
                occupancy: currentFluxCount,
                rate: fluxFilter === 'ALL' ? data.rate : (currentFluxCount / data.capacity) * 100
            };

            return (
              <ZoneCard 
                key={name} 
                id={`zone-card-${name}`}
                name={name} 
                data={displayData} 
                isDimmed={isDimmed}
                fluxFilter={fluxFilter}
                isSpecialMatch={isCategoryMatch && searchType !== 'NORMAL'}
                isHighlighted={highlightedSlot && highlightedSlot.startsWith(name)}
                onOpen3D={() => onOpen3D(name)}
              />
            );
          })
        ) : (
          <div className="col-span-full h-80 flex items-center justify-center border-2 border-dashed border-slate-800 rounded-[3rem] bg-slate-900/20">
            <p className="text-slate-500 font-black uppercase tracking-widest text-lg">Aucune zone de type {filterType} trouvée.</p>
          </div>
        )}
      </div>
    </div>
  );
}

function ZoneCard({ name, data, isDimmed, onOpen3D, isHighlighted, id, isSpecialMatch, fluxFilter }) {
  const isFull = data.rate >= 90;
  const isSpecial = name.includes('01') || name.includes('02');

  return (
    <motion.div 
      id={id}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: isDimmed ? 0.15 : 1, y: 0 }}
      whileHover={{ y: (isDimmed || isHighlighted) ? 0 : -5, scale: (isDimmed || isHighlighted) ? 1 : 1.01 }}
      className={`relative group bg-[#001d33]/80 border-2 ${
        isHighlighted ? 'border-orange-500 shadow-[0_0_40px_rgba(255,140,0,0.2)] z-30' : 
        isSpecialMatch ? 'border-emerald-500 shadow-[0_0_30px_rgba(16,185,129,0.15)]' :
        isFull ? 'border-red-900/40' : 'border-slate-800'
      } rounded-3xl p-10 transition-all duration-300 hover:bg-[#002d4d] ${isDimmed ? 'opacity-20 pointer-events-none' : ''}`}
    >
      {isSpecialMatch && (
        <div className="absolute top-3 right-3 bg-emerald-500 text-white px-4 py-1 rounded-full text-[8px] font-black uppercase tracking-widest z-40 animate-pulse">
          Compatible
        </div>
      )}
      {isHighlighted && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-orange-500 text-white px-8 py-2 rounded-full text-[11px] font-black uppercase tracking-[0.2em] shadow-lg animate-bounce z-40">
          Cible Trouvée
        </div>
      )}

      {/* Header du Bloc */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <div className={`p-4 rounded-2xl ${isFull ? 'bg-red-500/20 text-red-500' : 'bg-blue-500/20 text-blue-400 shadow-lg'}`}>
             {data.type === 'VIDE' ? <Zap size={22} /> : <Box size={22} />}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className={`text-3xl font-black tracking-tighter ${isDimmed ? 'text-slate-700' : 'text-white'}`}>{name}</h3>
              <span className={`text-[8px] font-black px-2 py-0.5 rounded-md border ${
                    data.types_admis === 'NORMAL' ? 'border-blue-500/30 text-blue-400 bg-blue-500/5' :
                    data.types_admis === 'FRIGO' ? 'border-cyan-500/30 text-cyan-400 bg-cyan-500/5' :
                    data.types_admis === 'DANGEREUX' ? 'border-red-500/30 text-red-400 bg-red-500/5' :
                    'border-orange-500/30 text-orange-400 bg-orange-500/5'
                }`}>
                    {data.types_admis}
              </span>
            </div>
            <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mt-1">
              {data.type === 'PLEIN' ? 'ZONE DE PLEINS' : 'ZONE DE VIDES'}
            </p>
          </div>
        </div>
        {isFull && <AlertTriangle className="text-red-500 animate-pulse" size={24} />}
      </div>

      {/* Barre de Progression */}
      <div className="space-y-3 mb-6">
        <div className="flex justify-between items-end">
          <span className="text-[11px] font-black text-slate-400 uppercase tracking-widest">
            {fluxFilter === 'ALL' ? "Taux d'occupation" : `Occupation ${fluxFilter}`}
          </span>
          <span className={`text-3xl font-black ${isFull ? 'text-red-400' : 'text-white'}`}>
            {fluxFilter === 'ALL' ? `${Math.round(data.rate)}%` : data.occupancy}
            {fluxFilter !== 'ALL' && <span className="text-xs ml-1 text-slate-500 font-bold uppercase tracking-widest">TC</span>}
          </span>
        </div>
        
        <div className="h-4 w-full bg-slate-950 rounded-full overflow-hidden border border-slate-800 shadow-inner">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: `${Math.max(data.rate, fluxFilter !== 'ALL' && data.occupancy > 0 ? 5 : 0)}%` }}
            transition={{ duration: 1, delay: 0.5 }}
            className={`h-full rounded-full ${
              fluxFilter === 'IMPORT' ? 'bg-gradient-to-r from-blue-600 to-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.5)]' :
              fluxFilter === 'EXPORT' ? 'bg-gradient-to-r from-amber-600 to-amber-400 shadow-[0_0_15px_rgba(251,191,36,0.5)]' :
              data.rate > 85 ? 'bg-gradient-to-r from-red-600 to-red-400' : 
              data.rate > 50 ? 'bg-gradient-to-r from-[#FF8C00] to-orange-400' : 
              'bg-gradient-to-r from-blue-600 to-blue-400'
            }`}
          />
        </div>

        <div className="flex items-center gap-1.5">
           <CheckCircle2 size={12} className="text-emerald-500" />
           <span className="text-[11px] font-black text-slate-400 tracking-wider uppercase">
             {fluxFilter !== 'ALL' ? `${fluxFilter} : ` : ''}{data.occupancy} / {data.capacity} TC EN STOCK
           </span>
        </div>
      </div>

      {/* Bouton 3D permanent - z-30 pour rester au-dessus de l'overlay */}
      <button 
        onClick={(e) => { e.stopPropagation(); onOpen3D(); }}
        className="w-full mt-6 py-4 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white text-[10px] font-black uppercase tracking-widest rounded-xl transition-all flex items-center justify-center gap-3 shadow-lg"
      >
        <Box size={16} />
        OUVRIR LA VUE 3D
      </button>

      {/* Hover Info Overlay - couvre tout sauf le bouton */}
      <div className="absolute inset-0 bottom-[60px] bg-slate-950/95 opacity-0 group-hover:opacity-100 transition-all duration-300 flex flex-col items-center justify-center p-6 text-center backdrop-blur-md z-20 rounded-t-[2.5rem]">
        <h4 className="text-2xl font-black text-white mb-1">{name}</h4>
        <p className="text-[9px] font-black text-orange-400 uppercase tracking-[0.3em] mb-4">{data.type === 'PLEIN' ? 'PLEIN' : 'VIDE'} &bull; {data.occupancy}/{data.capacity} TC</p>
        
        <div className="grid grid-cols-3 gap-2 w-full mb-4">
          <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
             <p className="text-[7px] text-slate-500 uppercase tracking-widest mb-0.5">Travées</p>
             <p className="text-xs font-black text-white">{data.range_allee}</p>
          </div>
          <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
             <p className="text-[7px] text-slate-500 uppercase tracking-widest mb-0.5">Max Z</p>
             <p className="text-xs font-black text-white">{data.max_z}</p>
          </div>
          <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
             <p className="text-[7px] text-slate-500 uppercase tracking-widest mb-0.5">Taux</p>
             <p className={`text-xs font-black ${isFull ? 'text-red-400' : 'text-emerald-400'}`}>{Math.round(data.rate)}%</p>
          </div>
        </div>

        <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-800 w-full">
           <p className="text-[7px] text-slate-500 uppercase tracking-widest mb-0.5">Spécialités</p>
           <p className="text-xs font-black text-blue-400">{data.types_admis || 'NORMAL'}</p>
        </div>
      </div>

      {/* Decorative Glow */}
      <div className="absolute -right-8 -bottom-8 w-32 h-32 bg-blue-500/5 rounded-full blur-[60px]" />
    </motion.div>
  );
}
