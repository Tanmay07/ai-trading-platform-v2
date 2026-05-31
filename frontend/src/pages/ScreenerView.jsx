import React, { useEffect, useState, useRef } from 'react';
import { getSectors, trainBatch, refreshSectors } from '../services/api';
import GlassCard from '../components/GlassCard';
import { Layers, Zap, TrendingUp, AlertCircle, Loader, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function ScreenerView() {
  const [sectors, setSectors] = useState({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [selectedSector, setSelectedSector] = useState(null);
  const [nIter, setNIter] = useState(10);
  
  const [trainingState, setTrainingState] = useState({ loading: false, done: false, result: null, error: null });

  const fetchSectors = async () => {
    try {
      const res = await getSectors();
      if (res.sectors) {
        setSectors(res.sectors);
        const keys = Object.keys(res.sectors);
        if (keys.length > 0 && !selectedSector) setSelectedSector(keys[0]);
      }
    } catch (err) {
      setError("Failed to fetch sectors");
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchSectors().finally(() => setLoading(false));
  }, []);

  const handleTrain = async () => {
    if (!selectedSector) return;
    const symbols = sectors[selectedSector].map(s => s.symbol);
    setTrainingState({ loading: true, done: false, result: null, error: null });
    
    try {
      const res = await trainBatch(symbols, "5y", nIter);
      setTrainingState({ loading: false, done: true, result: res, error: null });
    } catch (err) {
      setTrainingState({ loading: false, done: false, result: null, error: err.message || "Training failed" });
    }
  };



  const handleRefreshUniverse = async () => {
    try {
      setRefreshing(true);
      setError(null);
      await refreshSectors();
      await fetchSectors();
    } catch (err) {
      setError('Failed to refresh universe: ' + err.message);
    } finally {
      setRefreshing(false);
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
            
            <div style={{ marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.9rem', fontWeight: '500' }}>Tuning Iterations (Hyperparameters)</span>
                <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>{nIter === 0 ? 'Fast (No Tuning)' : `${nIter} Iters (Deep)`}</span>
              </div>
              <input 
                type="range" 
                min="0" max="20" step="5" 
                value={nIter} 
                onChange={(e) => setNIter(parseInt(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--accent-primary)' }}
              />
            </div>

            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                onClick={handleRefreshUniverse}
                disabled={refreshing}
                className="btn"
                style={{ flex: 1, display: 'flex', justifyContent: 'center', gap: '0.5rem', background: 'var(--bg-surface-elevated)', border: '1px solid var(--glass-border)', color: '#fff' }}
              >
                <RefreshCw size={18} className={refreshing ? 'animate-spin' : ''} />
                {refreshing ? 'Refreshing...' : 'Refresh'}
              </button>
              <button 
                className="btn btn-primary" 
                onClick={handleTrain} 
                disabled={trainingState.loading}
                style={{ flex: 2, display: 'flex', justifyContent: 'center', gap: '0.5rem' }}
              >
                {trainingState.loading ? <><Loader size={18} className="animate-spin" /> Training...</> : <><Zap size={18} /> Train Models</>}
              </button>
            </div>
            
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
                
                {trainingState.result.results && trainingState.result.results.length > 0 && (
                  <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--glass-border)' }}>
                    <h5 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-primary)' }}>Best Hyperparameters</h5>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '200px', overflowY: 'auto' }}>
                      {trainingState.result.results.map((r, i) => r.success && (
                        <div key={i} style={{ fontSize: '0.8rem', background: 'var(--glass-bg)', padding: '0.5rem', borderRadius: '4px' }}>
                          <span style={{ fontWeight: 'bold', color: 'var(--accent-secondary)' }}>{r.symbol} ({r.model_name})</span>
                          {r.best_params && (
                            <pre style={{ margin: '0.2rem 0 0 0', overflowX: 'auto', color: 'var(--text-secondary)' }}>
                              {JSON.stringify(r.best_params, null, 2)}
                            </pre>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </GlassCard>
        </div>
      </div>
    </div>
  );
}
