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
              <DollarSign size={24} color="var(--accent-primary)" />
            </div>
            <div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>Total Value</p>
              <h2 style={{ margin: 0, fontSize: '1.8rem' }}>₹{summary.total_market_value?.toFixed(2) || '0.00'}</h2>
            </div>
          </div>
        </GlassCard>

        <GlassCard>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ padding: '1rem', background: 'var(--bg-surface-elevated)', borderRadius: '50%' }}>
              {summary.total_unrealized_pnl >= 0 ? <TrendingUp size={24} color="var(--signal-up)" /> : <TrendingDown size={24} color="var(--signal-down)" />}
            </div>
            <div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>Unrealized P&L</p>
              <h2 style={{ margin: 0, fontSize: '1.8rem', color: summary.total_unrealized_pnl >= 0 ? 'var(--signal-up)' : 'var(--signal-down)' }}>
                {summary.total_unrealized_pnl >= 0 ? '+' : ''}₹{summary.total_unrealized_pnl?.toFixed(2) || '0.00'}
              </h2>
            </div>
          </div>
        </GlassCard>
      </div>

      <GlassCard title="Active Holdings">
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--glass-border)', color: 'var(--text-secondary)' }}>
                <th style={{ padding: '1rem 0.5rem' }}>Symbol</th>
                <th style={{ padding: '1rem 0.5rem' }}>Qty</th>
                <th style={{ padding: '1rem 0.5rem' }}>Avg Price</th>
                <th style={{ padding: '1rem 0.5rem' }}>Current Price</th>
                <th style={{ padding: '1rem 0.5rem' }}>P&L (%)</th>
              </tr>
            </thead>
            <tbody>
              {summary.holdings.map((holding) => (
                <tr key={holding.symbol} style={{ borderBottom: '1px solid var(--glass-border)' }}>
                  <td style={{ padding: '1rem 0.5rem', fontWeight: '500' }}>{holding.symbol}</td>
                  <td style={{ padding: '1rem 0.5rem' }}>{holding.quantity}</td>
                  <td style={{ padding: '1rem 0.5rem' }}>₹{holding.avg_buy_price?.toFixed(2)}</td>
                  <td style={{ padding: '1rem 0.5rem' }}>₹{holding.current_price?.toFixed(2) || 'N/A'}</td>
                  <td style={{ padding: '1rem 0.5rem', color: holding.unrealized_pnl >= 0 ? 'var(--signal-up)' : 'var(--signal-down)' }}>
                    {holding.unrealized_pnl >= 0 ? '+' : ''}{holding.unrealized_pnl_pct?.toFixed(2)}%
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
