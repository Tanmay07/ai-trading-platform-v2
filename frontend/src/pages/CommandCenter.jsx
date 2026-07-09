import React from 'react';
import MetricCard from '../components/ui/MetricCard';
import Badge from '../components/ui/Badge';
import { ShieldAlert, Activity, CheckCircle, Database, Server, ServerCrash } from 'lucide-react';

export default function CommandCenter() {
  const systemStatus = [
    { title: "Market Data", value: "Healthy", icon: <Database size={18} />, trend: "up", subtitle: "Phase D3 Active" },
    { title: "Feature Store", value: "Updated", icon: <Database size={18} />, trend: "up", subtitle: "Phase D2 Active" },
    { title: "AI Models", value: "9 Online", icon: <Activity size={18} />, trend: "up", subtitle: "Phase D5 Active" },
    { title: "Learning DB", value: "Healthy", icon: <Server size={18} />, trend: "up", subtitle: "Phase D6 Active" },
    { title: "Brokers", value: "Connected", icon: <Server size={18} />, trend: "up", subtitle: "Zerodha, Angel" },
    { title: "News Stream", value: "Healthy", icon: <ServerCrash size={18} />, subtitle: "Phase D4 Active" },
  ];

  return (
    <div className="animate-fade-in flex flex-col gap-6 h-full">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold mb-1 flex items-center gap-2">
            <ShieldAlert className="text-[var(--accent-primary)]" />
            HFOS Command Center
          </h1>
          <p className="text-[var(--text-secondary)] text-sm">Phase 10 & 12: Enterprise Infrastructure and Monitoring</p>
        </div>
        <button className="btn bg-[var(--signal-down)] hover:bg-red-600 text-white border-red-600 font-bold shadow-[0_0_15px_rgba(248,81,73,0.4)]">
          KILL SWITCH
        </button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {systemStatus.map((m, i) => (
          <MetricCard key={i} {...m} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1">
        <div className="glass-panel p-5 flex flex-col">
          <h3 className="font-semibold text-[var(--text-primary)] mb-4 border-b border-[var(--glass-border)] pb-2">Recent Execution Logs</h3>
          <div className="font-mono text-xs text-[var(--text-secondary)] space-y-2 overflow-auto">
            <div className="text-[var(--signal-up)]">[INFO] 09:15:23 - Order filled BEL.NS (Qty: 250 @ 284.50)</div>
            <div className="text-[var(--text-primary)]">[INFO] 09:16:01 - AI Committee consensus reached for TCS.NS (89%)</div>
            <div className="text-[var(--signal-down)]">[WARN] 09:18:42 - Slippage detected on HDFCBANK (+0.12%)</div>
            <div className="text-[var(--text-primary)]">[INFO] 09:20:00 - Alpha factors recalibrated successfully</div>
            <div className="text-[var(--text-primary)]">[INFO] 09:22:15 - Portfolio allocator finished daily rebalance check</div>
          </div>
        </div>

        <div className="glass-panel p-5 flex flex-col">
          <h3 className="font-semibold text-[var(--text-primary)] mb-4 border-b border-[var(--glass-border)] pb-2">Compliance Engine</h3>
          <div className="flex-1 flex flex-col justify-center items-center text-center">
            <CheckCircle size={48} className="text-[var(--signal-up)] mb-4" />
            <h4 className="text-lg font-bold text-[var(--text-primary)]">All Systems Compliant</h4>
            <p className="text-sm text-[var(--text-secondary)] max-w-sm mt-2">
              No sector limit breaches. Margin utilization at 41%. No restricted securities in queue.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
