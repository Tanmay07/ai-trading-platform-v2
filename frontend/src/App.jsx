import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Activity, LayoutDashboard, History, Layers, Compass, Target, Brain, LineChart, Cpu, FlaskConical, Gavel, ShieldAlert } from 'lucide-react';
import './index.css';

// Layout Component
function Sidebar() {
  const location = useLocation();
  const mainNavItems = [
    { path: '/', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
    { path: '/discovery', label: 'AI Discovery', icon: <Compass size={20} /> },
    { path: '/target-profit', label: 'Weekly Targets', icon: <Target size={20} /> },
    { path: '/paper-trading', label: 'Paper Trading', icon: <Target size={20} /> },
    { path: '/screener', label: 'Sector Screener', icon: <Layers size={20} /> },
    { path: '/analysis/RELIANCE.NS', label: 'Full Analysis', icon: <Activity size={20} /> },
    { path: '/market/RELIANCE.NS', label: 'Market View', icon: <Activity size={20} /> },
    { path: '/backtest', label: 'Backtesting', icon: <History size={20} /> },
  ];

  const aiNavItems = [
    { path: '/ai/portfolio', label: 'Portfolio Intelligence', icon: <LineChart size={20} /> },
    { path: '/ai/market', label: 'Market Intelligence', icon: <Activity size={20} /> },
    { path: '/ai/decision', label: 'AI Decision Center', icon: <Cpu size={20} /> },
    { path: '/ai/research', label: 'Research Lab', icon: <FlaskConical size={20} /> },
    { path: '/ai/strategy', label: 'Strategy Center', icon: <Gavel size={20} /> },
    { path: '/ai/command', label: 'Command Center', icon: <ShieldAlert size={20} /> },
  ];

  const renderNavItems = (items) => (
    <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      {items.map((item) => {
        const isActive = location.pathname === item.path || 
                         (item.path.startsWith('/market') && location.pathname.startsWith('/market') && item.path.split('/')[1] === location.pathname.split('/')[1]);
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
  );

  return (
    <div style={{
      width: '260px',
      borderRight: '1px solid var(--glass-border)',
      background: 'var(--bg-surface)',
      padding: '2rem 1rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '2rem',
      overflowY: 'auto'
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

      <div>
        <div style={{ padding: '0 1rem', marginBottom: '0.5rem', fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 'bold', letterSpacing: '0.05em' }}>
          Core
        </div>
        {renderNavItems(mainNavItems)}
      </div>

      <div>
        <div style={{ padding: '0 1rem', marginBottom: '0.5rem', fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--accent-primary)', fontWeight: 'bold', letterSpacing: '0.05em', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Brain size={14} />
          AI Intelligence
        </div>
        {renderNavItems(aiNavItems)}
      </div>
    </div>
  );
}

// Pages Placeholders
import Dashboard from './pages/Dashboard';
import MarketView from './pages/MarketView';
import BacktestView from './pages/BacktestView';
import ScreenerView from './pages/ScreenerView';
import DiscoveryView from './pages/DiscoveryView';
import FullAnalysisDashboard from './pages/FullAnalysisDashboard';
import TargetProfitSuggestions from './pages/TargetProfitSuggestions';
import PaperTrading from './pages/PaperTrading';

// New AI Pages
import PortfolioIntelligence from './pages/PortfolioIntelligence';
import MarketIntelligence from './pages/MarketIntelligence';
import AIDecisionCenter from './pages/AIDecisionCenter';
import ResearchLab from './pages/ResearchLab';
import StrategyCenter from './pages/StrategyCenter';
import CommandCenter from './pages/CommandCenter';
import AIInsightsDrawer from './components/AIInsightsDrawer';

function App() {
  return (
    <Router>
      <div className="app-container relative">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/target-profit" element={<TargetProfitSuggestions />} />
            <Route path="/discovery" element={<DiscoveryView />} />
            <Route path="/screener" element={<ScreenerView />} />
            <Route path="/market/:symbol" element={<MarketView />} />
            <Route path="/analysis/:symbol" element={<FullAnalysisDashboard />} />
            <Route path="/backtest" element={<BacktestView />} />
            <Route path="/paper-trading" element={<PaperTrading />} />

            {/* New AI Routes */}
            <Route path="/ai/portfolio" element={<PortfolioIntelligence />} />
            <Route path="/ai/market" element={<MarketIntelligence />} />
            <Route path="/ai/decision" element={<AIDecisionCenter />} />
            <Route path="/ai/research" element={<ResearchLab />} />
            <Route path="/ai/strategy" element={<StrategyCenter />} />
            <Route path="/ai/command" element={<CommandCenter />} />
          </Routes>
        </main>
        <AIInsightsDrawer />
      </div>
    </Router>
  );
}

export default App;
