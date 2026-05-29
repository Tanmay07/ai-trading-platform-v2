import React, { useEffect, useState } from 'react';
import { getSectors, trainBatch, getStrategy } from '../services/api';
import GlassCard from '../components/GlassCard';
import { Layers, Zap, TrendingUp, AlertCircle, Loader } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function ScreenerView() {
  const [sectors, setSectors] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedSector, setSelectedSector] = useState(null);
  
  const [trainingState, setTrainingState] = useState({ loading: false, done: false, result: null, error: null });
  const [strategyState, setStrategyState] = useState({ loading: false, done: false, predictions: null, error: null });

  useEffect(() => {
    setLoading(true);
    getSectors()
      .then(res => {
        if (res.sectors) {
          setSectors(res.sectors);
          const keys = Object.keys(res.sectors);
          if (keys.length > 0) setSelectedSector(keys[0]);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  const handleTrain = async () => {
    if (!selectedSector) return;
    const symbols = sectors[selectedSector].map(s => s.symbol);
    setTrainingState({ loading: true, done: false, result: null, error: null });
    
    try {
      const res = await trainBatch(symbols, "3y");
      setTrainingState({ loading: false, done: true, result: res, error: null });
    } catch (err) {
      setTrainingState({ loading: false, done: false, result: null, error: err.message || "Training failed" });
    }
  };

  const handleStrategy = async () => {
    if (!selectedSector) return;
    const symbols = sectors[selectedSector].map(s => s.symbol);
    setStrategyState({ loading: true, done: false, predictions: null, error: null });
    
    try {
      const res = await getStrategy(symbols);
      // Sort predictions by confidence
      const sorted = res.predictions.sort((a, b) => b.confidence_score - a.confidence_score);
      setStrategyState({ loading: false, done: true, predictions: sorted, error: null });
    } catch (err) {
      setStrategyState({ loading: false, done: false, predictions: null, error: err.message || "Strategy generation failed" });
    }
  };

  if (loading) {
    return <div style={{ padding: '2rem' }}>Loading sector universe...</div>;
  }

  const selectedStocks = selectedSector ? sectors[selectedSector] : [];

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header>
        <h1 style={{ fontSize: '2rem', margin: '0 0 0.5rem 0' }}>Sector Screener</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Analyze market sectors, train models, and generate strategies.</p>
      </header>

      <div style={{ display: 'flex', gap: '1rem', overflowX: 'auto', paddingBottom: '0.5rem' }}>
        {Object.keys(sectors).map(sector => (
          <button
            key={sector}
            onClick={() => {
              setSelectedSector(sector);
              setTrainingState({ loading: false, done: false, result: null, error: null });
              setStrategyState({ loading: false, done: false, predictions: null, error: null });
            }}
            style={{
              padding: '0.75rem 1.5rem',
              borderRadius: 'var(--border-radius-full)',
              border: '1px solid var(--glass-border)',
              background: selectedSector === sector ? 'var(--accent-primary)' : 'var(--glass-bg)',
              color: selectedSector === sector ? '#fff' : 'var(--text-primary)',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              fontWeight: '500',
              transition: 'all 0.2s'
            }}
          >
            {sector}
          </button>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        <GlassCard title={`${selectedSector} Universe`}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '400px', overflowY: 'auto', paddingRight: '0.5rem' }}>
            {selectedStocks.map((stock, idx) => (
              <div key={idx} style={{ 
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '0.75rem', background: 'var(--bg-surface-elevated)', borderRadius: 'var(--border-radius-sm)'
              }}>
                <div>
                  <Link to={`/market/${stock.symbol}`} style={{ fontWeight: 'bold', color: 'var(--text-primary)', textDecoration: 'none' }}>
                    {stock.symbol}
                  </Link>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontWeight: '500' }}>₹{stock.price ? stock.price.toFixed(2) : 'N/A'}</div>
                  {stock.change_pct !== undefined && (
                    <div style={{ fontSize: '0.85rem', color: stock.change_pct > 0 ? 'var(--signal-up)' : stock.change_pct < 0 ? 'var(--signal-down)' : 'var(--signal-neutral)' }}>
                      {stock.change_pct > 0 ? '+' : ''}{stock.change_pct.toFixed(2)}%
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </GlassCard>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <GlassCard title="ML Model Training">
            <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              Train deep learning models on 3 years of historical data for all stocks in the <strong>{selectedSector}</strong> sector.
            </p>
            <button 
              className="btn btn-primary" 
              onClick={handleTrain} 
              disabled={trainingState.loading}
              style={{ width: '100%', display: 'flex', justifyContent: 'center', gap: '0.5rem' }}
            >
              {trainingState.loading ? <><Loader size={18} className="animate-spin" /> Training Batch...</> : <><Zap size={18} /> Train Models</>}
            </button>
            
            {trainingState.error && (
              <div style={{ marginTop: '1rem', color: 'var(--signal-down)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <AlertCircle size={16} /> {trainingState.error}
              </div>
            )}
            
            {trainingState.done && trainingState.result && (
              <div style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(63, 185, 80, 0.1)', border: '1px solid var(--signal-up)', borderRadius: 'var(--border-radius-sm)' }}>
                <h4 style={{ color: 'var(--signal-up)', margin: '0 0 0.5rem 0' }}>Training Complete</h4>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                  <span>Total Trained:</span>
                  <span style={{ fontWeight: 'bold' }}>{trainingState.result.summary.total}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                  <span>Success Rate:</span>
                  <span style={{ fontWeight: 'bold', color: 'var(--signal-up)' }}>
                    {Math.round((trainingState.result.summary.success / trainingState.result.summary.total) * 100)}%
                  </span>
                </div>
              </div>
            )}
          </GlassCard>

          <GlassCard title="Strategy Generation">
            <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              Run the recommendation engine to generate aggregate BUY/HOLD/SELL signals using AI predictions and rule-based logic.
            </p>
            <button 
              className="btn" 
              onClick={handleStrategy} 
              disabled={strategyState.loading}
              style={{ width: '100%', display: 'flex', justifyContent: 'center', gap: '0.5rem', background: 'var(--bg-surface-elevated)', border: '1px solid var(--glass-border)', color: '#fff' }}
            >
              {strategyState.loading ? <><Loader size={18} className="animate-spin" /> Generating...</> : <><TrendingUp size={18} /> Run Strategy Engine</>}
            </button>
          </GlassCard>
        </div>
      </div>

      {/* Strategy Results */}
      {strategyState.predictions && (
        <GlassCard title="Generated Strategies (Ranked)">
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--glass-border)', color: 'var(--text-secondary)' }}>
                  <th style={{ padding: '1rem' }}>Symbol</th>
                  <th style={{ padding: '1rem' }}>Action</th>
                  <th style={{ padding: '1rem' }}>Confidence</th>
                  <th style={{ padding: '1rem' }}>Risk</th>
                  <th style={{ padding: '1rem' }}>Price</th>
                  <th style={{ padding: '1rem' }}>Target</th>
                  <th style={{ padding: '1rem' }}>Stop Loss</th>
                </tr>
              </thead>
              <tbody>
                {strategyState.predictions.map((rec, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <td style={{ padding: '1rem', fontWeight: 'bold' }}>
                      <Link to={`/market/${rec.symbol}`} style={{ color: 'inherit', textDecoration: 'none' }}>
                        {rec.symbol}
                      </Link>
                    </td>
                    <td style={{ padding: '1rem' }}>
                      <span style={{
                        padding: '0.2rem 0.6rem', borderRadius: '4px', fontSize: '0.85rem', fontWeight: 'bold',
                        color: rec.action === 'BUY' ? 'var(--signal-up)' : rec.action === 'SELL' ? 'var(--signal-down)' : 'var(--signal-neutral)',
                        background: rec.action === 'BUY' ? 'var(--signal-up-bg)' : rec.action === 'SELL' ? 'var(--signal-down-bg)' : 'var(--signal-neutral-bg)',
                      }}>
                        {rec.action}
                      </span>
                    </td>
                    <td style={{ padding: '1rem' }}>{rec.confidence_score}%</td>
                    <td style={{ padding: '1rem' }}>
                      <span style={{ color: rec.risk_score === 'High' ? 'var(--signal-down)' : rec.risk_score === 'Low' ? 'var(--signal-up)' : 'inherit' }}>
                        {rec.risk_score}
                      </span>
                    </td>
                    <td style={{ padding: '1rem' }}>₹{rec.current_price}</td>
                    <td style={{ padding: '1rem', color: 'var(--signal-up)' }}>₹{rec.suggested_target}</td>
                    <td style={{ padding: '1rem', color: 'var(--signal-down)' }}>₹{rec.suggested_stop_loss}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      )}

    </div>
  );
}
