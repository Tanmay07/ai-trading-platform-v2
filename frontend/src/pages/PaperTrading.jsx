import React, { useState, useEffect } from 'react';
import { getPaperPortfolios, deletePaperPortfolio } from '../services/api';
import { Target, Trash2, TrendingUp, TrendingDown, Clock, Loader } from 'lucide-react';
import GlassCard from '../components/GlassCard';

const PaperTrading = () => {
  const [portfolios, setPortfolios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPortfolios = async () => {
    try {
      setLoading(true);
      const data = await getPaperPortfolios();
      setPortfolios(data || []);
      setError(null);
    } catch (err) {
      setError(err.message || "Failed to load paper portfolios");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolios();
  }, []);

  const handleDelete = async (id) => {
    if (window.confirm("Are you sure you want to delete this paper portfolio?")) {
      try {
        await deletePaperPortfolio(id);
        fetchPortfolios();
      } catch (err) {
        alert("Failed to delete: " + err.message);
      }
    }
  };

  if (loading) {
    return <div style={{ padding: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Loader className="animate-spin" /> Loading Paper Trades...</div>;
  }

  if (error) {
    return <div style={{ padding: '2rem', color: 'var(--signal-down)' }}>Error: {error}</div>;
  }

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem', paddingBottom: '2rem' }}>
      <header>
        <h1 style={{ fontSize: '2rem', margin: '0 0 0.5rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Target size={28} style={{ color: 'var(--accent-primary)' }}/> Paper Trading Simulator
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>Track algorithmic trade suggestions in real-time without risking real capital.</p>
      </header>

      {portfolios.length === 0 ? (
        <GlassCard>
          <div style={{ textAlign: 'center', padding: '3rem 0', color: 'var(--text-secondary)' }}>
            <Target size={48} style={{ margin: '0 auto 1rem auto', opacity: 0.5 }} />
            <p>No active paper trades found.</p>
            <p style={{ fontSize: '0.875rem' }}>Go to <b>Weekly Targets</b> to create a new paper portfolio from AI suggestions.</p>
          </div>
        </GlassCard>
      ) : (
        portfolios.map((portfolio) => (
          <GlassCard key={portfolio.id} style={{ marginBottom: '1rem' }}>
            {/* Portfolio Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--glass-border)', paddingBottom: '1rem', marginBottom: '1rem' }}>
              <div>
                <h3 style={{ margin: '0 0 0.25rem 0', fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  Started on {new Date(portfolio.created_at).toLocaleDateString()}
                  <span style={{ fontSize: '0.75rem', fontWeight: 'normal', color: 'var(--text-secondary)', background: 'var(--bg-surface-elevated)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                    <Clock size={12} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom' }}/>
                    {new Date(portfolio.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </h3>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  Target Goal: <span style={{ color: 'var(--text-primary)' }}>₹{portfolio.target?.toLocaleString()}</span> | 
                  Expected: <span style={{ color: 'var(--signal-up)' }}>₹{portfolio.expected_total_profit?.toLocaleString()}</span>
                </div>
              </div>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Overall P&L</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: portfolio.total_pnl >= 0 ? 'var(--signal-up)' : 'var(--signal-down)' }}>
                    {portfolio.total_pnl >= 0 ? '+' : ''}₹{portfolio.total_pnl?.toLocaleString()} ({portfolio.total_pnl_pct}%)
                  </div>
                </div>
                <button 
                  onClick={() => handleDelete(portfolio.id)}
                  style={{ background: 'transparent', border: 'none', color: 'var(--signal-down)', cursor: 'pointer', padding: '0.5rem' }}
                  title="Delete Paper Portfolio"
                >
                  <Trash2 size={20} />
                </button>
              </div>
            </div>

            {/* Holdings Table */}
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--glass-border)', color: 'var(--text-secondary)' }}>
                    <th style={{ padding: '0.75rem 0.5rem' }}>Symbol</th>
                    <th style={{ padding: '0.75rem 0.5rem' }}>Qty</th>
                    <th style={{ padding: '0.75rem 0.5rem' }}>Entry (₹)</th>
                    <th style={{ padding: '0.75rem 0.5rem' }}>LTP (₹)</th>
                    <th style={{ padding: '0.75rem 0.5rem' }}>Target (₹)</th>
                    <th style={{ padding: '0.75rem 0.5rem' }}>Stop (₹)</th>
                    <th style={{ padding: '0.75rem 0.5rem' }}>Invested (₹)</th>
                    <th style={{ padding: '0.75rem 0.5rem', textAlign: 'right' }}>P&L (₹)</th>
                    <th style={{ padding: '0.75rem 0.5rem', textAlign: 'center' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {portfolio.stocks.map((stock) => (
                    <tr key={stock.symbol} style={{ borderBottom: '1px solid var(--glass-border)' }}>
                      <td style={{ padding: '0.75rem 0.5rem', fontWeight: '500' }}>{stock.symbol}</td>
                      <td style={{ padding: '0.75rem 0.5rem' }}>{stock.quantity}</td>
                      <td style={{ padding: '0.75rem 0.5rem' }}>{stock.entry_price}</td>
                      <td style={{ padding: '0.75rem 0.5rem', fontWeight: 'bold' }}>{stock.current_price}</td>
                      <td style={{ padding: '0.75rem 0.5rem', color: 'var(--signal-up)' }}>{stock.target_price}</td>
                      <td style={{ padding: '0.75rem 0.5rem', color: 'var(--signal-down)' }}>{stock.stop_loss}</td>
                      <td style={{ padding: '0.75rem 0.5rem' }}>{stock.invested?.toLocaleString()}</td>
                      <td style={{ padding: '0.75rem 0.5rem', textAlign: 'right', fontWeight: 'bold', color: stock.pnl >= 0 ? 'var(--signal-up)' : 'var(--signal-down)' }}>
                        {stock.pnl >= 0 ? '+' : ''}{stock.pnl?.toLocaleString()} ({stock.pnl_pct}%)
                      </td>
                      <td style={{ padding: '0.75rem 0.5rem', textAlign: 'center' }}>
                        <span style={{
                          padding: '0.2rem 0.5rem',
                          borderRadius: '4px',
                          fontSize: '0.75rem',
                          fontWeight: 'bold',
                          color: stock.status === 'Target Hit' ? 'var(--signal-up)' : stock.status === 'Stop Loss Hit' ? 'var(--signal-down)' : 'var(--text-secondary)',
                          background: stock.status === 'Target Hit' ? 'var(--signal-up-bg)' : stock.status === 'Stop Loss Hit' ? 'var(--signal-down-bg)' : 'var(--bg-surface-elevated)',
                        }}>
                          {stock.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            {/* Portfolio Footer */}
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--glass-border)', fontSize: '0.85rem' }}>
              <div style={{ color: 'var(--text-secondary)' }}>Total Capital Deployed: <span style={{ color: 'var(--text-primary)', fontWeight: 'bold' }}>₹{portfolio.total_invested?.toLocaleString()}</span></div>
              <div style={{ color: 'var(--text-secondary)' }}>Current Value: <span style={{ color: 'var(--text-primary)', fontWeight: 'bold' }}>₹{portfolio.total_current_value?.toLocaleString()}</span></div>
            </div>
          </GlassCard>
        ))
      )}
    </div>
  );
};

export default PaperTrading;
