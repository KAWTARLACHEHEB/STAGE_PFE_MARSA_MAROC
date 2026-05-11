import React, { useState } from 'react';
import { Package, MapPin, Clock, Box, Search, ChevronDown } from 'lucide-react';

export default function InventoryTable({ conteneurs, fluxFilter = 'ALL', onLocate }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [displayLimit, setDisplayLimit] = useState(50);

  if (!conteneurs || conteneurs.length === 0) {
    return (
      <div className="bg-[#001d33] border border-slate-800 rounded-[2.5rem] p-20 text-center">
        <div className="bg-slate-900 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 border border-slate-800">
           <Package size={40} className="text-slate-700" />
        </div>
        <h3 className="text-xl font-black text-white uppercase tracking-widest">Inventaire Vide</h3>
        <p className="text-slate-500 mt-2">Aucun conteneur détecté dans la base de données Gold.</p>
      </div>
    );
  }

  const filteredConteneurs = conteneurs.filter(ct => {
    const searchStr = (
      (ct.reference || '') + 
      (ct.zone || '') + 
      (ct.nom_navire || '') + 
      (ct.pod || '') + 
      (ct.type_iso_detail || '') +
      (ct.specialite || '')
    ).toLowerCase();
    
    // Gérer la faute de frappe commune "thank" -> "tank"
    const normalizedSearchTerm = searchTerm.toLowerCase().replace('thank', 'tank');
    
    const matchSearch = searchStr.includes(normalizedSearchTerm);
    
    let matchFlux = true;
    if (fluxFilter !== 'ALL') {
      matchFlux = (ct.flux || 'IMPORT').toUpperCase() === fluxFilter;
    }
    
    return matchSearch && matchFlux;
  });

  return (
    <div className="bg-[#001d33] border border-slate-800 rounded-[2.5rem] overflow-hidden shadow-2xl">
      <div className="p-8 border-b border-slate-800 flex flex-col md:flex-row justify-between items-start md:items-center gap-6 bg-slate-900/50">
        <div className="flex items-center gap-4">
          <div className="bg-[#FF8C00] p-2 rounded-xl">
            <Package size={20} className="text-white" />
          </div>
          <h3 className="font-black text-white uppercase tracking-widest text-sm">Répertoire National du Parc</h3>
        </div>

        <div className="flex items-center gap-6 w-full md:w-auto">
          <div className="relative flex-1 md:w-64">
            <Search size={14} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
            <input 
              type="text" 
              placeholder="Chercher référence ou zone..." 
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setDisplayLimit(50); // Reset limite lors d'une nouvelle recherche
              }}
              className="w-full bg-slate-950 border border-slate-800 rounded-full pl-10 pr-4 py-2.5 text-xs font-black uppercase tracking-widest text-white placeholder:text-slate-600 focus:outline-none focus:border-[#FF8C00] transition-colors"
            />
          </div>
          <div className="text-[10px] font-black text-slate-500 uppercase hidden lg:block">
            Mise à jour : {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-950/50 text-[#FF8C00] text-[9px] font-black uppercase tracking-[0.2em]">
              <th className="px-8 py-6">Référence</th>
              <th className="px-8 py-6">Position (Z-A-P-L)</th>
              <th className="px-8 py-6">Type / Taille</th>
              <th className="px-8 py-6">Flux / Métier</th>
              <th className="px-8 py-6">Poids (kg)</th>
              <th className="px-8 py-6">Départ Prévu</th>
              <th className="px-8 py-6">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {filteredConteneurs.slice(0, displayLimit).map((ct, i) => (
              <tr key={i} className="hover:bg-blue-500/5 transition-colors group">
                <td className="px-8 py-5">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center text-[10px] font-bold text-slate-400 group-hover:text-[#FF8C00] transition-colors border border-slate-800">
                      {i + 1}
                    </div>
                    <span className="text-sm font-black text-white tracking-tighter">{ct.reference || ct.container_id}</span>
                  </div>
                </td>
                <td className="px-8 py-5">
                  <div className="flex items-center gap-2 text-xs font-bold text-blue-400">
                    <MapPin size={12} />
                    {ct.zone}-{ct.allee}-{ct.pile} (Niv {ct.niveau_z})
                  </div>
                </td>
                <td className="px-8 py-5">
                  <div className="flex gap-2">
                    <span className="px-3 py-1 bg-slate-900 rounded-full text-[9px] font-black text-slate-400 border border-slate-800">{ct.type_conteneur}</span>
                    <span className="px-3 py-1 bg-slate-900 rounded-full text-[9px] font-black text-slate-400 border border-slate-800">{ct.size}'</span>
                  </div>
                </td>
                <td className="px-8 py-5">
                  <div className="flex flex-col gap-1">
                    <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded-sm inline-block w-max ${ct.flux === 'EXPORT' ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                      {ct.flux || 'IMPORT'}
                    </span>
                    {ct.flux === 'IMPORT' && ct.status_douane && (
                      <span className="text-[9px] font-bold text-slate-400 uppercase">
                        Douane: {ct.status_douane}
                      </span>
                    )}
                    {ct.flux === 'EXPORT' && ct.nom_navire && (
                      <span className="text-[9px] font-bold text-slate-400 uppercase">Vsl: {ct.nom_navire}</span>
                    )}
                    {ct.flux === 'EXPORT' && ct.pod && (
                      <span className="text-[9px] font-bold text-slate-400 uppercase">POD: {ct.pod}</span>
                    )}
                    {ct.type_iso_detail && (
                      <span className="text-[9px] font-bold text-[#FF8C00] uppercase italic">ISO: {ct.type_iso_detail}</span>
                    )}
                  </div>
                </td>
                <td className="px-8 py-5">
                  <span className="text-xs font-bold text-slate-300">{(ct.weight || 0).toLocaleString()} kg</span>
                </td>
                <td className="px-8 py-5">
                  <div className="flex items-center gap-2 text-[10px] font-medium text-slate-500">
                    <Clock size={12} />
                    {new Date(ct.departure_time).toLocaleDateString()}
                  </div>
                </td>
                <td className="px-8 py-5">
                  <div className="flex items-center gap-4">
                    <span className="flex items-center gap-2 text-[9px] font-black text-emerald-500 uppercase tracking-widest">
                      <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
                      En Stock
                    </span>
                    {onLocate && (
                      <button 
                        onClick={() => onLocate(ct)}
                        className="opacity-0 group-hover:opacity-100 transition-opacity bg-blue-600/20 text-blue-400 hover:bg-blue-600 hover:text-white px-3 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-widest flex items-center gap-2"
                      >
                        <Box size={12} />
                        Voir 3D
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
            {filteredConteneurs.length === 0 && (
              <tr>
                <td colSpan="7" className="px-8 py-12 text-center text-slate-500 font-bold uppercase tracking-widest text-[10px]">
                  Aucun conteneur ne correspond à "{searchTerm}"
                </td>
              </tr>
            )}
          </tbody>
        </table>
        
        {filteredConteneurs.length > displayLimit && (
          <div className="p-6 flex flex-col items-center gap-4 bg-slate-950/30">
            <p className="text-[10px] font-black text-slate-600 uppercase tracking-widest">
              Affichage de {displayLimit} sur {filteredConteneurs.length} conteneurs
            </p>
            <button 
              onClick={() => setDisplayLimit(prev => prev + 50)}
              className="px-6 py-2.5 rounded-full bg-slate-900 border border-slate-800 text-xs font-black uppercase tracking-widest text-slate-400 hover:text-[#FF8C00] hover:border-[#FF8C00] transition-colors flex items-center gap-2"
            >
              <ChevronDown size={14} />
              Charger Plus
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
