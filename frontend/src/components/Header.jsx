import React, { useState, useEffect } from 'react';
import { Clock, MapPin, ChevronDown } from 'lucide-react';

export default function Header({ terminal, setTerminal }) {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="h-20 border-b border-slate-800 bg-[#020617]/50 backdrop-blur-xl flex items-center justify-between px-8 z-30">
      <div className="flex items-center gap-6">
        <h2 className="text-sm font-black text-white uppercase tracking-[0.2em] flex items-center gap-3">
          <span className="w-2 h-8 bg-[#FF8C00] rounded-full" />
          Supervision <span className="text-blue-500">Flux Reels</span>
        </h2>
        
        {/* Selecteur de Terminal Premium */}
        <div className="flex bg-slate-900/80 p-1 rounded-xl border border-slate-800">
          {['TCE', 'TC3'].map((t) => (
            <button
              key={t}
              onClick={() => setTerminal(t)}
              className={`px-6 py-1.5 rounded-lg text-[10px] font-black transition-all ${
                terminal === t ? 'bg-[#002347] text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-6">
        <div className="hidden md:flex flex-col items-end">
          <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Temps Reel Terminal</span>
          <div className="flex items-center gap-2 text-white font-mono font-bold">
            <Clock size={14} className="text-[#FF8C00]" />
            {time.toLocaleTimeString('fr-FR')}
          </div>
        </div>
        <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-slate-800 to-slate-700 border border-slate-600 flex items-center justify-center text-white font-bold text-xs shadow-xl">
          KM
        </div>
      </div>
    </header>
  );
}
