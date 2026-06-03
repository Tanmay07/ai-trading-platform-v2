import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Activity, LayoutDashboard, History, Layers, Compass } from 'lucide-react';
import './index.css';

// Layout Component
function Sidebar() {
  const location = useLocation();
  const navItems = [
    { path: '/', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
    { path: '/discovery', label: 'AI Discovery', icon: <Compass size={20} /> },
    { path: '/screener', label: 'Sector Screener', icon: <Layers size={20} /> },
    { path: '/market/RELIANCE.NS', label: 'Market View', icon: <Activity size={20} /> },
    { path: '/backtest', label: 'Backtesting', icon: <History size={20} /> },
  ];

  return (
    <div style={{
      width: '260px',
      borderRight: '1px solid var(--glass-border)',
      background: 'var(--bg-surface)',
      padding: '2rem 1rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '2rem'
    }}>
      <div style={{ padding: '0 1rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{ 
          width: '32px', height: '32px', 
          borderRadius: '8px', 
          background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-hover))',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: '#fff', fontWeight: 'bold'
        }}>
          AI
        </div>
        <h2 style={{ fontSize: '1.2rem', fontWeight: '600', margin: 0 }}>Trading Pro</h2>
      </div>

      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path || 
                           (item.path.startsWith('/market') && location.pathname.startsWith('/market'));
          return (
            <Link 
              key={item.path} 
              to={item.path}
              style={{
                display: 'flex', alignItems: 'center', gap: '0.75rem',
                padding: '0.75rem 1rem',
                borderRadius: 'var(--border-radius-sm)',
                textDecoration: 'none',
                color: isActive ? '#fff' : 'var(--text-secondary)',
                background: isActive ? 'var(--glass-highlight)' : 'transparent',
                borderLeft: isActive ? '3px solid var(--accent-primary)' : '3px solid transparent',
                transition: 'all 0.2s ease',
                fontWeight: isActive ? '500' : '400'
              }}
            >
              {item.icon}
              {item.label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}

// Pages Placeholders
import Dashboard from './pages/Dashboard';
import MarketView from './pages/MarketView';
import BacktestView from './pages/BacktestView';
import ScreenerView from './pages/ScreenerView';
import DiscoveryView from './pages/DiscoveryView';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/discovery" element={<DiscoveryView />} />
            <Route path="/screener" element={<ScreenerView />} />
            <Route path="/market/:symbol" element={<MarketView />} />
            <Route path="/backtest" element={<BacktestView />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
