import React, { useState } from 'react';
import { Play, Activity, Target, ArrowRight, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function OptimizationPanel({ onOptimize, isOptimizing, simulationResult, onBatchOptimize }) {
  const [isBatchMode, setIsBatchMode] = useState(false);
  const [batchCount, setBatchCount] = useState(10);
  const [formData, setFormData] = useState({
    reference: 'MRSU-' + Math.floor(Math.random() * 10000),
    dimension: '20',
    special_type: 'NORMAL',
    weight: 22000,
    departure_time: new Date().toISOString().slice(0, 16)
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isBatchMode) {
      onBatchOptimize(batchCount);
    } else {
      onOptimize(formData);
    }
  };

  return (
    <div className="bg-[#001d33] border border-slate-800 rounded-[2.5rem] p-8 shadow-2xl relative overflow-hidden group">
      {/* Background Decorative */}
      <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
        <Target size={120} />
      </div>

      <div className="relative z-10 space-y-6">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-3">
            <div className="bg-[#FF8C00]/20 p-2 rounded-lg text-[#FF8C00]">
               <Zap size={20} />
            </div>
            <h3 className="font-black text-white uppercase tracking-[0.2em] text-xs">Simulation d'Arrivée</h3>
          </div>
          
          {/* Toggle Mode */}
          <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800">
            <button 
              onClick={() => setIsBatchMode(false)}
              className={`px-3 py-1.5 rounded-lg text-[9px] font-black uppercase transition-all ${!isBatchMode ? 'bg-[#FF8C00] text-white shadow-lg' : 'text-slate-600'}`}
            >
              Unique
            </button>
            <button 
              onClick={() => setIsBatchMode(true)}
              className={`px-3 py-1.5 rounded-lg text-[9px] font-black uppercase transition-all ${isBatchMode ? 'bg-[#FF8C00] text-white shadow-lg' : 'text-slate-600'}`}
            >
              Massive (Batch)
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {!isBatchMode ? (
            <>
              <div className="space-y-1">
                <label className="text-[9px] font-black uppercase text-slate-500 ml-1">Référence Conteneur</label>
                <input 
                  value={formData.reference}
                  onChange={(e) => setFormData({...formData, reference: e.target.value})}
                  className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-5 py-4 text-sm text-white focus:outline-none focus:border-[#FF8C00] transition-colors font-mono"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[9px] font-black uppercase text-slate-500 ml-1">Spécialité</label>
                  <select 
                    value={formData.special_type}
                    onChange={(e) => setFormData({...formData, special_type: e.target.value})}
                    className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-5 py-4 text-sm text-white focus:outline-none focus:border-[#FF8C00] appearance-none"
                  >
                    <option value="NORMAL">NORMAL</option>
                    <option value="FRIGO">FRIGO</option>
                    <option value="DANGEREUX">DANGER</option>
                    <option value="HORS_GABARIT">OOG</option>
                    <option value="CITERNE">CITERNE</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-[9px] font-black uppercase text-slate-500 ml-1">Poids (Kg)</label>
                  <input 
                    type="number"
                    value={formData.weight}
                    onChange={(e) => setFormData({...formData, weight: e.target.value})}
                    className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-5 py-4 text-sm text-white focus:outline-none focus:border-[#FF8C00]"
                  />
                </div>
              </div>
            </>
          ) : (
            <div className="space-y-1">
              <label className="text-[9px] font-black uppercase text-slate-500 ml-1">Nombre de conteneurs (Arrivée massive)</label>
              <div className="flex items-center gap-4">
                <input 
                  type="range"
                  min="1"
                  max="100"
                  value={batchCount}
                  onChange={(e) => setBatchCount(parseInt(e.target.value))}
                  className="flex-1 accent-[#FF8C00]"
                />
                <span className="bg-slate-950 px-4 py-2 rounded-xl border border-slate-800 text-white font-black text-lg min-w-[60px] text-center">
                  {batchCount}
                </span>
              </div>
              <p className="text-[10px] text-slate-600 italic mt-2 text-center">
                L'IA va générer {batchCount} arrivées avec des dates de sorties variées pour tester la congestion.
              </p>
            </div>
          )}

          <button 
            type="submit"
            disabled={isOptimizing}
            className={`w-full py-5 rounded-[1.5rem] font-black uppercase tracking-widest text-[10px] transition-all flex items-center justify-center gap-3 shadow-xl ${
              isOptimizing ? 'bg-slate-800 text-slate-600' : 'bg-gradient-to-r from-[#FF8C00] to-orange-600 text-white hover:scale-[1.02] active:scale-[0.98] shadow-orange-900/20'
            }`}
          >
            {isOptimizing ? 'Calcul IA en cours...' : isBatchMode ? `Lancer Simulation Massive (${batchCount})` : 'Optimiser le Stacking'}
            <ArrowRight size={16} />
          </button>
        </form>

        {/* Résultat Clignotant */}
        <AnimatePresence>
          {simulationResult && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 p-6 bg-blue-500/10 border border-blue-500/30 rounded-3xl relative overflow-hidden"
            >
              <motion.div 
                animate={{ opacity: [0.1, 0.3, 0.1] }} 
                transition={{ duration: 1.5, repeat: Infinity }}
                className="absolute inset-0 bg-blue-400"
              />
              <div className="relative z-10">
                <p className="text-[9px] font-black text-blue-400 uppercase tracking-widest mb-1">
                  {simulationResult.batchCount ? "Rapport de Simulation Massive" : "Slot IA Recommandé"}
                </p>
                <h4 className="text-2xl font-black text-white tracking-tighter">
                  {simulationResult.batchCount ? `${simulationResult.batchCount} TC Ajoutés` : simulationResult.slot}
                </h4>
                <div className="max-h-32 overflow-y-auto mt-3 pr-2 scrollbar-thin scrollbar-thumb-blue-500/20">
                  <p className="text-[10px] text-blue-300/80 font-bold leading-relaxed">
                    {simulationResult.reasoning}
                  </p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
