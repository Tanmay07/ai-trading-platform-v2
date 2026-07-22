import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Layout
import RootLayout from './components/layout/RootLayout';

// Workspaces
import DashboardWorkspace from './pages/workspaces/DashboardWorkspace';
import MarketsWorkspace from './pages/workspaces/MarketsWorkspace';
import ResearchWorkspace from './pages/workspaces/ResearchWorkspace';
import CommitteeWorkspace from './pages/workspaces/CommitteeWorkspace';
import PortfolioWorkspace from './pages/workspaces/PortfolioWorkspace';
import PaperTradingWorkspace from './pages/workspaces/PaperTradingWorkspace';
import AICopilotWorkspace from './pages/workspaces/AICopilotWorkspace';
import PlatformWorkspace from './pages/workspaces/PlatformWorkspace';
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
          <Route path="committee/*" element={<CommitteeWorkspace />} />
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
