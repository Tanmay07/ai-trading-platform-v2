import React, { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { createChart, CandlestickSeries } from 'lightweight-charts';
import GlassCard from '../components/GlassCard';
import { getMarketHistory, getSentiment, getPrediction } from '../services/api';
import { Search } from 'lucide-react';

export default function MarketView() {
  const { symbol } = useParams();
  const navigate = useNavigate();
  
  const [searchInput, setSearchInput] = useState('');
  const [loading, setLoading] = useState(true);
  
  // Data states
  const [history, setHistory] = useState(null);
  const [sentiment, setSentiment] = useState(null);
  const [prediction, setPrediction] = useState(null);

  const chartContainerRef = useRef();
  const chartRef = useRef();

  // Fetch data
  useEffect(() => {
    if (!symbol) return;
    setLoading(true);

    Promise.all([
      getMarketHistory(symbol).catch(() => null),
      getSentiment(symbol).catch(() => null),
      getPrediction(symbol).catch(() => null)
    ]).then(([hist, sent, pred]) => {
      setHistory(hist);
      setSentiment(sent);
      setPrediction(pred);
      setLoading(false);
    });
  }, [symbol]);

  // Render Chart
  useEffect(() => {
    if (!history || !history.data || !chartContainerRef.current) return;

    const candleData = history.data.reduce((acc, row) => {
      if (!row.Date) return acc;
      const time = row.Date.split('T')[0];
      if (!acc.length || acc[acc.length - 1].time !== time) {
        acc.push({
          time,
          open: row.Open,
          high: row.High,
          low: row.Low,
          close: row.Close
        });
      }
      return acc;
    }, []);

    if (!chartRef.current) {
      chartRef.current = createChart(chartContainerRef.current, {
        layout: {
          background: { type: 'solid', color: 'transparent' },
          textColor: '#8b949e',
        },
        grid: {
          vertLines: { color: 'rgba(255, 255, 255, 0.05)' },
          horzLines: { color: 'rgba(255, 255, 255, 0.05)' },
        },
        width: chartContainerRef.current.clientWidth,
        height: 400,
      });

      const candlestickSeriesInstance = chartRef.current.addSeries(CandlestickSeries, {
        upColor: '#3fb950',
        downColor: '#f85149',
        borderVisible: false,
        wickUpColor: '#3fb950',
        wickDownColor: '#f85149',
      });
      candlestickSeriesInstance.setData(candleData);
    } else {
      // If chart exists, just update data (assuming we added simple update logic)
      // For simplicity, we can recreate or just set data on the existing series.
    }

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [history]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchInput.trim()) {
      navigate(`/market/${searchInput.trim().toUpperCase()}`);
    }
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '2rem', margin: '0 0 0.5rem 0' }}>{symbol || 'Market View'}</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Detailed analysis and predictions</p>
        </div>
        
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '0.5rem' }}>
          <div style={{ position: 'relative' }}>
            <Search size={18} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
            <input 
              type="text" 
              placeholder="Search symbol (e.g. TCS.NS)" 
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              style={{ paddingLeft: '2.2rem', width: '250px' }}
            />
          </div>
          <button type="submit" className="btn btn-primary">Analyze</button>
        </form>
      </header>

      {loading ? (
        <div style={{ padding: '2rem' }}>Loading market data...</div>
      ) : (
        <>
          <GlassCard title="Price Chart">
            <div ref={chartContainerRef} style={{ width: '100%', height: '400px' }} />
          </GlassCard>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
            <GlassCard title="AI Prediction (Ensemble)">
              {prediction && prediction.prediction ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Direction:</span>
                    <span style={{ 
                      fontWeight: 'bold', 
                      color: prediction.prediction.direction === 'UP' ? 'var(--signal-up)' : prediction.prediction.direction === 'DOWN' ? 'var(--signal-down)' : 'var(--signal-neutral)',
                      background: prediction.prediction.direction === 'UP' ? 'var(--signal-up-bg)' : prediction.prediction.direction === 'DOWN' ? 'var(--signal-down-bg)' : 'var(--signal-neutral-bg)',
                      padding: '0.2rem 0.6rem',
                      borderRadius: '4px'
                    }}>
                      {prediction.prediction.direction}
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Confidence:</span>
                    <span>{(prediction.prediction.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Probability:</span>
                    <span>{(prediction.prediction.probability * 100).toFixed(1)}%</span>
                  </div>
                  <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--glass-border)' }}>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>Class Probabilities</p>
                    {Object.entries(prediction.prediction.probabilities || {}).map(([key, val]) => (
                      <div key={key} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.25rem' }}>
                        <span>{key}</span>
                        <span>{(val * 100).toFixed(1)}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <p style={{ color: 'var(--text-secondary)' }}>Prediction not available. Model might not be trained.</p>
              )}
            </GlassCard>

            <GlassCard title="News Sentiment">
              {sentiment && sentiment.success ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Overall Score:</span>
                    <span style={{ 
                      fontWeight: 'bold',
                      color: sentiment.sentiment_score > 0 ? 'var(--signal-up)' : sentiment.sentiment_score < 0 ? 'var(--signal-down)' : 'var(--signal-neutral)'
                    }}>
                      {sentiment.sentiment_score > 0 ? '+' : ''}{sentiment.sentiment_score.toFixed(2)}
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Articles Analyzed:</span>
                    <span>{sentiment.article_count}</span>
                  </div>
                  
                  <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--glass-border)', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Recent Headlines</p>
                    {sentiment.articles?.slice(0, 3).map((article, idx) => (
                      <a key={idx} href={article.url} target="_blank" rel="noreferrer" style={{ textDecoration: 'none', color: 'inherit' }}>
                        <div style={{ padding: '0.75rem', background: 'var(--bg-surface-elevated)', borderRadius: 'var(--border-radius-sm)', transition: 'background 0.2s', ':hover': { background: 'var(--glass-highlight)' } }}>
                          <p style={{ fontSize: '0.85rem', margin: '0 0 0.4rem 0', fontWeight: '500' }}>{article.title}</p>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                            <span>{new Date(article.published_at * 1000).toLocaleDateString()}</span>
                            <span style={{ color: article.compound_score > 0 ? 'var(--signal-up)' : article.compound_score < 0 ? 'var(--signal-down)' : 'var(--signal-neutral)' }}>
                              Score: {article.compound_score.toFixed(2)}
                            </span>
                          </div>
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              ) : (
                <p style={{ color: 'var(--text-secondary)' }}>Sentiment data not available.</p>
              )}
            </GlassCard>
          </div>
        </>
      )}
    </div>
  );
}
