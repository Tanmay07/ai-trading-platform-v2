import React, { useState, useEffect } from 'react';
import GlassCard from '../components/GlassCard';
import { runBacktest, getBacktestRuns } from '../services/api';

export default function BacktestView() {
  const [runs, setRuns] = useState([]);
  const [loadingRuns, setLoadingRuns] = useState(true);
  
  const [form, setForm] = useState({
    symbol: 'RELIANCE.NS',
    start_date: '2023-01-01',
    end_date: '2024-01-01',
    initial_capital: 100000
  });
  
  const [activeResult, setActiveResult] = useState(null);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    fetchRuns();
  }, []);

  const fetchRuns = () => {
    getBacktestRuns().then(data => {
      setRuns(data);
      setLoadingRuns(false);
    }).catch(err => {
      console.error(err);
      setLoadingRuns(false);
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setRunning(true);
    setActiveResult(null);
    try {
      const result = await runBacktest(form);
      setActiveResult(result);
      fetchRuns(); // Refresh history
    } catch (err) {
      alert('Failed to run backtest. Check console.');
      console.error(err);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header>
        <h1 style={{ fontSize: '2rem', margin: '0 0 0.5rem 0' }}>Strategy Backtesting</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Run historical simulations to evaluate strategy performance</p>
      </header>

      <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
        {/* Configuration Form */}
        <div style={{ flex: '1', minWidth: '300px' }}>
          <GlassCard title="Configuration">
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                <label style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Symbol</label>
                <input 
                  type="text" 
                  value={form.symbol} 
                  onChange={(e) => setForm({...form, symbol: e.target.value})} 
                  required 
                />
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  <label style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Start Date</label>
                  <input 
                    type="date" 
                    value={form.start_date} 
                    onChange={(e) => setForm({...form, start_date: e.target.value})} 
                    required 
                  />
                </div>
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  <label style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>End Date</label>
                  <input 
                    type="date" 
                    value={form.end_date} 
                    onChange={(e) => setForm({...form, end_date: e.target.value})} 
                    required 
                  />
                </div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                <label style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Initial Capital (₹)</label>
                <input 
                  type="number" 
                  value={form.initial_capital} 
                  onChange={(e) => setForm({...form, initial_capital: Number(e.target.value)})} 
                  required 
                />
              </div>
              <button 
                type="submit" 
                className="btn btn-primary" 
                disabled={running}
                style={{ marginTop: '0.5rem', opacity: running ? 0.7 : 1 }}
              >
                {running ? 'Running Simulation...' : 'Run Backtest'}
              </button>
            </form>
          </GlassCard>
        </div>

        {/* Results / History Panel */}
        <div style={{ flex: '2', minWidth: '400px' }}>
          {activeResult ? (
            <GlassCard title="Simulation Results">
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.5rem', marginBottom: '2rem' }}>
                <div style={{ background: 'var(--bg-surface-elevated)', padding: '1rem', borderRadius: 'var(--border-radius-sm)', flex: 1, minWidth: '120px' }}>
                  <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Total Return</p>
                  <h3 style={{ margin: '0.5rem 0 0 0', color: activeResult.metrics.total_return >= 0 ? 'var(--signal-up)' : 'var(--signal-down)' }}>
                    {(activeResult.metrics.total_return * 100).toFixed(2)}%
                  </h3>
                </div>
                <div style={{ background: 'var(--bg-surface-elevated)', padding: '1rem', borderRadius: 'var(--border-radius-sm)', flex: 1, minWidth: '120px' }}>
                  <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Sharpe Ratio</p>
                  <h3 style={{ margin: '0.5rem 0 0 0', color: activeResult.metrics.sharpe_ratio >= 1 ? 'var(--signal-up)' : 'inherit' }}>
                    {activeResult.metrics.sharpe_ratio.toFixed(2)}
                  </h3>
                </div>
                <div style={{ background: 'var(--bg-surface-elevated)', padding: '1rem', borderRadius: 'var(--border-radius-sm)', flex: 1, minWidth: '120px' }}>
                  <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Max Drawdown</p>
                  <h3 style={{ margin: '0.5rem 0 0 0', color: 'var(--signal-down)' }}>
                    {(activeResult.metrics.max_drawdown * 100).toFixed(2)}%
                  </h3>
                </div>
                <div style={{ background: 'var(--bg-surface-elevated)', padding: '1rem', borderRadius: 'var(--border-radius-sm)', flex: 1, minWidth: '120px' }}>
                  <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Win Rate</p>
                  <h3 style={{ margin: '0.5rem 0 0 0' }}>
                    {(activeResult.metrics.win_rate * 100).toFixed(1)}%
                  </h3>
                </div>
              </div>

              <div>
                <h4 style={{ margin: '0 0 1rem 0' }}>Recent Trades ({activeResult.trades.length} total)</h4>
                <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                  <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid var(--glass-border)', color: 'var(--text-secondary)' }}>
                        <th style={{ padding: '0.5rem' }}>Action</th>
                        <th style={{ padding: '0.5rem' }}>Entry Date</th>
                        <th style={{ padding: '0.5rem' }}>Exit Date</th>
                        <th style={{ padding: '0.5rem' }}>Return</th>
                      </tr>
                    </thead>
                    <tbody>
                      {activeResult.trades.slice().reverse().map((trade, i) => (
                        <tr key={i} style={{ borderBottom: '1px solid var(--glass-border)' }}>
                          <td style={{ padding: '0.5rem', color: trade.action === 'BUY' ? 'var(--signal-up)' : 'var(--signal-down)' }}>{trade.action}</td>
                          <td style={{ padding: '0.5rem' }}>{trade.entry_date}</td>
                          <td style={{ padding: '0.5rem' }}>{trade.exit_date || 'Open'}</td>
                          <td style={{ padding: '0.5rem', color: trade.return_pct > 0 ? 'var(--signal-up)' : trade.return_pct < 0 ? 'var(--signal-down)' : 'inherit' }}>
                            {trade.return_pct ? `${(trade.return_pct * 100).toFixed(2)}%` : '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </GlassCard>
          ) : (
            <GlassCard title="History">
              {loadingRuns ? (
                <p>Loading history...</p>
              ) : runs.length === 0 ? (
                <p style={{ color: 'var(--text-secondary)' }}>No backtest history found.</p>
              ) : (
                <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
                  {runs.map(run => (
                    <div key={run.id} style={{ 
                      padding: '1rem', 
                      background: 'var(--bg-surface-elevated)', 
                      borderRadius: 'var(--border-radius-sm)',
                      marginBottom: '1rem',
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                    }}>
                      <div>
                        <h4 style={{ margin: '0 0 0.25rem 0' }}>{run.symbol}</h4>
                        <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                          {run.start_date} to {run.end_date}
                        </p>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <h4 style={{ margin: '0 0 0.25rem 0', color: run.total_return >= 0 ? 'var(--signal-up)' : 'var(--signal-down)' }}>
                          {(run.total_return * 100).toFixed(2)}%
                        </h4>
                        <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                          Win Rate: {(run.win_rate * 100).toFixed(1)}%
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </GlassCard>
          )}
        </div>
      </div>
    </div>
  );
}
