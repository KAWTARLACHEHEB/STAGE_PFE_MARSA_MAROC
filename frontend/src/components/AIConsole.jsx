import React, { useRef, useEffect } from 'react';
import { Terminal } from 'lucide-react';

export default function AIConsole({ logs }) {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const getLogStyle = (log) => {
    if (log.startsWith('✅') || log.includes('OK') || log.includes('pret')) return 'text-emerald-400 font-bold';
    if (log.startsWith('❌') || log.includes('ERREUR') || log.includes('FOUILLE')) return 'text-red-400';
    if (log.includes('CONGESTION')) return 'text-amber-400';
    if (log.startsWith('[IA]') || log.startsWith('>')) return 'text-blue-300';
    return 'text-emerald-400/70';
  };

  return (
    <div className="bg-black/80 border-t-4 border-[#FF8C00] rounded-2xl overflow-hidden shadow-2xl font-mono">
      {/* Barre titre style terminal */}
      <div className="bg-[#111] px-6 py-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal size={14} className="text-emerald-500" />
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
            Marsa Maroc AI Engine — Console
          </span>
        </div>
        <div className="flex gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
          <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
        </div>
      </div>

      {/* Logs */}
      <div ref={scrollRef} className="p-6 h-44 overflow-y-auto text-xs space-y-1">
        {logs.map((log, i) => (
          <div key={i} className={getLogStyle(log)}>
            <span className="text-slate-600 mr-2 select-none">{String(i + 1).padStart(2, '0')}</span>
            {log}
          </div>
        ))}
        <div className="flex items-center gap-1 text-emerald-400/50 mt-1">
          <span>&gt;</span>
          <span className="w-2 h-3 bg-emerald-400/50 animate-pulse inline-block" />
        </div>
      </div>
    </div>
  );
}
