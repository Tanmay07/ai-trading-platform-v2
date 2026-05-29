import React from 'react';

export default function GlassCard({ title, children, style = {} }) {
  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem', ...style }}>
      {title && (
        <h3 style={{ 
          fontSize: '1.1rem', 
          fontWeight: '600', 
          margin: 0,
          color: 'var(--text-primary)',
          borderBottom: '1px solid var(--glass-border)',
          paddingBottom: '0.75rem'
        }}>
          {title}
        </h3>
      )}
      <div style={{ flex: 1 }}>
        {children}
      </div>
    </div>
  );
}
