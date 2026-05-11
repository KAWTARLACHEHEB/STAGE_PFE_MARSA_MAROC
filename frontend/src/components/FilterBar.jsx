import React from 'react';
import { Filter, Box, Zap, Target, Thermometer, ShieldAlert, Expand, Droplets, ArrowDownLeft, ArrowUpRight, Globe } from 'lucide-react';

export default function FilterBar({ filterType, setFilterType, containerCategory, setContainerCategory, fluxFilter, setFluxFilter, zones = {}, statsMapping = {} }) {
  const zoneList = Object.values(zones || {});
  const pleinCount = zoneList.filter(z => z.type === 'PLEIN').length;
  const videCount = zoneList.filter(z => z.type === 'VIDE').length;

  console.log("[FilterBar] Flux actuel:", fluxFilter);

  return (
    <div className="bg-[#001d33] border border-slate-800 rounded-[2.5rem] p-4 lg:p-6 shadow-2xl flex flex-col xl:flex-row gap-6 xl:items-center justify-between">
      <div className="flex flex-col lg:flex-row items-start lg:items-center gap-6">
        <div className="flex items-center gap-4">
          <div className="bg-slate-900 p-4 rounded-[1.5rem] border border-slate-800 hidden sm:block">
             <Filter size={20} className="text-[#FF8C00]" />
          </div>
          <div className="flex bg-slate-950 p-1.5 rounded-[1.8rem] border border-slate-800 overflow-x-auto no-scrollbar">
            <FilterBtn 
              active={filterType === 'ALL'} 
              onClick={() => setFilterType('ALL')} 
              label={`Tout le parc (${zoneList.length})`} 
            />
            <FilterBtn 
              active={filterType === 'PLEIN'} 
              onClick={() => setFilterType('PLEIN')} 
              label={`Plein (${pleinCount})`} 
              icon={<Box size={14} />}
            />
            <FilterBtn 
              active={filterType === 'VIDE'} 
              onClick={() => setFilterType('VIDE')} 
              label={`Vide (${videCount})`} 
              icon={<Zap size={14} />}
            />
          </div>
        </div>

        <div className="h-10 w-px bg-slate-800 hidden lg:block" />

        {/* NOUVEAU: Filtre de Flux Logistique */}
        <div className="flex items-center gap-4 overflow-x-auto pb-2 lg:pb-0 no-scrollbar">
          <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest whitespace-nowrap">Flux :</span>
          <div className="flex bg-slate-950 p-1.5 rounded-[1.8rem] border border-slate-800 overflow-x-auto no-scrollbar">
            <FilterBtn 
              active={fluxFilter === 'ALL'} 
              onClick={() => { console.log("Click ALL"); setFluxFilter('ALL'); }} 
              label="Tous" 
              icon={<Globe size={14} />}
            />
            <FilterBtn 
              active={fluxFilter === 'IMPORT'} 
              onClick={() => { console.log("Click IMPORT"); setFluxFilter('IMPORT'); }} 
              label="Import" 
              icon={<ArrowDownLeft size={14} />}
            />
            <FilterBtn 
              active={fluxFilter === 'EXPORT'} 
              onClick={() => { console.log("Click EXPORT"); setFluxFilter('EXPORT'); }} 
              label="Export" 
              icon={<ArrowUpRight size={14} />}
            />
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4 overflow-x-auto pb-2 xl:pb-0 no-scrollbar">
        <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest whitespace-nowrap">Specialité :</span>
        <div className="flex gap-2">
          <TypeTag active={containerCategory === 'NORMAL'}       onClick={() => setContainerCategory('NORMAL')}       label="Dry Standard"      icon={<Target size={14} />}      color="blue"   />
          <TypeTag active={containerCategory === 'FRIGO'}        onClick={() => setContainerCategory('FRIGO')}        label="Reefer"            icon={<Thermometer size={14} />} color="cyan"   />
          <TypeTag active={containerCategory === 'DANGEREUX'}    onClick={() => setContainerCategory('DANGEREUX')}    label="Dangereux (IMDG)"  icon={<ShieldAlert size={14} />} color="red"    />
          <TypeTag active={containerCategory === 'CITERNE'}      onClick={() => setContainerCategory('CITERNE')}      label="Tank"              icon={<Droplets size={14} />}    color="sky"    />
          <TypeTag active={containerCategory === 'HORS_GABARIT'} onClick={() => setContainerCategory('HORS_GABARIT')} label="OOG / Flat Rack"   icon={<Expand size={14} />}      color="purple" />
        </div>
      </div>
    </div>
  );
}

function FilterBtn({ label, active, onClick, icon }) {
  return (
    <button 
      onClick={onClick}
      className={`px-6 py-3 rounded-[1.4rem] text-[10px] font-black uppercase tracking-widest transition-all flex items-center gap-2 whitespace-nowrap ${
        active ? 'bg-[#FF8C00] text-white shadow-lg shadow-orange-900/20' : 'text-slate-500 hover:text-slate-300'
      }`}
    >
      {icon}
      {label}
    </button>
  );
}

function TypeTag({ label, icon, active, onClick, color = 'blue' }) {
  const colors = {
    blue:   { active: 'bg-blue-600/10 border-blue-500 text-blue-400',     inactive: 'bg-slate-900 border-slate-800 text-slate-500 hover:border-blue-800 hover:text-blue-400' },
    cyan:   { active: 'bg-cyan-600/10 border-cyan-500 text-cyan-400',     inactive: 'bg-slate-900 border-slate-800 text-slate-500 hover:border-cyan-800 hover:text-cyan-400' },
    red:    { active: 'bg-red-600/10 border-red-500 text-red-400',         inactive: 'bg-slate-900 border-slate-800 text-slate-500 hover:border-red-800 hover:text-red-400' },
    purple: { active: 'bg-purple-600/10 border-purple-500 text-purple-400', inactive: 'bg-slate-900 border-slate-800 text-slate-500 hover:border-purple-800 hover:text-purple-400' },
    sky:    { active: 'bg-sky-600/10 border-sky-500 text-sky-400',         inactive: 'bg-slate-900 border-slate-800 text-slate-500 hover:border-sky-800 hover:text-sky-400' },
  };
  const cls = colors[color] || colors.blue;
  return (
    <button 
      onClick={onClick}
      className={`flex items-center gap-2 px-5 py-3 rounded-2xl border text-[10px] font-black uppercase tracking-widest transition-all ${
        active ? cls.active : cls.inactive
      }`}
    >
      {icon}
      {label}
    </button>
  );
}
