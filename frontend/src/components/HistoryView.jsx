import React, { useState } from 'react';
import { History, Search, Download, Filter, Clock } from 'lucide-react';

export default function HistoryView({ history }) {
  const [searchTerm, setSearchTerm] = useState('');

  // Si history est vide ou non fourni
  const data = history && history.length > 0 ? history : [];

  const filteredHistory = data.filter(item => 
    (item.reference || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (item.slot || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleExport = () => {
    if (!filteredHistory.length) return;
    const headers = ["ID", "Reference", "Action", "Slot", "Horodatage", "Status"];
    const rows = filteredHistory.map(h => [
      h.id,
      h.reference,
      h.action,
      h.slot,
      h.horodatage,
      h.status
    ]);
    const csvContent = [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", `Historique_Marsa_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div>
          <h2 className="text-3xl font-black text-white uppercase tracking-tighter">Journal d'Opérations</h2>
          <p className="text-slate-500 font-medium">Historique complet des mouvements IA du terminal</p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={handleExport}
            className="bg-slate-900 border border-slate-800 p-3 rounded-xl hover:bg-slate-800 transition-colors"
            title="Exporter CSV"
          >
            <Download size={20} className="text-[#FF8C00]" />
          </button>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
            <input 
              type="text" 
              placeholder="Rechercher par référence ou slot..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-3 text-sm focus:outline-none focus:border-[#FF8C00] transition-all w-64 text-white"
            />
          </div>
        </div>
      </div>

      <div className="bg-[#001d33] border border-slate-800 rounded-[2.5rem] overflow-hidden shadow-2xl">
        <table className="w-full text-left">
          <thead>
            <tr className="bg-slate-900/50 text-[#FF8C00] text-[10px] font-black uppercase tracking-widest">
              <th className="px-8 py-6">ID</th>
              <th className="px-8 py-6">Référence</th>
              <th className="px-8 py-6">Action</th>
              <th className="px-8 py-6">Emplacement</th>
              <th className="px-8 py-6">Horodatage</th>
              <th className="px-8 py-6">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50 text-white">
            {filteredHistory.map((item) => (
              <tr key={item.id} className="hover:bg-white/5 transition-colors group">
                <td className="px-8 py-5 text-slate-500 font-bold">#{item.id}</td>
                <td className="px-8 py-5 font-black group-hover:text-blue-400 transition-colors">{item.reference}</td>
                <td className="px-8 py-5">
                  <span className={`px-3 py-1 rounded-lg text-[10px] font-black ${
                    item.action === 'ENTRÉE' ? 'bg-emerald-500/10 text-emerald-500' : 
                    item.action === 'SORTIE' ? 'bg-blue-500/10 text-blue-500' : 'bg-orange-500/10 text-orange-500'
                  }`}>
                    {item.action}
                  </span>
                </td>
                <td className="px-8 py-5 text-sm font-bold text-slate-300">{item.slot}</td>
                <td className="px-8 py-5 text-[10px] text-slate-400 font-medium">
                  <div className="flex items-center gap-2">
                    <Clock size={12} className="text-slate-600" />
                    {item.horodatage}
                  </div>
                </td>
                <td className="px-8 py-5">
                  <div className={`w-2 h-2 rounded-full ${item.status === 'SUCCESS' ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-orange-500 shadow-[0_0_8px_rgba(249,115,22,0.5)]'}`} />
                </td>
              </tr>
            ))}
            {filteredHistory.length === 0 && (
              <tr>
                <td colSpan="6" className="px-8 py-24 text-center">
                   <div className="flex flex-col items-center gap-4">
                      <div className="bg-slate-900 p-4 rounded-full border border-slate-800">
                        <History size={40} className="text-slate-700" />
                      </div>
                      <p className="text-slate-500 font-bold uppercase text-xs tracking-widest">
                        {searchTerm ? `Aucun résultat pour "${searchTerm}"` : "Aucun mouvement enregistré pour ce terminal"}
                      </p>
                   </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
