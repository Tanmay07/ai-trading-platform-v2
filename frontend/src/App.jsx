import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import { Activity, LayoutDashboard, History, Layers, Compass, Target, Brain, LineChart, Cpu, FlaskConical, Gavel, ShieldAlert, Database, BrainCircuit, TrendingUp, Globe, ActivitySquare, Microscope, Split, PlayCircle, Zap, Radio } from 'lucide-react';
import './index.css';

// Layout Component
function Sidebar() {
  const location = useLocation();
  const mainNavItems = [
    { path: '/', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
    { path: '/live-trading', label: 'Live Trading Desk', icon: <Zap size={20} /> },
    { path: '/discovery', label: 'AI Discovery', icon: <Compass size={20} /> },
    { path: '/target-profit', label: 'Weekly Targets', icon: <Target size={20} /> },
    { path: '/paper-trading', label: 'Paper Trading Engine', icon: <Target size={20} /> },
    { path: '/alpha-research', label: 'Alpha Research Lab', icon: <Compass size={20} /> },
    { path: '/multi-strategy', label: 'Multi-Strategy Portfolio', icon: <Layers size={20} /> },
    { path: '/portfolio-optimizer', label: 'Portfolio Optimizer', icon: <Compass size={20} /> },
    { path: '/event-intelligence', label: 'Event Intelligence', icon: <Radio size={20} /> },
    { path: '/market-regime', label: 'Market Regime & Digital Twin', icon: <ActivitySquare size={20} /> },
    { path: '/adaptive-intelligence', label: 'Adaptive Intelligence', icon: <Compass size={20} /> },
    { path: '/operations-center', label: 'Operations Center', icon: <Target size={20} /> },
    { path: '/screener', label: 'Sector Screener', icon: <Layers size={20} /> },
    { path: '/analysis/RELIANCE.NS', label: 'Full Analysis', icon: <Activity size={20} /> },
    { path: '/market/RELIANCE.NS', label: 'Market View', icon: <Activity size={20} /> },
    { path: '/backtest', label: 'Backtesting', icon: <History size={20} /> },
    { path: '/platform/bootstrap', label: 'Platform Bootstrap', icon: <PlayCircle size={20} /> },
  ];

  const aiNavItems = [
    { path: '/ai/portfolio', label: 'Portfolio Intelligence', icon: <LineChart size={20} /> },
    { path: '/ai/execution', label: 'Execution Intelligence', icon: <Target size={20} /> },
    { path: '/ai/committee', label: 'Investment Committee', icon: <Gavel size={20} /> },
    { path: '/ai/market', label: 'Market Intelligence', icon: <Activity size={20} /> },
    { path: '/ai/decision', label: 'AI Decision Center', icon: <Cpu size={20} /> },
    { path: '/ai/research', label: 'Research Lab', icon: <FlaskConical size={20} /> },
    { path: '/ai/strategy', label: 'Strategy Center', icon: <Gavel size={20} /> },
    { path: '/ai/command', label: 'Command Center', icon: <ShieldAlert size={20} /> },
  ];

  const platformNavItems = [
    { path: '/platform/data', label: 'Data Intelligence', icon: <Database size={20} /> },
    { path: '/platform/model', label: 'Model Intelligence', icon: <BrainCircuit size={20} /> },
    { path: '/platform/prediction', label: 'Prediction Intelligence', icon: <TrendingUp size={20} /> },
    { path: '/platform/model-arena', label: 'G7.3 Model Arena', icon: <BrainCircuit size={20} /> },
    { path: '/platform/paper-trading', label: 'G7.4 Paper Trading', icon: <Target size={20} /> },
    { path: '/platform/continuous-learning', label: 'G7.4 Continuous Learning', icon: <FlaskConical size={20} /> },
    { path: '/platform/decision-intelligence', label: 'G7.5 Decision Intelligence', icon: <ShieldAlert size={20} /> },
    { path: '/platform/market-hub', label: 'Market Intelligence Hub', icon: <Globe size={20} /> },
    { path: '/platform/health', label: 'Platform Health', icon: <ActivitySquare size={20} /> },
    { path: '/platform/tradability', label: 'Tradability Engine', icon: <ShieldAlert size={20} /> },
    { path: '/platform/features', label: 'Feature Intelligence', icon: <Layers size={20} /> },
    { path: '/platform/alpha', label: 'Alpha Research Lab', icon: <Microscope size={20} /> },
    { path: '/platform/datasets', label: 'Dataset Engineering', icon: <Database size={20} /> },
    { path: '/platform/scenarios', label: 'Scenario Generators', icon: <Split size={20} /> },
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

      <div>
        <div style={{ padding: '0 1rem', marginBottom: '0.5rem', fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 'bold', letterSpacing: '0.05em' }}>
          AI Platform
        </div>
        {renderNavItems(platformNavItems)}
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
import PaperTradingEngine from './pages/PaperTradingEngine';

// New AI Pages
import PortfolioIntelligence from './pages/PortfolioIntelligence';
import ExecutionIntelligence from './pages/ExecutionIntelligence';
import CommitteeIntelligence from './pages/CommitteeIntelligence';
import AdaptiveIntelligence from './pages/AdaptiveIntelligence';
import OperationsCenter from './pages/OperationsCenter';
import AlphaResearchLab from './pages/AlphaResearchLab';
import StrategyIntelligence from './pages/StrategyIntelligence';
import PortfolioOptimizer from './pages/PortfolioOptimizer';
import EventIntelligence from './pages/EventIntelligence';
import MarketRegime from './pages/MarketRegime';

// import DiagnosticsIntelligence from './pages/DiagnosticsIntelligence';
import TradeOutcomeIntelligence from './pages/TradeOutcomeIntelligence';
import TradeValidationDashboard from './pages/TradeValidationDashboard';
import AIDecisionCenter from './pages/AIDecisionCenter';
import ResearchLab from './pages/ResearchLab';
import StrategyCenter from './pages/StrategyCenter';
import CommandCenter from './pages/CommandCenter';
import AIInsightsDrawer from './components/AIInsightsDrawer';

// Platform Pages (Phase F2)
import DataIntelligence from './pages/DataIntelligence';
import ModelIntelligence from './pages/ModelIntelligence';
import MetaDecisionIntelligence from './pages/MetaDecisionIntelligence';
import TradeIntelligence from './pages/TradeIntelligence';
import FeatureStoreIntelligence from './pages/FeatureStoreIntelligence';
import FactorEngineIntelligence from './pages/FactorEngineIntelligence';
import ModelArenaIntelligence from './pages/ModelArenaIntelligence';
import PaperTradingValidation from './pages/PaperTradingValidation';
import ContinuousLearningDashboard from './pages/ContinuousLearningDashboard';
import DecisionIntelligenceDashboard from './pages/DecisionIntelligenceDashboard';
import ExecutiveDashboard from './pages/ExecutiveDashboard';
import ResearchTerminal from './pages/ResearchTerminal';
import ProductionIntelligence from './pages/ProductionIntelligence';
import PredictionIntelligence from './pages/PredictionIntelligence';
import MarketIntelligenceHub from './pages/MarketIntelligenceHub';
import PlatformHealth from './pages/PlatformHealth';
import TradabilityIntelligence from './pages/TradabilityIntelligence';
import FeatureIntelligence from './pages/FeatureIntelligence';
import FactorIntelligence from './pages/FactorIntelligence';
import ModelArena from './pages/ModelArena';
import AlphaIntelligence from './pages/AlphaIntelligence';
import DatasetIntelligence from './pages/DatasetIntelligence';
import ScenarioIntelligence from './pages/ScenarioIntelligence';
import BootstrapWizard from './pages/BootstrapWizard';
import LiveTradingDesk from './pages/LiveTradingDesk';

function App() {
  return (
    <Router>
      <div className="app-container relative">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<ExecutiveDashboard />} />
            <Route path="/target-profit" element={<TargetProfitSuggestions />} />
            <Route path="/discovery" element={<DiscoveryView />} />
            <Route path="/screener" element={<ScreenerView />} />
            <Route path="/market/:symbol" element={<MarketView />} />
            <Route path="/analysis/:symbol" element={<FullAnalysisDashboard />} />
            <Route path="/backtest" element={<BacktestView />} />
            <Route path="/paper-trading" element={<PaperTradingEngine />} />
            <Route path="/live-trading" element={<LiveTradingDesk />} />

            {/* New AI Routes */}
            <Route path="/ai/portfolio" element={<PortfolioIntelligence />} />
            <Route path="/ai/execution" element={<ExecutionIntelligence />} />
            <Route path="/committee" element={<CommitteeIntelligence />} />
            <Route path="/alpha-research" element={<AlphaResearchLab />} />
            <Route path="/multi-strategy" element={<StrategyIntelligence />} />
            <Route path="/portfolio-optimizer" element={<PortfolioOptimizer />} />
            <Route path="/event-intelligence" element={<EventIntelligence />} />
            <Route path="/market-regime" element={<MarketRegime />} />
            <Route path="/adaptive-intelligence" element={<AdaptiveIntelligence />} />
            <Route path="/operations-center" element={<OperationsCenter />} />
            {/* <Route path="training" element={<DiagnosticsIntelligence />} /> */}
            <Route path="outcomes" element={<TradeOutcomeIntelligence />} />
            <Route path="validation" element={<TradeValidationDashboard />} />
            {/* <Route path="models" element={<ModelsList />} /> */}
            <Route path="/ai/research" element={<ResearchLab />} />
            <Route path="/ai/strategy" element={<StrategyCenter />} />
            <Route path="/ai/command" element={<CommandCenter />} />

            {/* Platform Routes */}
            <Route path="/platform/data" element={<DataIntelligence />} />
            <Route path="/platform/model" element={<ModelIntelligence />} />
            <Route path="/platform/prediction" element={<PredictionIntelligence />} />
            <Route path="/platform/market-hub" element={<MarketIntelligenceHub />} />
            <Route path="/platform/health" element={<PlatformHealth />} />
            <Route path="/platform/tradability" element={<TradabilityIntelligence />} />
            <Route path="/platform/features" element={<FeatureIntelligence />} />
            <Route path="/platform/factor-intel" element={<FactorIntelligence />} />
            <Route path="/platform/model" element={<ModelArena />} />
            <Route path="/platform/model-arena" element={<ModelArenaIntelligence />} />
            <Route path="/platform/paper-trading" element={<PaperTradingValidation />} />
            <Route path="/platform/continuous-learning" element={<ContinuousLearningDashboard />} />
            <Route path="/platform/decision-intelligence" element={<DecisionIntelligenceDashboard />} />
            <Route path="/platform/research/:symbol" element={<ResearchTerminal />} />
            <Route path="/platform/production" element={<ProductionIntelligence />} />
            <Route path="/platform/alpha" element={<AlphaIntelligence />} />
                
                {/* Meta Decision Engine (Phase F) */}
                <Route path="/platform/meta" element={<MetaDecisionIntelligence />} />
                
                {/* Portfolio Intelligence Engine (Phase F1) */}
                <Route path="/platform/portfolio" element={<PortfolioIntelligence />} />
                
                {/* Fallback to Dashboard */}
                <Route path="*" element={<Navigate to="/platform/dataset" replace />} />
          </Routes>
        </main>
        <AIInsightsDrawer />
      </div>
    </Router>
  );
}

export default App;
