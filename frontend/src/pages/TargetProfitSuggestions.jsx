import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getTargetProfitSuggestions, createPaperPortfolio } from '../services/api';
import { Target, TrendingUp, ShieldAlert, Zap, BookOpen, Layers, Play } from 'lucide-react';

const TargetProfitSuggestions = () => {
  const [target, setTarget] = useState(5000);
  const [maxCapital, setMaxCapital] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isPaperTesting, setIsPaperTesting] = useState(false);
  const navigate = useNavigate();

  const fetchSuggestions = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getTargetProfitSuggestions(target, maxCapital || null);
      setSuggestions(data.data || []);
    } catch (err) {
      setError(err.message || 'Failed to fetch suggestions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSuggestions();
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    fetchSuggestions();
  };

  const handlePaperTest = async (bundle) => {
    try {
      setIsPaperTesting(true);
      await createPaperPortfolio(bundle);
      navigate('/paper-trading');
    } catch (err) {
      alert("Failed to start paper testing: " + err.message);
    } finally {
      setIsPaperTesting(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', padding: '2rem', color: '#fff' }}>
      {/* Header & Controls */}
      <div style={{ marginBottom: '2.5rem', borderBottom: '1px solid var(--surface-border)', paddingBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.875rem', fontWeight: 'bold', display: 'flex', alignItems: 'center', marginBottom: '0.5rem' }}>
          <Target style={{ color: 'var(--primary)', marginRight: '0.75rem' }} size={32} />
          Weekly Target Plans
        </h1>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>Algorithmically selected trades to hit your exact monetary goals.</p>
        
        <form onSubmit={handleSubmit} style={{ display: 'flex', alignItems: 'flex-end', gap: '1.5rem', background: 'var(--surface-color)', padding: '1.5rem', borderRadius: '12px', border: '1px solid var(--surface-border)' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '600', color: '#cbd5e1', marginBottom: '0.5rem' }}>I want to earn (₹)</label>
            <input 
              type="number" 
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              style={{ background: 'rgba(0,0,0,0.2)', border: '1px solid var(--surface-border)', color: '#fff', borderRadius: '4px', padding: '0.5rem 1rem', fontSize: '1.25rem', fontWeight: 'bold', width: '12rem', outline: 'none' }}
            />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '600', color: '#cbd5e1', marginBottom: '0.5rem' }}>Max Capital Available (₹) Optional</label>
            <input 
              type="number" 
              value={maxCapital}
              onChange={(e) => setMaxCapital(e.target.value)}
              placeholder="No limit"
              style={{ background: 'rgba(0,0,0,0.2)', border: '1px solid var(--surface-border)', color: '#fff', borderRadius: '4px', padding: '0.5rem 1rem', fontSize: '1.25rem', width: '16rem', outline: 'none' }}
            />
          </div>
          <button 
            type="submit" 
            style={{ background: '#3b82f6', color: '#ffffff', fontWeight: 'bold', padding: '0.5rem 2rem', borderRadius: '8px', height: '46px', border: 'none', cursor: 'pointer', transition: 'background 0.2s' }}
            onMouseOver={(e) => e.target.style.background = '#2563eb'}
            onMouseOut={(e) => e.target.style.background = '#3b82f6'}
          >
            Calculate Plans
          </button>
        </form>
      </div>

      {/* Results */}
      {loading ? (
        <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '5rem 0' }}>Crunching numbers and analyzing models...</div>
      ) : error ? (
        <div style={{ textAlign: 'center', color: '#ef4444', padding: '5rem 0' }}>{error}</div>
      ) : suggestions.length === 0 ? (
        <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '5rem 0' }}>No trades found matching your capital constraints or there are no positive forecasts today.</div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '2rem' }}>
          {suggestions.map((bundle, idx) => (
            <div key={bundle.bundle_id} style={{ background: 'var(--surface-color)', borderRadius: '12px', border: '1px solid var(--surface-border)', overflow: 'hidden', display: 'flex', flexDirection: 'column', position: 'relative' }}>
              {idx === 0 && <div style={{ position: 'absolute', top: 0, right: 0, background: 'var(--primary)', color: '#000', fontSize: '0.75rem', fontWeight: 'bold', padding: '0.25rem 0.75rem', borderBottomLeftRadius: '8px' }}>TOP PORTFOLIO</div>}
              
              {/* Bundle Header */}
              <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--surface-border)', background: 'rgba(255,255,255,0.02)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: 0, display: 'flex', alignItems: 'center' }}>
                    <Layers size={24} style={{ marginRight: '0.75rem', color: 'var(--primary)' }} />
                    Portfolio Option {idx + 1}
                  </h2>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', margin: '0.25rem 0 0 0' }}>
                    <span style={{ color: '#60a5fa', fontWeight: '600' }}>+{bundle.combined_growth_forecast}% Expected Growth</span> • {bundle.combined_confidence}% AI Confidence
                  </p>
                </div>
                <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem' }}>
                  <div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Expected Profit</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#34d399' }}>₹{bundle.expected_total_profit.toLocaleString('en-IN')}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Capital Required: ₹{bundle.total_capital_required.toLocaleString('en-IN')}</div>
                  </div>
                  <button 
                    onClick={() => handlePaperTest(bundle)}
                    disabled={isPaperTesting}
                    style={{ 
                      background: 'rgba(52, 211, 153, 0.1)', 
                      color: '#34d399', 
                      border: '1px solid #34d399', 
                      borderRadius: '4px', 
                      padding: '0.5rem 1rem', 
                      fontSize: '0.875rem', 
                      fontWeight: 'bold', 
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}
                  >
                    <Play size={16} />
                    {isPaperTesting ? 'Starting...' : 'Paper Test Option'}
                  </button>
                </div>
              </div>

              {/* Stocks Grid */}
              <div style={{ padding: '1.5rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '1.5rem' }}>
                {bundle.stocks.map((s) => (
                  <div key={s.symbol} style={{ background: 'rgba(0,0,0,0.2)', borderRadius: '8px', border: '1px solid var(--surface-border)', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--surface-border)', paddingBottom: '0.75rem' }}>
                      <div>
                        <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', margin: 0 }}>{s.symbol.replace('.NS', '')}</h3>
                        <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', margin: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '200px' }}>{s.company_name}</p>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Buy Quantity</div>
                        <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#60a5fa' }}>{s.target_plan.quantity} Shares</div>
                      </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.875rem' }}>
                      <div style={{ color: 'var(--text-secondary)' }}>Entry Price:</div>
                      <div style={{ fontWeight: 'bold', textAlign: 'right' }}>₹{s.trade_setup.sugg_entry}</div>
                      
                      <div style={{ color: 'var(--text-secondary)' }}>Target Exit:</div>
                      <div style={{ fontWeight: 'bold', textAlign: 'right', color: '#34d399' }}>₹{s.trade_setup.exit_price}</div>
                      
                      <div style={{ color: 'var(--text-secondary)' }}>Stop Loss:</div>
                      <div style={{ fontWeight: 'bold', textAlign: 'right', color: '#f87171' }}>₹{s.trade_setup.stop_loss}</div>

                      <div style={{ color: 'var(--text-secondary)' }}>Capital Needed:</div>
                      <div style={{ fontWeight: 'bold', textAlign: 'right' }}>₹{s.target_plan.capital_required.toLocaleString('en-IN')}</div>
                      
                      <div style={{ color: 'var(--text-secondary)' }}>Expected Profit:</div>
                      <div style={{ fontWeight: 'bold', textAlign: 'right', color: '#34d399' }}>₹{s.target_plan.expected_total_profit.toLocaleString('en-IN')}</div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--surface-border)' }}>
                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '0.25rem', display: 'flex', alignItems: 'center' }}><BookOpen size={12} style={{ marginRight: '0.25rem' }}/> Fundamentals</div>
                        <div style={{ fontSize: '0.75rem' }}>ROE: <span style={{ color: '#4ade80' }}>{s.fundamentals.roe}%</span></div>
                      </div>
                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '0.25rem', display: 'flex', alignItems: 'center' }}><Zap size={12} style={{ marginRight: '0.25rem' }}/> ML Forecast</div>
                        <div style={{ fontSize: '0.75rem', color: '#34d399', fontWeight: '600' }}>{s.ml_analysis['3_day_forecast']} expected</div>
                      </div>
                    </div>

                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TargetProfitSuggestions;
