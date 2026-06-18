import React, { useState, useEffect } from 'react';
import { getTargetProfitSuggestions } from '../services/api';
import { Target, TrendingUp, ShieldAlert, Zap, BookOpen } from 'lucide-react';

const TargetProfitSuggestions = () => {
  const [target, setTarget] = useState(5000);
  const [maxCapital, setMaxCapital] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
            style={{ background: 'var(--primary)', color: '#000', fontWeight: 'bold', padding: '0.5rem 2rem', borderRadius: '4px', height: '46px', border: 'none', cursor: 'pointer' }}
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
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          {suggestions.map((s, idx) => (
            <div key={s.symbol} style={{ background: 'var(--surface-color)', borderRadius: '12px', border: '1px solid var(--surface-border)', overflow: 'hidden', display: 'flex', flexDirection: 'column', position: 'relative' }}>
              {idx === 0 && <div style={{ position: 'absolute', top: 0, right: 0, background: 'var(--primary)', color: '#000', fontSize: '0.75rem', fontWeight: 'bold', padding: '0.25rem 0.75rem', borderBottomLeftRadius: '8px' }}>TOP PICK</div>}
              
              <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--surface-border)', background: 'rgba(255,255,255,0.02)' }}>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: 0 }}>{s.symbol.replace('.NS', '')}</h2>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', margin: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{s.company_name}</p>
              </div>

              <div style={{ padding: '1.5rem', flexGrow: 1, display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                {/* The Plan */}
                <div style={{ background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)', padding: '1rem', borderRadius: '8px' }}>
                  <h3 style={{ fontWeight: '600', color: '#93c5fd', display: 'flex', alignItems: 'center', marginBottom: '0.75rem', fontSize: '1rem', marginTop: 0 }}>
                    <Zap size={16} style={{ marginRight: '0.5rem' }} /> The Action Plan
                  </h3>
                  <div style={{ fontSize: '1.125rem' }}>
                    Buy <span style={{ fontWeight: 'bold', color: '#fff' }}>{s.target_plan.quantity}</span> shares at <span style={{ fontWeight: 'bold', color: '#fff' }}>₹{s.trade_setup.sugg_entry}</span>
                  </div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                    Requires <span style={{ color: '#fff', fontWeight: '500' }}>₹{s.target_plan.capital_required.toLocaleString('en-IN')}</span> capital
                  </div>
                </div>

                <div style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '1rem', borderRadius: '8px' }}>
                  <h3 style={{ fontWeight: '600', color: '#34d399', display: 'flex', alignItems: 'center', marginBottom: '0.75rem', fontSize: '1rem', marginTop: 0 }}>
                    <TrendingUp size={16} style={{ marginRight: '0.5rem' }} /> The Exit Strategy
                  </h3>
                  <div style={{ fontSize: '1.125rem' }}>
                    Sell at <span style={{ fontWeight: 'bold', color: '#6ee7b7' }}>₹{s.trade_setup.exit_price}</span> to make <span style={{ fontWeight: 'bold', color: '#6ee7b7' }}>₹{s.target_plan.expected_total_profit.toLocaleString('en-IN')}</span> profit
                  </div>
                </div>

                <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', padding: '0.75rem', borderRadius: '8px', display: 'flex', alignItems: 'center' }}>
                  <ShieldAlert size={16} style={{ color: '#f87171', marginRight: '0.5rem' }} />
                  <span style={{ color: '#fca5a5', fontSize: '0.875rem' }}>Stop Loss: <strong>₹{s.trade_setup.stop_loss}</strong> (Risking ~₹{((s.trade_setup.sugg_entry - s.trade_setup.stop_loss) * s.target_plan.quantity).toLocaleString('en-IN')})</span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--surface-border)' }}>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '0.25rem', display: 'flex', alignItems: 'center' }}><BookOpen size={12} style={{ marginRight: '0.25rem' }}/> Fundamentals</div>
                    <div style={{ fontSize: '0.875rem' }}>ROE: <span style={{ color: '#4ade80' }}>{s.fundamentals.roe}%</span></div>
                    <div style={{ fontSize: '0.875rem' }}>EPS: <span style={{ color: '#fff' }}>{s.fundamentals.eps}</span></div>
                  </div>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '0.25rem', display: 'flex', alignItems: 'center' }}><Zap size={12} style={{ marginRight: '0.25rem' }}/> ML Forecast</div>
                    <div style={{ fontSize: '0.875rem', color: '#34d399', fontWeight: '600' }}>{s.ml_analysis['3_day_forecast']} expected</div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TargetProfitSuggestions;
