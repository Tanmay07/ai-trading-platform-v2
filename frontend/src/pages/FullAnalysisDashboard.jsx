import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

const FullAnalysisDashboard = () => {
  const { symbol } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchInput, setSearchInput] = useState('');

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        setLoading(true);
        // Assuming your backend runs on localhost:8000 and uses the new route
        const response = await api.get(`/suggestions/${symbol}/analysis`);
        setData(response.data.data);
      } catch (err) {
        setError(err.message || 'Failed to fetch analysis data');
      } finally {
        setLoading(false);
      }
    };

    if (symbol) {
      fetchAnalysis();
    }
  }, [symbol]);

  if (loading) {
    return <div className="p-8 text-center text-gray-400">Loading analysis for {symbol}...</div>;
  }

  if (error || !data) {
    return <div className="p-8 text-center text-red-500">Error: {error}</div>;
  }

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchInput.trim()) {
      let searchSymbol = searchInput.trim().toUpperCase();
      if (!searchSymbol.endsWith('.NS')) {
        searchSymbol += '.NS';
      }
      navigate(`/analysis/${searchSymbol}`);
      setSearchInput('');
    }
  };

  // Format helpers
  const { trade_setup, ml_analysis, fundamentals, sentiment, ai_reasoning, company_name, live_price } = data;

  return (
    <div style={{ minHeight: '100vh', padding: '2rem', color: '#fff' }}>
      {/* Header section with Search */}
      <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '1px solid var(--surface-border)' }}>
        <h1 style={{ fontSize: '2rem', margin: 0 }}>{symbol.replace('.NS', '')}</h1>
        <span style={{ fontSize: '1.25rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>{company_name}</span>
        
        <form onSubmit={handleSearch} style={{ display: 'flex', marginLeft: 'auto', gap: '0.5rem' }}>
          <input 
            type="text" 
            placeholder="Search NSE Universe (e.g. INFY)" 
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '8px',
              border: '1px solid rgba(59, 130, 246, 0.5)',
              background: 'rgba(0, 0, 0, 0.3)',
              color: '#fff',
              outline: 'none',
              minWidth: '250px'
            }}
          />
          <button type="submit" style={{
            background: 'var(--accent)',
            color: '#fff',
            border: 'none',
            padding: '0.5rem 1rem',
            borderRadius: '8px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}>Search</button>
        </form>
        <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginLeft: '1rem' }}>Updated: {data.updated_at?.split('T')[0] || 'Live'}</span>
      </div>

      {/* Sentiments */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        <div className="glass-panel" style={{ padding: '1rem', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center' }}><span style={{ marginRight: '0.25rem' }}>📰</span> News Sentiment</div>
          <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--success)', display: 'flex', alignItems: 'center' }}>
            <span style={{ width: '0.75rem', height: '0.75rem', backgroundColor: 'var(--success)', borderRadius: '50%', marginRight: '0.5rem' }}></span>
            {sentiment?.news_sentiment || 'Bullish'}
          </div>
        </div>
        <div className="glass-panel" style={{ padding: '1rem', border: '1px solid rgba(245, 158, 11, 0.3)' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center' }}><span style={{ marginRight: '0.25rem' }}>📊</span> Market Sentiment</div>
          <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--warning)' }}>{sentiment?.market_sentiment || 'Neutral Market'}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Score: {sentiment?.score || '50/100'}</div>
        </div>
      </div>

      {/* Trade Setup */}
      <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '1rem', textAlign: 'center', marginBottom: '1.5rem' }}>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Sugg. Entry</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>₹{trade_setup?.sugg_entry || live_price}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Live Price</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--success)' }}>₹{live_price}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Exit Price</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--success)' }}>₹{trade_setup?.exit_price || '-'}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Stop Loss</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--danger)' }}>₹{trade_setup?.stop_loss || '-'}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>R:R</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--accent)' }}>{trade_setup?.rr_ratio || '-'}</div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '8px' }}>
          <button style={{ background: 'var(--success)', color: '#fff', border: 'none', padding: '0.75rem 1.5rem', borderRadius: '4px', fontWeight: 'bold', marginRight: '1rem', display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
            <span style={{ marginRight: '0.5rem' }}>☑</span> BUY / ENTER
          </button>
          <div style={{ fontSize: '0.875rem' }}>
            <p style={{ margin: 0, fontWeight: 'bold' }}>Solid technical setup with healthy fundamentals</p>
            <p style={{ margin: 0, color: 'var(--success)', marginTop: '0.25rem', fontSize: '0.75rem' }}>☛ ACTION: Standard entry recommended. SL at ₹{trade_setup?.stop_loss}.</p>
          </div>
        </div>
      </div>

      {/* AI Trend Reasoning */}
      <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '1.5rem', border: '1px solid rgba(59, 130, 246, 0.3)', background: 'rgba(59, 130, 246, 0.05)' }}>
        <h3 style={{ color: 'var(--accent)', margin: '0 0 0.5rem 0', display: 'flex', alignItems: 'center' }}>
          <span style={{ marginRight: '0.5rem' }}>💡</span> AI Trend Reasoning
        </h3>
        <p style={{ margin: 0, fontSize: '0.875rem', lineHeight: '1.6' }}>
          {ai_reasoning || "AI model predicts a probability of an upward trend based on technical indicators and market momentum."}
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        {/* ML Analysis */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ margin: '0 0 1rem 0', display: 'flex', alignItems: 'center' }}>
            <span style={{ marginRight: '0.5rem' }}>🤖</span> Deep ML Analysis (scikit-learn)
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>3-Day Forecast</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--success)' }}>{ml_analysis?.['3_day_forecast'] || '+0.0%'}</div>
              <div style={{ fontSize: '0.625rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Price move predicted by Gradient Boosting</div>
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Signal Strength</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>{ml_analysis?.signal_strength || '0%'}</div>
              <div style={{ fontSize: '0.625rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Anomaly detection breakout conviction</div>
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Model Confidence</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>{ml_analysis?.model_confidence || '0%'}</div>
              <div style={{ fontSize: '0.625rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>R² accuracy on historical data</div>
            </div>
          </div>
        </div>

        {/* Fundamentals */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ margin: '0 0 1rem 0', display: 'flex', alignItems: 'center' }}>
            <span style={{ marginRight: '0.5rem' }}>📊</span> Fundamentals
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem 2rem', fontSize: '0.875rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--surface-border)', paddingBottom: '0.25rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>EPS (TTM)</span>
              <span style={{ fontWeight: 'bold' }}>{fundamentals?.eps || '-'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--surface-border)', paddingBottom: '0.25rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>P/E Ratio</span>
              <span style={{ fontWeight: 'bold', color: 'var(--warning)' }}>{fundamentals?.pe_ratio || '-'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--surface-border)', paddingBottom: '0.25rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>P/B Ratio</span>
              <span style={{ fontWeight: 'bold' }}>{fundamentals?.pb_ratio || '-'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--surface-border)', paddingBottom: '0.25rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Debt/Equity</span>
              <span style={{ fontWeight: 'bold', color: 'var(--success)' }}>{fundamentals?.debt_equity || '-'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--surface-border)', paddingBottom: '0.25rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>ROE (%)</span>
              <span style={{ fontWeight: 'bold' }}>{fundamentals?.roe || '-'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--surface-border)', paddingBottom: '0.25rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Free Cash Flow</span>
              <span style={{ fontWeight: 'bold' }}>{fundamentals?.free_cash_flow || '-'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FullAnalysisDashboard;
