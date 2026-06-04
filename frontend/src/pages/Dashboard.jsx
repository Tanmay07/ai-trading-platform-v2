import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import GlassCard from '../components/GlassCard';
import { getMarketSummary, addPortfolioHolding, updatePortfolioHolding, deletePortfolioHolding, getStrategy } from '../services/api';
import { TrendingUp, TrendingDown, DollarSign, Plus, Edit2, Trash2, X, Zap, Loader, AlertCircle } from 'lucide-react';

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const [modalState, setModalState] = useState({ isOpen: false, mode: 'add', data: null });
  const [detailsModal, setDetailsModal] = useState({ isOpen: false, data: null });
  const [formData, setFormData] = useState({ symbol: '', quantity: '', buy_price: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [strategyState, setStrategyState] = useState({ loading: false, done: false, predictions: null, error: null });

  const generateConclusion = (pred) => {
    if (!pred) return "";
    const action = pred.action;
    const score = pred.confidence_score;
    
    if (action === 'HOLD') {
      if (score < 30) {
        return "The AI is highly uncertain due to heavily conflicting signals. For example, positive price trends might be entirely offset by bearish constraints like dead volume or extreme volatility. The engine recommends holding your current position to avoid getting chopped out, but advises against allocating fresh capital until true conviction returns.";
      } else {
        return "The AI recommends a HOLD. The current market conditions for this stock are consolidating or range-bound, lacking a strong directional catalyst to justify a new entry or exit.";
      }
    } else if (action === 'BUY') {
      if (score >= 50) {
        return "The AI has strong conviction in a BUY signal. There is excellent alignment across price momentum, volume support, and technical indicators suggesting an upward continuation.";
      } else {
        return "The AI suggests a cautious BUY. While the technicals lean positive, the conviction is moderate, indicating potential upside but with some lingering risks or missing confirmations.";
      }
    } else if (action === 'SELL') {
      if (score >= 50) {
        return "The AI strongly recommends a SELL. Multiple technical dimensions indicate severe deterioration. Exiting or reducing the position is advised to protect against further downside risk.";
      } else {
        return "The AI leans towards a SELL. The technical structure is weakening, though the immediate downside momentum is moderate. Consider tightening stop-losses.";
      }
    }
    return "The engine has analyzed the technicals and sentiment to generate this recommendation.";
  };

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

  const handleStrategy = async () => {
    if (!summary || !summary.holdings || summary.holdings.length === 0) return;
    const symbols = summary.holdings.map(h => h.symbol);
    setStrategyState({ loading: true, done: false, predictions: null, error: null });
    
    try {
      const res = await getStrategy(symbols);
      const predMap = {};
      res.predictions.forEach(p => predMap[p.symbol] = p);
      setStrategyState({ loading: false, done: true, predictions: predMap, error: null });
    } catch (err) {
      setStrategyState({ loading: false, done: false, predictions: null, error: err.message || "Strategy generation failed" });
    }
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
            onClick={handleStrategy} 
            disabled={strategyState.loading || summary.holdings.length === 0}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          >
            {strategyState.loading ? <><Loader size={16} className="animate-spin" /> Analyzing...</> : <><Zap size={16} /> Buy/Hold/Sell Analysis Engine</>}
          </button>
          <button className="btn" onClick={() => handleOpenModal('add')} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Plus size={16} /> Add Holding
          </button>
        </div>
      </header>
      {strategyState.error && (
        <div style={{ color: 'var(--signal-down)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertCircle size={16} /> {strategyState.error}
        </div>
      )}

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
                {strategyState.done && (
                  <>
                    <th style={{ padding: '1rem 0.5rem' }}>Signal</th>
                    <th style={{ padding: '1rem 0.5rem' }}>Target</th>
                    <th style={{ padding: '1rem 0.5rem' }}>Stop Loss</th>
                  </>
                )}
                <th style={{ padding: '1rem 0.5rem', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {summary.holdings.map((holding) => {
                const pred = strategyState.predictions ? strategyState.predictions[holding.symbol] : null;
                return (
                <tr key={holding.symbol} style={{ borderBottom: '1px solid var(--glass-border)' }}>
                  <td style={{ padding: '1rem 0.5rem', fontWeight: '500' }}>{holding.symbol}</td>
                  <td style={{ padding: '1rem 0.5rem' }}>{holding.quantity}</td>
                  <td style={{ padding: '1rem 0.5rem' }}>₹{holding.avg_buy_price?.toFixed(2)}</td>
                  <td style={{ padding: '1rem 0.5rem' }}>₹{holding.current_price?.toFixed(2) || 'N/A'}</td>
                  <td style={{ padding: '1rem 0.5rem', color: holding.unrealized_pnl >= 0 ? 'var(--signal-up)' : 'var(--signal-down)' }}>
                    {holding.unrealized_pnl >= 0 ? '+' : ''}{holding.unrealized_pnl_pct?.toFixed(2)}%
                  </td>
                  {strategyState.done && (
                    <>
                      <td style={{ padding: '1rem 0.5rem' }}>
                        {pred ? (
                          <span 
                            onClick={() => setDetailsModal({ isOpen: true, data: pred })}
                            style={{ 
                              padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 'bold',
                              background: pred.action === 'BUY' ? 'rgba(63, 185, 80, 0.2)' : pred.action === 'SELL' ? 'rgba(248, 81, 73, 0.2)' : 'rgba(139, 148, 158, 0.2)',
                              color: pred.action === 'BUY' ? 'var(--signal-up)' : pred.action === 'SELL' ? 'var(--signal-down)' : 'var(--text-secondary)',
                              cursor: 'pointer',
                              display: 'inline-flex', alignItems: 'center', gap: '0.2rem'
                            }}
                            title="Click to view AI reasoning"
                          >
                            {pred.action} ({Math.round(pred.confidence_score)}%)
                          </span>
                        ) : '-'}
                      </td>
                      <td style={{ padding: '1rem 0.5rem', color: 'var(--signal-up)' }}>{pred ? `₹${pred.target_price?.toFixed(2)}` : '-'}</td>
                      <td style={{ padding: '1rem 0.5rem', color: 'var(--signal-down)' }}>{pred ? `₹${pred.stop_loss?.toFixed(2)}` : '-'}</td>
                    </>
                  )}
                  <td style={{ padding: '1rem 0.5rem', textAlign: 'right' }}>
                    <button onClick={() => handleOpenModal('edit', holding)} style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', marginRight: '0.5rem' }} title="Edit">
                      <Edit2 size={16} />
                    </button>
                    <button onClick={() => handleDelete(holding.symbol)} style={{ background: 'transparent', border: 'none', color: 'var(--signal-down)', cursor: 'pointer' }} title="Delete">
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              )})}
            </tbody>
          </table>
        </div>
      </GlassCard>

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

      {detailsModal.isOpen && detailsModal.data && createPortal(
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0, 0, 0, 0.7)', backdropFilter: 'blur(4px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999, padding: '1rem'
        }}>
          <div style={{ width: '100%', maxWidth: '600px', position: 'relative', maxHeight: '90vh', overflowY: 'auto' }}>
            <GlassCard title={`AI Reasoning: ${detailsModal.data.symbol}`}>
              <button onClick={() => setDetailsModal({ isOpen: false, data: null })} style={{ position: 'absolute', top: '1.5rem', right: '1.5rem', background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
              <div style={{ marginTop: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                  <span style={{
                    padding: '0.4rem 0.8rem', borderRadius: '4px', fontSize: '1rem', fontWeight: 'bold',
                    background: detailsModal.data.action === 'BUY' ? 'rgba(63, 185, 80, 0.2)' : detailsModal.data.action === 'SELL' ? 'rgba(248, 81, 73, 0.2)' : 'rgba(139, 148, 158, 0.2)',
                    color: detailsModal.data.action === 'BUY' ? 'var(--signal-up)' : detailsModal.data.action === 'SELL' ? 'var(--signal-down)' : 'var(--text-secondary)'
                  }}>
                    {detailsModal.data.action} ({Math.round(detailsModal.data.confidence_score)}% Conviction)
                  </span>
                  <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                    Risk Level: <strong style={{ color: '#fff' }}>{detailsModal.data.risk_score}</strong>
                  </span>
                </div>

                <h4 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-primary)' }}>Why? (Key Reasons)</h4>
                <ul style={{ paddingLeft: '1.2rem', marginBottom: '1.5rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                  {detailsModal.data.reasons && detailsModal.data.reasons.length > 0 ? (
                    detailsModal.data.reasons.map((reason, i) => <li key={i}>{reason}</li>)
                  ) : (
                    <li>No specific reasons provided by the engine.</li>
                  )}
                </ul>

                <div style={{ background: 'var(--bg-surface-elevated)', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', borderLeft: `4px solid ${detailsModal.data.action === 'BUY' ? 'var(--signal-up)' : detailsModal.data.action === 'SELL' ? 'var(--signal-down)' : '#8b949e'}` }}>
                  <h4 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-primary)' }}>AI Conclusion</h4>
                  <p style={{ margin: 0, color: 'var(--text-secondary)', lineHeight: '1.5', fontSize: '0.95rem' }}>
                    {generateConclusion(detailsModal.data)}
                  </p>
                </div>

                <h4 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-primary)' }}>Sentiment</h4>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
                  {detailsModal.data.sentiment_summary || 'N/A (No news data)'}
                </p>

                <h4 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-primary)' }}>Technical Metrics Snapshot</h4>
                {detailsModal.data.supporting_indicators ? (
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                    <div><strong>RSI (14):</strong> {detailsModal.data.supporting_indicators.rsi?.toFixed(2)}</div>
                    <div><strong>MACD Hist:</strong> {detailsModal.data.supporting_indicators.macd_histogram?.toFixed(2)}</div>
                    <div><strong>SMA 20:</strong> ₹{detailsModal.data.supporting_indicators.sma_20?.toFixed(2)}</div>
                    <div><strong>SMA 50:</strong> ₹{detailsModal.data.supporting_indicators.sma_50?.toFixed(2)}</div>
                    <div><strong>SMA 200:</strong> ₹{detailsModal.data.supporting_indicators.sma_200?.toFixed(2)}</div>
                    <div><strong>Vol Ratio:</strong> {detailsModal.data.supporting_indicators.volume_ratio?.toFixed(2)}x</div>
                    <div><strong>Target:</strong> ₹{detailsModal.data.suggested_target?.toFixed(2)}</div>
                    <div><strong>Stop Loss:</strong> ₹{detailsModal.data.suggested_stop_loss?.toFixed(2)}</div>
                  </div>
                ) : (
                  <p style={{ color: 'var(--text-secondary)' }}>No technical metrics available.</p>
                )}
              </div>
            </GlassCard>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
}
