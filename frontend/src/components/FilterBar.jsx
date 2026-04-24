import React from 'react';
import { Filter, Box, Zap, Target, Thermometer, ShieldAlert, Expand, Droplets } from 'lucide-react';

export default function FilterBar({ filterType, setFilterType, containerCategory, setContainerCategory, zones = {} }) {
  const zoneList = Object.values(zones);
  const pleinCount = zoneList.filter(z => z.type === 'PLEIN').length;
  const videCount = zoneList.filter(z => z.type === 'VIDE').length;

  return (
    <div className="bg-[#001d33] border border-slate-800 rounded-[2.5rem] p-4 lg:p-6 shadow-2xl flex flex-col lg:flex-row gap-6 lg:items-center justify-between">
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

      <div className="flex items-center gap-4 overflow-x-auto pb-2 lg:pb-0 no-scrollbar">
        <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest whitespace-nowrap">Specialité :</span>
        <div className="flex gap-2">
          <TypeTag active={containerCategory === 'NORMAL'} onClick={() => setContainerCategory('NORMAL')} label="Normal" icon={<Target size={14} />} />
          <TypeTag active={containerCategory === 'FRIGO'} onClick={() => setContainerCategory('FRIGO')} label="Frigo" icon={<Thermometer size={14} />} />
          <TypeTag active={containerCategory === 'DANGER'} onClick={() => setContainerCategory('DANGER')} label="Danger" icon={<ShieldAlert size={14} />} />
          <TypeTag active={containerCategory === 'OOG'} onClick={() => setContainerCategory('OOG')} label="OOG" icon={<Expand size={14} />} />
          <TypeTag active={containerCategory === 'CITERNE'} onClick={() => setContainerCategory('CITERNE')} label="Citerne" icon={<Droplets size={14} />} />
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

function TypeTag({ label, icon, active, onClick }) {
  return (
    <button 
      onClick={onClick}
      className={`flex items-center gap-2 px-5 py-3 rounded-2xl border text-[10px] font-black uppercase tracking-widest transition-all ${
        active ? 'bg-blue-600/10 border-blue-500 text-blue-400' : 'bg-slate-900 border-slate-800 text-slate-500 hover:border-slate-700'
      }`}
    >
      {icon}
      {label}
    </button>
  );
}
