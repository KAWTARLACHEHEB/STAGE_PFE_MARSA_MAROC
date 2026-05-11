import React, { useState } from 'react';
import { Search, MapPin, AlertTriangle, ShieldCheck, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function ContainerTracker({ onFound }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query) return;
    
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/container/${query.trim()}`);
      if (!response.ok) throw new Error("Conteneur non localisé");
      
      const data = await response.json();
      setResult(data);
      onFound(data); // On passe tout l'objet
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative">
      <form onSubmit={handleSearch} className="relative group">
        <input 
          type="text"
          placeholder="Rechercher Position Réelle (ex: HLBU...)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full lg:w-96 bg-[#001d33] border border-slate-800 rounded-full pl-12 pr-6 py-4 text-sm text-white focus:outline-none focus:border-orange-500 transition-all shadow-2xl"
        />
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-hover:text-orange-500 transition-colors" size={18} />
        {loading && (
          <div className="absolute right-4 top-1/2 -translate-y-1/2">
            <div className="w-4 h-4 border-2 border-orange-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}
      </form>

      <AnimatePresence>
        {result && (
          <motion.div 
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="absolute top-full mt-4 w-full lg:w-[400px] bg-slate-900 border border-slate-800 rounded-[2rem] p-6 shadow-3xl z-50 overflow-hidden"
          >
            <div className="absolute top-0 right-0 p-4">
                <button onClick={() => setResult(null)} className="text-slate-500 hover:text-white">
                    <X size={18} />
                </button>
            </div>

            <div className="flex items-center gap-4 mb-6">
                <div className="bg-orange-500/20 p-3 rounded-2xl">
                    <MapPin className="text-orange-500" size={24} />
                </div>
                <div>
                    <h4 className="text-lg font-black text-white tracking-tighter uppercase">{result.reference}</h4>
                    <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Localisé au {result.terminal}</p>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-3 mb-4">
                <DataCard label="Bloc" value={result.coords.bloc} />
                <DataCard label="Travee" value={result.coords.travee} />
                <DataCard label="Pile" value={result.coords.cellule} />
                <DataCard label="Niveau" value={result.coords.niveau} highlight={result.coords.niveau > 6} />
            </div>

            {/* Détails Métier (Flux / Douane / Navire) */}
            {(result.flux || result.navire_id) && (
              <div className="bg-slate-950 border border-slate-800 rounded-2xl p-4 mb-6">
                <div className="flex items-center gap-2 mb-3">
                  <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded-sm ${result.flux === 'EXPORT' ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                    {result.flux || 'IMPORT'}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-[10px] font-bold text-slate-400 uppercase">
                  {result.flux === 'IMPORT' && result.statut_import && (
                    <div className="col-span-2">Douane: <span className="text-white">{result.statut_import.replace('_', ' ')}</span></div>
                  )}
                  {result.flux === 'EXPORT' && result.navire_id && (
                    <div>Navire: <span className="text-white">{result.navire_id}</span></div>
                  )}
                  {result.flux === 'EXPORT' && result.pod && (
                    <div>POD: <span className="text-white">{result.pod}</span></div>
                  )}
                </div>
              </div>
            )}

            <div className={`flex items-center gap-3 p-4 rounded-2xl ${
                result.coords.niveau > 6 ? 'bg-red-500/10 border border-red-500/20 text-red-400' : 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400'
            }`}>
                {result.coords.niveau > 6 ? <AlertTriangle size={18} /> : <ShieldCheck size={18} />}
                <span className="text-[10px] font-black uppercase tracking-widest">{result.safety_status}</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {error && (
        <motion.p 
          initial={{ opacity: 0 }} 
          animate={{ opacity: 1 }}
          className="absolute top-full mt-2 left-4 text-red-500 text-[10px] font-black uppercase tracking-widest"
        >
          {error}
        </motion.p>
      )}
    </div>
  );
}

function DataCard({ label, value, highlight }) {
    return (
        <div className={`p-4 rounded-2xl border ${highlight ? 'bg-red-500/10 border-red-500/20' : 'bg-slate-950 border-slate-800'}`}>
            <p className="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-1">{label}</p>
            <p className={`text-xl font-black ${highlight ? 'text-red-400' : 'text-white'}`}>{value}</p>
        </div>
    )
}
