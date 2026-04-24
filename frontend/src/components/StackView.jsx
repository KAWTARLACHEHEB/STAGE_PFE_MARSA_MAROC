import React from 'react';
import { LayoutDashboard } from 'lucide-react';

export default function StackView({ simulationResult }) {
  return (
    <div className="bg-[#001d33] border border-slate-800 rounded-2xl p-6">
      <h3 className="font-bold text-white uppercase tracking-wider text-sm mb-6 flex items-center gap-2">
        <LayoutDashboard size={18} className="text-blue-500" />
        Visualisation de la Pile
      </h3>

      {/* Vue 3D simplifiée (4 niveaux du haut vers le bas) */}
      <div className="flex flex-col-reverse gap-2 h-64 border-l-4 border-b-4 border-slate-700 p-4 bg-[#020617] rounded-lg">
        {[1, 2, 3, 4].map(level => {
          const isRecommended = simulationResult && simulationResult.level === level;
          return (
            <div
              key={level}
              className={`flex-1 flex items-center justify-between px-4 rounded-lg border-2 border-dashed transition-all duration-500 ${
                isRecommended
                  ? 'bg-[#FF8C00]/20 border-[#FF8C00] text-[#FF8C00] animate-pulse'
                  : 'bg-slate-900/50 border-slate-800 text-slate-700'
              }`}
            >
              <span className="text-xs font-black">Z{level}</span>
              {isRecommended && (
                <span className="text-[9px] font-black bg-[#FF8C00] text-white px-2 py-0.5 rounded-full">
                  IA
                </span>
              )}
            </div>
          );
        })}
      </div>

      {simulationResult ? (
        <div className="mt-4 text-center space-y-1">
          <p className="text-xs text-slate-400">
            Position recommandée · Zone{' '}
            <span className="text-white font-bold">{simulationResult.zone}</span>
          </p>
          <p className="text-xl font-black text-[#FF8C00]">{simulationResult.slot}</p>
          <p className="text-[10px] text-slate-500">Score IA : {simulationResult.score}</p>
        </div>
      ) : (
        <p className="mt-4 text-center text-[10px] text-slate-600 uppercase tracking-widest">
          En attente de simulation...
        </p>
      )}
    </div>
  );
}
