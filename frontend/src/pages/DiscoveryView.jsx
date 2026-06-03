import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  Search, 
  Filter, 
  RefreshCw, 
  Target,
  Zap,
  Briefcase,
  AlertCircle,
  Activity
} from 'lucide-react';
import axios from 'axios';

const DiscoveryView = () => {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all');
  const [isScanning, setIsScanning] = useState(false);

  const fetchOpportunities = async (forceRefresh = false) => {
    try {
      if (forceRefresh) setIsScanning(true);
      
      const response = await axios.get(`http://localhost:8000/discovery/scan${forceRefresh ? '?force_refresh=true' : ''}`);
      
      if (response.data.status === 'scanning') {
        setIsScanning(true);
        // Poll again in 5 seconds
        setTimeout(() => fetchOpportunities(), 5000);
      } else {
        setOpportunities(response.data.data || []);
        setLoading(false);
        setIsScanning(false);
      }
    } catch (error) {
      console.error('Error fetching discovery data:', error);
      setLoading(false);
      setIsScanning(false);
    }
  };

  useEffect(() => {
    fetchOpportunities();
  }, []);

  const filteredOpportunities = opportunities.filter(opp => {
    if (activeTab === 'high_growth') return opp.predicted_return > 5;
    if (activeTab === 'value') return opp.value_score > 70;
    if (activeTab === 'momentum') return opp.momentum_score > 70;
    if (activeTab === 'sentiment') return opp.sentiment_score > 70;
    return true;
  });

  const getRecommendationColor = (rec) => {
    switch (rec) {
      case 'Strong Buy': return 'var(--accent-primary)';
      case 'Buy': return '#10b981';
      case 'Watchlist': return '#f59e0b';
      case 'Hold': return '#6b7280';
      default: return '#ef4444';
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
      <header style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '2rem', margin: '0 0 0.5rem 0', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Target className="text-accent" size={32} />
            AI Opportunity Discovery Engine
          </h1>
          <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
            Continuously scanning the NSE universe to identify high-probability trading opportunities.
          </p>
        </div>
        
        <button 
          onClick={() => fetchOpportunities(true)}
          disabled={isScanning}
          style={{
            display: 'flex', alignItems: 'center', gap: '0.5rem',
            padding: '0.75rem 1.25rem',
            background: 'var(--glass-surface)',
            border: '1px solid var(--glass-border)',
            borderRadius: 'var(--border-radius-sm)',
            color: 'var(--text-primary)',
            cursor: isScanning ? 'not-allowed' : 'pointer',
            opacity: isScanning ? 0.7 : 1,
            transition: 'all 0.2s ease'
          }}
        >
          <RefreshCw size={18} className={isScanning ? 'animate-spin' : ''} />
          {isScanning ? 'Scanning Universe...' : 'Run Full Scan'}
        </button>
      </header>

      {/* Tabs */}
      <div style={{ 
        display: 'flex', gap: '1rem', marginBottom: '2rem', 
        borderBottom: '1px solid var(--glass-border)', paddingBottom: '1rem' 
      }}>
        {[
          { id: 'all', label: 'All Opportunities', icon: <TrendingUp size={18} /> },
          { id: 'high_growth', label: 'High Growth', icon: <Zap size={18} /> },
          { id: 'value', label: 'Value Picks (52W Low)', icon: <Briefcase size={18} /> },
          { id: 'momentum', label: 'Momentum Breakouts', icon: <Activity size={18} /> },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              display: 'flex', alignItems: 'center', gap: '0.5rem',
              padding: '0.5rem 1rem',
              background: activeTab === tab.id ? 'var(--glass-highlight)' : 'transparent',
              border: 'none',
              borderRadius: 'var(--border-radius-sm)',
              color: activeTab === tab.id ? '#fff' : 'var(--text-secondary)',
              cursor: 'pointer',
              fontWeight: activeTab === tab.id ? '500' : '400',
              transition: 'all 0.2s'
            }}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <RefreshCw className="animate-spin" size={48} style={{ margin: '0 auto 1rem', color: 'var(--accent-primary)' }} />
          <h2>Initializing AI Discovery Engine...</h2>
          <p>Analyzing fundamentals, technicals, and sentiment.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '1.5rem', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))' }}>
          {filteredOpportunities.map((opp) => (
            <div key={opp.symbol} style={{
              background: 'var(--glass-surface)',
              border: '1px solid var(--glass-border)',
              borderRadius: 'var(--border-radius-md)',
              padding: '1.5rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '1rem'
            }}>
              {/* Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h3 style={{ margin: '0 0 0.25rem 0', fontSize: '1.25rem', fontWeight: 'bold' }}>{opp.symbol}</h3>
                  <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>{opp.sector}</div>
                </div>
                <div style={{ 
                  padding: '0.25rem 0.75rem', 
                  borderRadius: '100px', 
                  fontSize: '0.85rem', 
                  fontWeight: 'bold',
                  background: `${getRecommendationColor(opp.recommendation)}20`,
                  color: getRecommendationColor(opp.recommendation),
                  border: `1px solid ${getRecommendationColor(opp.recommendation)}50`
                }}>
                  {opp.recommendation}
                </div>
              </div>

              {/* Top Stats */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', padding: '1rem 0', borderTop: '1px solid var(--glass-border)', borderBottom: '1px solid var(--glass-border)' }}>
                <div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Opportunity Score</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--accent-primary)' }}>{opp.opportunity_score}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Exp. Return (30d)</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: opp.predicted_return > 0 ? '#10b981' : '#ef4444' }}>
                    +{opp.predicted_return}%
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>AI Confidence</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{opp.confidence}%</div>
                </div>
              </div>

              {/* Component Scores */}
              <div>
                <div style={{ fontSize: '0.9rem', fontWeight: '500', marginBottom: '0.75rem' }}>Engine Diagnostics</div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Fundamental:</span>
                    <span>{opp.fundamental_score}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Momentum:</span>
                    <span>{opp.momentum_score}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Value:</span>
                    <span>{opp.value_score}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Sentiment:</span>
                    <span>{opp.sentiment_score}</span>
                  </div>
                </div>
              </div>

              {/* Explanations */}
              <div style={{ 
                background: 'rgba(0,0,0,0.2)', 
                padding: '1rem', 
                borderRadius: 'var(--border-radius-sm)',
                fontSize: '0.85rem',
                color: 'var(--text-secondary)',
                lineHeight: '1.5'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
                  <AlertCircle size={14} />
                  <span style={{ fontWeight: '500' }}>Key Drivers</span>
                </div>
                <ul style={{ margin: 0, paddingLeft: '1.25rem' }}>
                  {opp.explanation?.key_drivers.map((reason, i) => (
                    <li key={i}>{reason}</li>
                  ))}
                </ul>
              </div>

            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DiscoveryView;
