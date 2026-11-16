import React from 'react';
import { 
  X, 
  Layers, 
  Zap, 
  Database, 
  CheckCircle2, 
  AlertTriangle,
  Cpu,
  Clock
} from 'lucide-react';

export default function ContextInspector({ activeItem, onClose }) {
  if (!activeItem) return null;

  const { context, cached, clientLatencyMs, serverProcessTimeMs, query } = activeItem;

  // Parse formatted context blocks from search_engine.py
  // Format: [Source: <title> | Relevance Score: <score>]\n<text>
  const parseChunks = (rawContext) => {
    if (!rawContext || rawContext.startsWith('No relevant') || rawContext.startsWith('N/A')) {
      return [];
    }
    const blocks = rawContext.split('\n\n---\n\n');
    return blocks.map((block, idx) => {
      const match = block.match(/^\[Source:\s*(.*?)\s*\|\s*Relevance Score:\s*(.*?)\]\n([\s\S]*)$/);
      if (match) {
        return {
          id: idx + 1,
          title: match[1],
          score: parseFloat(match[2]),
          text: match[3],
        };
      }
      return { id: idx + 1, title: 'Document Chunk', score: null, text: block };
    });
  };

  const chunks = parseChunks(context);

  return (
    <aside className="w-96 border-l border-slate-800 bg-slate-900/60 backdrop-blur-md flex flex-col h-[calc(100vh-4rem)] sticky top-16 overflow-hidden animate-slide-left">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          <h3 className="font-semibold text-sm text-white">Retrieval & Rerank Inspector</h3>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Latency & Cache Stats Bar */}
      <div className="p-4 bg-slate-950/60 border-b border-slate-800 space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400">Response Pipeline:</span>
          {cached ? (
            <span className="flex items-center gap-1 font-semibold text-amber-300 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
              <Zap className="w-3 h-3 fill-amber-300" />
              Redis Cache HIT (&lt; 1ms)
            </span>
          ) : (
            <span className="flex items-center gap-1 font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              <Cpu className="w-3 h-3" />
              Live 2-Stage Retrieval
            </span>
          )}
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs pt-1">
          <div className="bg-slate-900 p-2 rounded border border-slate-800">
            <span className="text-slate-500 block text-[10px]">Client Roundtrip</span>
            <span className="font-mono text-slate-200 font-semibold">{clientLatencyMs || 0} ms</span>
          </div>
          <div className="bg-slate-900 p-2 rounded border border-slate-800">
            <span className="text-slate-500 block text-[10px]">Server Process Time</span>
            <span className="font-mono text-cyan-300 font-semibold">
              {serverProcessTimeMs ? `${serverProcessTimeMs} ms` : 'Cached'}
            </span>
          </div>
        </div>
      </div>

      {/* Chunks List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span>Grounded Context Blocks ({chunks.length})</span>
          <span className="text-[11px] text-slate-500">Threshold: min_score ≥ 0.20</span>
        </div>

        {chunks.length === 0 ? (
          <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 text-center">
            <AlertTriangle className="w-6 h-6 text-amber-400 mx-auto mb-2 opacity-80" />
            <p className="text-xs text-slate-400">
              {context || 'No context chunks retrieved.'}
            </p>
          </div>
        ) : (
          chunks.map((chunk) => (
            <div
              key={chunk.id}
              className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition space-y-2"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-200">
                  <Database className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0" />
                  <span className="truncate max-w-[170px]" title={chunk.title}>
                    {chunk.title}
                  </span>
                </div>
                {chunk.score !== null && (
                  <span className={`text-[11px] font-mono px-1.5 py-0.5 rounded font-semibold border ${
                    chunk.score >= 0.8 
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      : chunk.score >= 0.4
                      ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'
                      : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                  }`}>
                    {chunk.score.toFixed(4)}
                  </span>
                )}
              </div>

              <p className="text-xs font-mono text-slate-300 bg-slate-950/70 p-2.5 rounded-lg border border-slate-800/80 leading-relaxed">
                {chunk.text}
              </p>

              <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1">
                <span className="flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                  Neo4j Verified Lineage
                </span>
                <span>Chunk #{chunk.id}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}