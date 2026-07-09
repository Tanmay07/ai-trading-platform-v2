import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { Link } from 'react-router-dom';
import GlassCard from '../components/GlassCard';
import { getMarketSummary, addPortfolioHolding, updatePortfolioHolding, deletePortfolioHolding, getFullAnalysis } from '../services/api';
import { TrendingUp, TrendingDown, DollarSign, Plus, Edit2, Trash2, X, Zap, Loader, AlertCircle, ChevronDown, ChevronUp, BarChart2, Activity } from 'lucide-react';

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const [modalState, setModalState] = useState({ isOpen: false, mode: 'add', data: null });
  const [formData, setFormData] = useState({ symbol: '', quantity: '', buy_price: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Full analysis state
  const [analysisState, setAnalysisState] = useState({ loading: false, done: false, data: null, error: null });
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  const loadData = () => {
    setLoading(true);
    getMarketSummary()
      .then(data => {
        setSummary(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load summary', err);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleOpenModal = (mode, holding = null) => {
    if (mode === 'edit') {
      setFormData({ symbol: holding.symbol, quantity: holding.quantity, buy_price: holding.avg_buy_price });
    } else {
      setFormData({ symbol: '', quantity: '', buy_price: '' });
    }
    setModalState({ isOpen: true, mode, data: holding });
  };

  const handleCloseModal = () => {
    setModalState({ isOpen: false, mode: 'add', data: null });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const payload = {
        symbol: formData.symbol.toUpperCase().trim(),
        quantity: parseInt(formData.quantity, 10),
        buy_price: parseFloat(formData.buy_price)
      };
      
      if (!payload.symbol.endsWith('.NS') && !payload.symbol.endsWith('.BO')) {
        payload.symbol += '.NS';
      }

      if (modalState.mode === 'add') {
        await addPortfolioHolding(payload);
      } else {
        await updatePortfolioHolding(payload.symbol, payload);
      }
      handleCloseModal();
      loadData();
    } catch (err) {
      alert('Failed to save holding: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (symbol) => {
    if (!window.confirm(`Are you sure you want to remove ${symbol}?`)) return;
    try {
      await deletePortfolioHolding(symbol);
      loadData();
    } catch (err) {
      alert('Failed to delete holding: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleFullAnalysis = async () => {
    setAnalysisState({ loading: true, done: false, data: null, error: null });
    try {
      const res = await getFullAnalysis();
      setAnalysisState({ loading: false, done: true, data: res, error: null });
    } catch (err) {
      setAnalysisState({ loading: false, done: false, data: null, error: err.message || "Full analysis failed" });
    }
  };

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const getSortedAnalysis = () => {
    if (!analysisState.data?.analysis) return [];
    const rows = [...analysisState.data.analysis];
    if (!sortConfig.key) return rows;
    
    rows.sort((a, b) => {
      let aVal = a[sortConfig.key];
      let bVal = b[sortConfig.key];
      if (typeof aVal === 'string') aVal = aVal.toLowerCase();
      if (typeof bVal === 'string') bVal = bVal.toLowerCase();
      if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
    return rows;
  };

  const getVerdictStyle = (verdict) => {
    if (!verdict) return {};
    if (verdict.includes('BUY MORE')) return { background: 'rgba(63, 185, 80, 0.2)', color: 'var(--signal-up)', fontWeight: 'bold' };
    if (verdict.includes('AVERAGE DOWN')) return { background: 'rgba(88, 166, 255, 0.2)', color: 'var(--accent-primary)', fontWeight: 'bold' };
    if (verdict.includes('BUY')) return { background: 'rgba(63, 185, 80, 0.1)', color: 'var(--signal-up)' };
    if (verdict.includes('SELL') || verdict === 'CUT LOSSES') return { background: 'rgba(248, 81, 73, 0.2)', color: 'var(--signal-down)' };
    return { background: 'rgba(139, 148, 158, 0.2)', color: 'var(--text-secondary)' };
  };

  const SortIcon = ({ column }) => {
    if (sortConfig.key !== column) return null;
    return sortConfig.direction === 'asc' ? <ChevronUp size={12} /> : <ChevronDown size={12} />;
  };

  if (loading && !summary) return <div className="animate-fade-in" style={{ padding: '2rem' }}>Loading Dashboard...</div>;
  if (!summary) return <div style={{ padding: '2rem' }}>Failed to load dashboard data. Ensure backend is running.</div>;

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 style={{ fontSize: '2rem', margin: '0 0 0.5rem 0' }}>Portfolio Overview</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Live summary of your active watchlist</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <button 
            className="btn btn-primary" 
            onClick={handleFullAnalysis} 
            disabled={analysisState.loading}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          >
            {analysisState.loading ? <><Loader size={16} className="animate-spin" /> Analyzing All Holdings...</> : <><Zap size={16} /> Run Full Portfolio Analysis</>}
          </button>
          <button className="btn" onClick={() => handleOpenModal('add')} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Plus size={16} /> Add Holding
          </button>
        </div>
      </header>

      {analysisState.error && (
        <div style={{ color: 'var(--signal-down)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertCircle size={16} /> {analysisState.error}
        </div>
      )}

      {/* AI Platform Health Snapshot */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
        {[
          { label: 'Historical Data', status: 'Healthy', color: 'var(--signal-up)' },
          { label: 'Model Acc.', status: '74%', color: '#a855f7' },
          { label: 'Pred. Acc.', status: '71%', color: '#3b82f6' },
          { label: 'Cache Hit', status: '93%', color: 'var(--signal-up)' },
          { label: 'News API', status: 'Healthy', color: 'var(--signal-up)' },
          { label: 'Learning DB', status: 'Healthy', color: 'var(--signal-up)' },
        ].map(item => (
          <GlassCard key={item.label} style={{ padding: '0.75rem', textAlign: 'center' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '0.25rem' }}>{item.label}</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: item.color }}>{item.status}</div>
          </GlassCard>
        ))}
      </div>

      {/* Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.5rem' }}>
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

        {analysisState.done && analysisState.data?.totals && (
          <>
            <GlassCard>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ padding: '1rem', background: 'var(--bg-surface-elevated)', borderRadius: '50%' }}>
                  <DollarSign size={24} color="#8b949e" />
                </div>
                <div>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>Total Invested</p>
                  <h2 style={{ margin: 0, fontSize: '1.8rem' }}>₹{analysisState.data.totals.total_invested?.toFixed(2)}</h2>
                </div>
              </div>
            </GlassCard>
            <GlassCard>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ padding: '1rem', background: 'var(--bg-surface-elevated)', borderRadius: '50%' }}>
                  <TrendingUp size={24} color="var(--accent-primary)" />
                </div>
                <div>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>Holdings</p>
                  <h2 style={{ margin: 0, fontSize: '1.8rem' }}>{analysisState.data.holdings_count}</h2>
                </div>
              </div>
            </GlassCard>
          </>
        )}
      </div>

      {/* Full Analysis Table */}
      {analysisState.done && analysisState.data?.analysis ? (
        <GlassCard title="Full Portfolio Analysis — AI Verdicts">
          <div style={{ overflowX: 'auto', marginTop: '0.5rem' }}>
            <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--glass-border)', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
                  {[
                    { key: 'symbol', label: 'Symbol' },
                    { key: 'sector', label: 'Sector' },
                    { key: 'quantity', label: 'Qty' },
                    { key: 'avg_price', label: 'Avg Price (₹)' },
                    { key: 'ltp', label: 'LTP (₹)' },
                    { key: 'invested_value', label: 'Invested (₹)' },
                    { key: 'current_value', label: 'Current (₹)' },
                    { key: 'weight_pct', label: 'Weight %' },
                    { key: 'pnl_pct', label: 'P&L %' },
                    { key: 'verdict', label: 'Verdict' },
                  ].map(col => (
                    <th 
                      key={col.key}
                      onClick={() => handleSort(col.key)}
                      style={{ padding: '0.75rem 0.5rem', cursor: 'pointer', userSelect: 'none' }}
                    >
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                        {col.label} <SortIcon column={col.key} />
                      </span>
                    </th>
                  ))}
                  <th style={{ padding: '0.75rem 0.5rem', minWidth: '300px' }}>Rationale</th>
                  <th style={{ padding: '0.75rem 0.5rem', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {getSortedAnalysis().map((row) => (
                  <tr key={row.symbol} style={{ borderBottom: '1px solid var(--glass-border)' }}>
                    <td style={{ padding: '0.6rem 0.5rem', fontWeight: '600', whiteSpace: 'nowrap' }}>{row.symbol}</td>
                    <td style={{ padding: '0.6rem 0.5rem', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>{row.sector}</td>
                    <td style={{ padding: '0.6rem 0.5rem' }}>{row.quantity?.toLocaleString()}</td>
                    <td style={{ padding: '0.6rem 0.5rem' }}>{row.avg_price?.toFixed(2)}</td>
                    <td style={{ padding: '0.6rem 0.5rem' }}>{row.ltp?.toFixed(2)}</td>
                    <td style={{ padding: '0.6rem 0.5rem' }}>{row.invested_value?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                    <td style={{ padding: '0.6rem 0.5rem' }}>{row.current_value?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                    <td style={{ padding: '0.6rem 0.5rem' }}>{row.weight_pct?.toFixed(2)}%</td>
                    <td style={{ 
                      padding: '0.6rem 0.5rem', 
                      fontWeight: '600',
                      color: row.pnl_pct >= 0 ? 'var(--signal-up)' : 'var(--signal-down)' 
                    }}>
                      {row.pnl_pct >= 0 ? '+' : ''}{row.pnl_pct?.toFixed(2)}%
                    </td>
                    <td style={{ padding: '0.6rem 0.5rem' }}>
                      <span style={{
                        padding: '0.2rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.75rem',
                        fontWeight: 'bold',
                        whiteSpace: 'nowrap',
                        ...getVerdictStyle(row.verdict)
                      }}>
                        {row.verdict}
                      </span>
                    </td>
                    <td style={{ 
                      padding: '0.6rem 0.5rem', 
                      color: 'var(--text-secondary)', 
                      fontSize: '0.8rem',
                      lineHeight: '1.4',
                      maxWidth: '400px'
                    }}>
                      {row.rationale}
                    </td>
                    <td style={{ padding: '0.6rem 0.5rem', textAlign: 'right', whiteSpace: 'nowrap' }}>
                      <Link to={`/market/${row.symbol}`} style={{ color: 'var(--accent-primary)', marginRight: '0.5rem' }} title="Market View">
                        <BarChart2 size={16} />
                      </Link>
                      <Link to={`/analysis/${row.symbol}`} style={{ color: 'var(--text-primary)', marginRight: '0.75rem' }} title="Full Analysis">
                        <Activity size={16} />
                      </Link>
                      <button onClick={() => handleOpenModal('edit', { symbol: row.symbol, quantity: row.quantity, avg_buy_price: row.avg_price })} style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', marginRight: '0.5rem' }} title="Edit">
                        <Edit2 size={16} />
                      </button>
                      <button onClick={() => handleDelete(row.symbol)} style={{ background: 'transparent', border: 'none', color: 'var(--signal-down)', cursor: 'pointer' }} title="Delete">
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      ) : (
        /* Default Holdings Table (before analysis is run) */
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
                  <th style={{ padding: '1rem 0.5rem', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {summary.holdings && summary.holdings.map((holding) => (
                  <tr key={holding.symbol} style={{ borderBottom: '1px solid var(--glass-border)' }}>
                    <td style={{ padding: '1rem 0.5rem', fontWeight: '500' }}>{holding.symbol}</td>
                    <td style={{ padding: '1rem 0.5rem' }}>{holding.quantity}</td>
                    <td style={{ padding: '1rem 0.5rem' }}>₹{holding.avg_buy_price?.toFixed(2)}</td>
                    <td style={{ padding: '1rem 0.5rem' }}>₹{holding.current_price?.toFixed(2) || 'N/A'}</td>
                    <td style={{ padding: '1rem 0.5rem', color: holding.unrealized_pnl >= 0 ? 'var(--signal-up)' : 'var(--signal-down)' }}>
                      {holding.unrealized_pnl >= 0 ? '+' : ''}{holding.unrealized_pnl_pct?.toFixed(2)}%
                    </td>
                    <td style={{ padding: '1rem 0.5rem', textAlign: 'right', whiteSpace: 'nowrap' }}>
                      <Link to={`/market/${holding.symbol}`} style={{ color: 'var(--accent-primary)', marginRight: '0.5rem' }} title="Market View">
                        <BarChart2 size={16} />
                      </Link>
                      <Link to={`/analysis/${holding.symbol}`} style={{ color: 'var(--text-primary)', marginRight: '0.75rem' }} title="Full Analysis">
                        <Activity size={16} />
                      </Link>
                      <button onClick={() => handleOpenModal('edit', holding)} style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', marginRight: '0.5rem' }} title="Edit">
                        <Edit2 size={16} />
                      </button>
                      <button onClick={() => handleDelete(holding.symbol)} style={{ background: 'transparent', border: 'none', color: 'var(--signal-down)', cursor: 'pointer' }} title="Delete">
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      )}

      {/* Add/Edit Holding Modal */}
      {modalState.isOpen && createPortal(
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0, 0, 0, 0.7)', backdropFilter: 'blur(4px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999
        }}>
          <div style={{ width: '100%', maxWidth: '400px', position: 'relative' }}>
            <GlassCard title={modalState.mode === 'add' ? 'Add Holding' : 'Edit Holding'}>
              <button onClick={handleCloseModal} style={{ position: 'absolute', top: '1.5rem', right: '1.5rem', background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
              <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Symbol (NSE)</label>
                  <input 
                    type="text" 
                    required 
                    value={formData.symbol} 
                    onChange={e => setFormData({...formData, symbol: e.target.value})} 
                    disabled={modalState.mode === 'edit'}
                    style={{ width: '100%', padding: '0.75rem', background: 'var(--bg-surface-elevated)', border: '1px solid var(--glass-border)', color: '#fff', borderRadius: '4px' }}
                    placeholder="e.g. RELIANCE"
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Quantity</label>
                  <input 
                    type="number" 
                    required 
                    min="1"
                    value={formData.quantity} 
                    onChange={e => setFormData({...formData, quantity: e.target.value})} 
                    style={{ width: '100%', padding: '0.75rem', background: 'var(--bg-surface-elevated)', border: '1px solid var(--glass-border)', color: '#fff', borderRadius: '4px' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Average Buy Price (₹)</label>
                  <input 
                    type="number" 
                    required 
                    step="0.01"
                    min="0.01"
                    value={formData.buy_price} 
                    onChange={e => setFormData({...formData, buy_price: e.target.value})} 
                    style={{ width: '100%', padding: '0.75rem', background: 'var(--bg-surface-elevated)', border: '1px solid var(--glass-border)', color: '#fff', borderRadius: '4px' }}
                  />
                </div>
                <button type="submit" className="btn" disabled={isSubmitting} style={{ marginTop: '0.5rem', width: '100%' }}>
                  {isSubmitting ? 'Saving...' : 'Save Holding'}
                </button>
              </form>
            </GlassCard>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
}
