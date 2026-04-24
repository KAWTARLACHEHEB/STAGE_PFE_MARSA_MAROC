import React from 'react';
import { Package, MapPin, Clock, Weight, Box } from 'lucide-react';

export default function InventoryTable({ conteneurs }) {
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

  return (
    <div className="bg-[#001d33] border border-slate-800 rounded-[2.5rem] overflow-hidden shadow-2xl">
      <div className="p-8 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
        <div className="flex items-center gap-4">
          <div className="bg-[#FF8C00] p-2 rounded-xl">
            <Package size={20} className="text-white" />
          </div>
          <h3 className="font-black text-white uppercase tracking-widest text-sm">Répertoire National du Parc</h3>
        </div>
        <div className="text-[10px] font-black text-slate-500 uppercase">
          Mise à jour : {new Date().toLocaleTimeString()}
        </div>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-950/50 text-[#FF8C00] text-[9px] font-black uppercase tracking-[0.2em]">
              <th className="px-8 py-6">Référence</th>
              <th className="px-8 py-6">Position (Z-A-P-L)</th>
              <th className="px-8 py-6">Type / Taille</th>
              <th className="px-8 py-6">Poids (kg)</th>
              <th className="px-8 py-6">Départ Prévu</th>
              <th className="px-8 py-6">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {conteneurs.slice(0, 50).map((ct, i) => (
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
                  <span className="text-xs font-bold text-slate-300">{(ct.weight || 0).toLocaleString()} kg</span>
                </td>
                <td className="px-8 py-5">
                  <div className="flex items-center gap-2 text-[10px] font-medium text-slate-500">
                    <Clock size={12} />
                    {new Date(ct.departure_time).toLocaleDateString()}
                  </div>
                </td>
                <td className="px-8 py-5">
                  <span className="flex items-center gap-2 text-[9px] font-black text-emerald-500 uppercase tracking-widest">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
                    En Stock
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {conteneurs.length > 50 && (
          <div className="p-6 text-center bg-slate-950/30">
            <p className="text-[10px] font-black text-slate-600 uppercase tracking-widest">
              Affichage des 50 premiers sur {conteneurs.length} conteneurs
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
