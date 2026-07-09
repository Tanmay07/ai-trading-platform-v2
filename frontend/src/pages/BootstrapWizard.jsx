import React, { useEffect, useState } from 'react';
import MetricCard from '../components/ui/MetricCard';
import { PlayCircle, ShieldCheck, Database, HardDrive, Clock, Activity } from 'lucide-react';
import api from '../services/api';

export default function BootstrapWizard() {
  const [preflight, setPreflight] = useState(null);
  const [executionId, setExecutionId] = useState(null);
  const [status, setStatus] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPreflight = async () => {
      try {
        const res = await api.get('/api/bootstrap/preflight');
        setPreflight(res.data);
      } catch (err) {
        console.error("Error fetching preflight:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchPreflight();
  }, []);

  // Poll status if running
  useEffect(() => {
    let interval;
    if (executionId) {
      interval = setInterval(async () => {
        try {
          const res = await api.get(`/api/bootstrap/status/${executionId}`);
          setStatus(res.data);
        } catch (e) {
          console.error(e);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [executionId]);

  const handleStart = async () => {
    try {
      const res = await api.post('/api/bootstrap/start');
      setExecutionId(res.data.execution_id);
    } catch (e) {
      console.error(e);
    }
  };

  if (loading || !preflight) return <div className="p-8">Loading Preflight Engine...</div>;

  return (
    <div className="animate-fade-in flex flex-col gap-6 h-full max-w-5xl">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold mb-1 flex items-center gap-2">
            <PlayCircle className="text-[var(--accent-primary)]" />
            Initialization Bootstrap Manager
          </h1>
          <p className="text-[var(--text-secondary)] text-sm">Preflight Estimation & Resumable Execution Engine</p>
        </div>
        
        {!executionId && (
          <button onClick={handleStart} className="btn btn-primary flex items-center gap-2 px-6">
            <PlayCircle size={18} /> Start Orchestrator
          </button>
        )}
      </div>

      {!executionId ? (
        // Preflight View
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
          <div className="glass-panel p-6">
            <h3 className="font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
              <ShieldCheck className="text-[var(--accent-primary)]" size={20} />
              Preflight Estimation (Phase E1.5)
            </h3>
            
            <div className="space-y-4 text-sm text-[var(--text-secondary)]">
              <div className="flex justify-between border-b border-[var(--glass-border)] pb-2">
                <span>Active Universe:</span>
                <span className="text-[var(--text-primary)] font-mono">{preflight.universe.total_symbols} symbols</span>
              </div>
              
              <div className="flex justify-between border-b border-[var(--glass-border)] pb-2">
                <span>Historical History Available:</span>
                <span className="text-[var(--text-primary)] font-mono">{preflight.historical.already_available} symbols</span>
              </div>
              
              <div className="flex justify-between border-b border-[var(--glass-border)] pb-2">
                <span>Historical Data Missing:</span>
                <span className="text-[var(--signal-down)] font-mono font-bold">{preflight.historical.missing} symbols</span>
              </div>
              
              <div className="flex justify-between border-b border-[var(--glass-border)] pb-2">
                <span>Expected API Requests (Yahoo):</span>
                <span className="text-[var(--text-primary)] font-mono">~{preflight.historical.est_api_calls} calls</span>
              </div>
              
              <div className="flex justify-between pt-2">
                <span>Features to Generate:</span>
                <span className="text-[var(--text-primary)] font-mono">{preflight.features.est_rows_generated.toLocaleString()} rows</span>
              </div>
            </div>
          </div>
          
          <div className="flex flex-col gap-4">
            <MetricCard title="Estimated Execution Time" value={`${preflight.overall.est_time_minutes} min`} icon={<Clock size={18} />} subtitle="Parallel processing active" />
            <MetricCard title="Estimated Storage Impact" value={`${preflight.overall.est_storage_gb} GB`} icon={<HardDrive size={18} />} subtitle="Database + Parquet" />
          </div>
        </div>
      ) : (
        // Execution View
        <div className="glass-panel p-6 mt-4">
           <h3 className="font-semibold text-[var(--text-primary)] mb-6 flex items-center gap-2">
              <Activity className="text-[var(--accent-primary)]" size={20} />
              Live Execution Status
            </h3>
            
            <div className="space-y-4">
              {Object.entries(status).length === 0 ? (
                <div className="text-[var(--text-secondary)] text-sm">Initializing stages...</div>
              ) : (
                Object.entries(status).map(([stage, info]) => (
                  <div key={stage} className="flex justify-between items-center p-3 rounded bg-[var(--bg-base)] border border-[var(--glass-border)]">
                    <span className="font-medium text-[var(--text-primary)]">{stage}</span>
                    <div className="flex items-center gap-4">
                       <span className="text-xs text-[var(--text-muted)] font-mono">{info.progress}</span>
                       <span className={`text-xs px-2 py-1 rounded font-semibold ${
                         info.status === 'Completed' ? 'bg-[var(--signal-up)]/20 text-[var(--signal-up)]' :
                         info.status === 'Running' ? 'bg-[var(--accent-primary)]/20 text-[var(--accent-primary)] animate-pulse' :
                         'bg-[var(--bg-surface)] text-[var(--text-muted)]'
                       }`}>
                         {info.status}
                       </span>
                    </div>
                  </div>
                ))
              )}
            </div>
        </div>
      )}
    </div>
  );
}
