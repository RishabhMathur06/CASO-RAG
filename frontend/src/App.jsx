import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ChatArea from './components/ChatArea';
import ContextInspector from './components/ContextInspector';
import IngestModal from './components/IngestModal';
import { checkHealth, queryRAG } from './services/api';

export default function App() {
  const [isOnline, setIsOnline] = useState(false);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeItem, setActiveItem] = useState(null);
  const [isIngestOpen, setIsIngestOpen] = useState(false);

  // Check backend health periodically
  useEffect(() => {
    const pollHealth = async () => {
      const res = await checkHealth();
      setIsOnline(res.status === 'healthy');
    };
    pollHealth();
    const interval = setInterval(pollHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleSendQuery = async (queryText, topK) => {
    setLoading(true);
    try {
      const res = await queryRAG(queryText, topK);
      const newMsg = {
        id: Date.now(),
        query: queryText,
        answer: res.answer,
        context: res.context,
        cached: res.cached,
        clientLatencyMs: res.clientLatencyMs,
        serverProcessTimeMs: res.serverProcessTimeMs,
        top_k: topK,
      };

      setMessages((prev) => [...prev, newMsg]);

      // Automatically inspect context if live retrieval occurred
      if (res.context && !res.context.startsWith('N/A')) {
        setActiveItem(newMsg);
      }
    } catch (err) {
      const errMsg = {
        id: Date.now(),
        query: queryText,
        answer: `Error executing query: ${err.response?.data?.detail || err.message}`,
        context: 'N/A - Error',
        cached: false,
        clientLatencyMs: 0,
        top_k: topK,
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar
        isOnline={isOnline}
        onOpenIngest={() => setIsIngestOpen(true)}
      />

      <div className="flex-1 flex overflow-hidden">
        <ChatArea
          messages={messages}
          onSendQuery={handleSendQuery}
          loading={loading}
          onInspectContext={(item) => setActiveItem(item)}
          activeContextId={activeItem?.id}
        />

        <ContextInspector
          activeItem={activeItem}
          onClose={() => setActiveItem(null)}
        />
      </div>

      <IngestModal
        isOpen={isIngestOpen}
        onClose={() => setIsIngestOpen(false)}
        onSuccess={() => {
          // Document ingested: cache is automatically invalidated by backend
        }}
      />
    </div>
  );
}