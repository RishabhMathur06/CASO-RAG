import React, { useState } from 'react';
import { 
  Network, 
  ExternalLink, 
  Trash2, 
  PlusCircle, 
  Activity, 
  Database,
  BarChart2
} from 'lucide-react';
import { clearRedisCache } from '../services/api';

export default function Navbar({ isOnline, onOpenIngest }) {
  const [clearing, setClearing] = useState(false);
  const [clearMsg, setClearMsg] = useState('');

  const handleClearCache = async () => {
    try {
      setClearing(true);
      const res = await clearRedisCache();
      setClearMsg(res.message || 'Cache cleared!');
      setTimeout(() => setClearMsg(''), 3000);
    } catch (err) {
      setClearMsg('Error clearing cache');
      setTimeout(() => setClearMsg(''), 3000);
    } finally {
      setClearing(false);
    }
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/80 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <Network className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-lg text-white tracking-tight">CASO-RAG</span>
            <span className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              GraphRAG-X
            </span>
          </div>
          <p className="text-[11px] text-slate-400">Context-Aware Self-Organizing Dual Store</p>
        </div>
      </div>

      {/* Center status */}
      <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/80 border border-slate-700/60 text-xs">
        <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
        <span className="text-slate-300 font-medium">
          {isOnline ? 'Backend Online (Port 8000)' : 'Backend Disconnected'}
        </span>
      </div>

      {/* Quick Action Links & Ingest */}
      <div className="flex items-center gap-2">
        {clearMsg && (
          <span className="text-xs text-amber-400 bg-amber-500/10 px-2 py-1 rounded border border-amber-500/20 animate-fade-in">
            {clearMsg}
          </span>
        )}

        <button
          onClick={handleClearCache}
          disabled={clearing}
          title="Clear Redis Query Cache"
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 transition"
        >
          <Trash2 className="w-3.5 h-3.5 text-amber-400" />
          <span>{clearing ? 'Clearing...' : 'Flush Cache'}</span>
        </button>

        <button
          onClick={onOpenIngest}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-indigo-600 hover:bg-indigo-500 rounded-lg shadow-sm transition"
        >
          <PlusCircle className="w-3.5 h-3.5" />
          <span>Ingest Document</span>
        </button>

        {/* Ops shortcuts */}
        <div className="h-5 w-[1px] bg-slate-800 mx-1" />

        <a
          href="http://localhost:3001"
          target="_blank"
          rel="noreferrer"
          title="Open Grafana Dashboard (:3001)"
          className="p-2 text-slate-400 hover:text-cyan-400 hover:bg-slate-800 rounded-lg transition"
        >
          <Activity className="w-4 h-4" />
        </a>

        <a
          href="http://localhost:5001"
          target="_blank"
          rel="noreferrer"
          title="Open MLflow Experiments (:5001)"
          className="p-2 text-slate-400 hover:text-indigo-400 hover:bg-slate-800 rounded-lg transition"
        >
          <BarChart2 className="w-4 h-4" />
        </a>

        <a
          href="http://localhost:7474"
          target="_blank"
          rel="noreferrer"
          title="Open Neo4j Browser (:7474)"
          className="p-2 text-slate-400 hover:text-emerald-400 hover:bg-slate-800 rounded-lg transition"
        >
          <Database className="w-4 h-4" />
        </a>

        <a
          href="http://localhost:8000/docs"
          target="_blank"
          rel="noreferrer"
          title="Open Swagger API Docs (:8000/docs)"
          className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition"
        >
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>
    </header>
  );
}