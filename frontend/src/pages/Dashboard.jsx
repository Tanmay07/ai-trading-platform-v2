import React, { useEffect, useState } from 'react';
import GlassCard from '../components/GlassCard';
import { getMarketSummary } from '../services/api';
import { TrendingUp, TrendingDown, DollarSign } from 'lucide-react';

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMarketSummary()
      .then(data => {
        setSummary(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load summary', err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="animate-fade-in" style={{ padding: '2rem' }}>Loading Dashboard...</div>;
  if (!summary) return <div style={{ padding: '2rem' }}>Failed to load dashboard data. Ensure backend is running.</div>;

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header>
        <h1 style={{ fontSize: '2rem', margin: '0 0 0.5rem 0' }}>Portfolio Overview</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Live summary of your active watchlist</p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
        <GlassCard>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ padding: '1rem', background: 'var(--bg-surface-elevated)', borderRadius: '50%' }}>
              <TrendingUp size={24} color="var(--signal-up)" />
            </div>
            <div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>Watchlist Size</p>
              <h2 style={{ margin: 0, fontSize: '1.8rem' }}>{summary.count}</h2>
            </div>
          </div>
        </GlassCard>

        {/* Can add more top-level stats here */}
      </div>

      <GlassCard title="Active Symbols">
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--glass-border)', color: 'var(--text-secondary)' }}>
                <th style={{ padding: '1rem 0.5rem' }}>Symbol</th>
                <th style={{ padding: '1rem 0.5rem' }}>Last Close</th>
                <th style={{ padding: '1rem 0.5rem' }}>Trend (SMA)</th>
              </tr>
            </thead>
            <tbody>
              {summary.assets.map((asset, idx) => (
                <tr key={asset.symbol} style={{ borderBottom: '1px solid var(--glass-border)' }}>
                  <td style={{ padding: '1rem 0.5rem', fontWeight: '500' }}>{asset.symbol}</td>
                  <td style={{ padding: '1rem 0.5rem' }}>₹{asset.last_price?.toFixed(2) || 'N/A'}</td>
                  <td style={{ padding: '1rem 0.5rem' }}>
                    {asset.trend === 'BULLISH' ? (
                      <span style={{ color: 'var(--signal-up)' }}>Bullish</span>
                    ) : asset.trend === 'BEARISH' ? (
                      <span style={{ color: 'var(--signal-down)' }}>Bearish</span>
                    ) : (
                      <span style={{ color: 'var(--signal-neutral)' }}>Neutral</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
}
