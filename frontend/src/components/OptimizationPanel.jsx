import React, { useState } from 'react';
import { Play, Activity, Target, ArrowRight, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function OptimizationPanel({ onOptimize, isOptimizing, simulationResult }) {
  const [formData, setFormData] = useState({
    reference: 'MRSU-' + Math.floor(Math.random() * 10000),
    dimension: '20',
    special_type: 'NORMAL',
    weight: 22000,
    departure_time: new Date().toISOString().slice(0, 16)
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onOptimize(formData);
  };

  return (
    <div className="bg-[#001d33] border border-slate-800 rounded-[2.5rem] p-8 shadow-2xl relative overflow-hidden group">
      {/* Background Decorative */}
      <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
        <Target size={120} />
      </div>

      <div className="relative z-10 space-y-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="bg-[#FF8C00]/20 p-2 rounded-lg text-[#FF8C00]">
             <Zap size={20} />
          </div>
          <h3 className="font-black text-white uppercase tracking-[0.2em] text-xs">Simulation d'Arrivée</h3>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
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
                <option value="CITERNES">CITERNE</option>
              </select>
            </div>
            <div className="space-y-1">
              <label className="text-[9px] font-black uppercase text-slate-500 ml-1">Poids (T)</label>
              <input 
                type="number"
                value={formData.weight}
                onChange={(e) => setFormData({...formData, weight: e.target.value})}
                className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-5 py-4 text-sm text-white focus:outline-none focus:border-[#FF8C00]"
              />
            </div>
          </div>

          <button 
            type="submit"
            disabled={isOptimizing}
            className={`w-full py-5 rounded-[1.5rem] font-black uppercase tracking-widest text-[10px] transition-all flex items-center justify-center gap-3 shadow-xl ${
              isOptimizing ? 'bg-slate-800 text-slate-600' : 'bg-gradient-to-r from-[#FF8C00] to-orange-600 text-white hover:scale-[1.02] active:scale-[0.98] shadow-orange-900/20'
            }`}
          >
            {isOptimizing ? 'Calcul IA en cours...' : 'Optimiser le Stacking'}
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
                <p className="text-[9px] font-black text-blue-400 uppercase tracking-widest mb-1">Slot IA Recommandé</p>
                <h4 className="text-2xl font-black text-white tracking-tighter">{simulationResult.slot}</h4>
                <p className="text-[10px] text-blue-300/70 mt-2 font-bold italic">Raison : {simulationResult.reasoning}</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
