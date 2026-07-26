import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Layout
import RootLayout from './components/layout/RootLayout';

// Workspaces
import DashboardWorkspace from './pages/workspaces/DashboardWorkspace';
import MarketsWorkspace from './pages/workspaces/MarketsWorkspace';
import ResearchWorkspace from './pages/workspaces/ResearchWorkspace';
import PortfolioRecommendationWorkspace from './pages/workspaces/PortfolioRecommendationWorkspace';
import PortfolioWorkspace from './pages/workspaces/PortfolioWorkspace';
import PaperTradingWorkspace from './pages/workspaces/PaperTradingWorkspace';
import AICopilotWorkspace from './pages/workspaces/AICopilotWorkspace';
import PlatformWorkspace from './pages/workspaces/PlatformWorkspace';
import PolicyAdminWorkspace from './pages/workspaces/PolicyAdminWorkspace';
import MarketIntelligenceWorkspace from './pages/workspaces/MarketIntelligenceWorkspace';
import AICIOWorkspace from './pages/workspaces/AICIOWorkspace';
import AIStudioWorkspace from './pages/workspaces/AIStudioWorkspace';
import DataStudioWorkspace from './pages/workspaces/DataStudioWorkspace';
import GovernanceWorkspace from './pages/workspaces/GovernanceWorkspace';

// Auth State (to protect admin routes)
import { useAuthStore } from './store/authStore';

// Providers & Global CSS
import './index.css';

const ProtectedAdminRoute = ({ children }) => {
  const { isAdmin } = useAuthStore();
  if (!isAdmin) {
    return <Navigate to="/" replace />;
  }
  return children;
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<RootLayout />}>
          {/* Primary Navigation Workspaces */}
          <Route index element={<DashboardWorkspace />} />
          <Route path="markets/*" element={<MarketsWorkspace />} />
          <Route path="research/*" element={<ResearchWorkspace />} />
          <Route path="committee/*" element={<PortfolioRecommendationWorkspace />} />
          <Route path="portfolio/*" element={<PortfolioWorkspace />} />
          <Route path="paper-trading/*" element={<PaperTradingWorkspace />} />
          <Route path="copilot/*" element={<AICopilotWorkspace />} />
          
          {/* Administrator Workspaces */}
          <Route path="platform/*" element={
            <ProtectedAdminRoute>
              <PlatformWorkspace />
            </ProtectedAdminRoute>
          } />
          <Route path="ai-studio/*" element={
            <ProtectedAdminRoute>
              <AIStudioWorkspace />
            </ProtectedAdminRoute>
          } />
          <Route path="ai-cio/*" element={
            <ProtectedAdminRoute>
              <AICIOWorkspace />
            </ProtectedAdminRoute>
          } />
          <Route path="market-intelligence/*" element={
            <ProtectedAdminRoute>
              <MarketIntelligenceWorkspace />
            </ProtectedAdminRoute>
          } />
          <Route path="policy-admin/*" element={
            <ProtectedAdminRoute>
              <PolicyAdminWorkspace />
            </ProtectedAdminRoute>
          } />
          <Route path="data-studio/*" element={
            <ProtectedAdminRoute>
              <DataStudioWorkspace />
            </ProtectedAdminRoute>
          } />
          <Route path="governance/*" element={
            <ProtectedAdminRoute>
              <GovernanceWorkspace />
            </ProtectedAdminRoute>
          } />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
