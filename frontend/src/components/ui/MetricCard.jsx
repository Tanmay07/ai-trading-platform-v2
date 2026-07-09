import React from 'react';

export default function MetricCard({ title, value, icon, subtitle, trend }) {
  return (
    <div className="glass-panel p-5 flex flex-col gap-2 relative overflow-hidden group">
      <div className="flex justify-between items-center text-sm text-[var(--text-secondary)] font-medium">
        <span>{title}</span>
        {icon && <span className="text-[var(--accent-primary)] opacity-80">{icon}</span>}
      </div>
      <div className="text-2xl font-bold text-[var(--text-primary)]">
        {value}
      </div>
      {(subtitle || trend) && (
        <div className="flex items-center gap-2 text-xs mt-1">
          {trend && (
            <span className={`px-1.5 py-0.5 rounded ${trend === 'up' ? 'text-[var(--signal-up)] bg-[var(--signal-up-bg)]' : trend === 'down' ? 'text-[var(--signal-down)] bg-[var(--signal-down-bg)]' : 'text-[var(--signal-neutral)] bg-[var(--signal-neutral-bg)]'}`}>
              {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}
            </span>
          )}
          <span className="text-[var(--text-muted)]">{subtitle}</span>
        </div>
      )}
      
      {/* Decorative gradient blob */}
      <div className="absolute -bottom-4 -right-4 w-16 h-16 bg-[var(--accent-primary)] rounded-full blur-2xl opacity-10 group-hover:opacity-20 transition-opacity duration-300"></div>
    </div>
  );
}
