import React, { useState } from 'react';
import { X, UploadCloud, CheckCircle2, AlertCircle, FileText } from 'lucide-react';
import { ingestDocument } from '../services/api';

const SAMPLES = [
  {
    title: 'Apple Silicon Architecture',
    text: 'Apple Silicon is a series of system on a chip (SoC) processors using ARM architecture. Announced in November 2020 starting with M1, it features a Unified Memory Architecture (UMA) that shares high-bandwidth memory across CPU, GPU, and Neural Engine without bus transfers.'
  },
  {
    title: 'Enterprise Security Policy 2026',
    text: 'All internal API communications must enforce TLS 1.3 encryption and AES-256 for data at rest. Access to Neo4j graph nodes and Qdrant vector collections requires role-based authentication and audit logging. Responsible AI guardrails must screen for prompt injection and redact PII.'
  }
];

export default function IngestModal({ isOpen, onClose, onSuccess }) {
  const [title, setTitle] = useState('');
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !text.trim()) return;

    setLoading(true);
    setStatus(null);

    try {
      const res = await ingestDocument(title.trim(), text.trim());
      setStatus({ type: 'success', message: res.message || 'Document indexed successfully into Qdrant & Neo4j!' });
      setTimeout(() => {
        setTitle('');
        setText('');
        setStatus(null);
        if (onSuccess) onSuccess();
        onClose();
      }, 1500);
    } catch (err) {
      setStatus({ type: 'error', message: err.response?.data?.detail || err.message || 'Ingestion failed' });
    } finally {
      setLoading(false);
    }
  };

  const loadSample = (sample) => {
    setTitle(sample.title);
    setText(sample.text);
    setStatus(null);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 mb-4">
          <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <UploadCloud className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">Dual-Store Ingestion Studio</h2>
            <p className="text-xs text-slate-400">Chunks & embeds into Qdrant vector store and creates Neo4j graph nodes</p>
          </div>
        </div>

        {/* Sample Templates */}
        <div className="mb-4">
          <p className="text-xs font-medium text-slate-400 mb-2">Quick load sample document:</p>
          <div className="flex gap-2">
            {SAMPLES.map((s, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => loadSample(s)}
                className="flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700/60 transition"
              >
                <FileText className="w-3.5 h-3.5 text-indigo-400" />
                <span>{s.title}</span>
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Document Title</label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Q4 2026 Financial Strategy"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Document Content</label>
            <textarea
              required
              rows={6}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste raw text to be recursively chunked and ingested..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 resize-none font-mono text-xs"
            />
          </div>

          {status && (
            <div className={`p-3 rounded-lg text-xs flex items-center gap-2 ${
              status.type === 'success' 
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
            }`}>
              {status.type === 'success' ? <CheckCircle2 className="w-4 h-4 flex-shrink-0" /> : <AlertCircle className="w-4 h-4 flex-shrink-0" />}
              <span>{status.message}</span>
            </div>
          )}

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !title || !text}
              className="px-4 py-2 text-xs font-medium text-white bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-lg transition shadow-md shadow-indigo-600/20"
            >
              {loading ? 'Chunking & Indexing...' : 'Index Document'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}