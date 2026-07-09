import React from 'react';

export default function Badge({ children, variant = 'neutral' }) {
  const variants = {
    neutral: 'text-[var(--text-secondary)] bg-[var(--bg-surface-elevated)] border-[var(--glass-border)]',
    success: 'text-[var(--signal-up)] bg-[var(--signal-up-bg)] border-[rgba(63,185,80,0.2)]',
    danger: 'text-[var(--signal-down)] bg-[var(--signal-down-bg)] border-[rgba(248,81,73,0.2)]',
    primary: 'text-[var(--accent-primary)] bg-[rgba(88,166,255,0.1)] border-[rgba(88,166,255,0.2)]',
    warning: 'text-[#e3b341] bg-[rgba(227,179,65,0.1)] border-[rgba(227,179,65,0.2)]',
  };

  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${variants[variant]}`}>
      {children}
    </span>
  );
}
