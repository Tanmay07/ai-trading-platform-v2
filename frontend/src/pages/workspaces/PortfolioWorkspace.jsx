import React, { useState, useEffect } from 'react';
import WorkspaceTabs from '../../components/common/WorkspaceTabs';
import OverviewTab from '../../components/portfolio_v2/OverviewTab';
import HoldingsTab from '../../components/portfolio_v2/HoldingsTab';
import { getPortfolios } from '../../services/portfolioV2Api';

// Placeholder components for the other tabs
const TransactionsTab = () => <div className="p-4 text-gray-300">Transaction Ledger (Work in Progress)</div>;
const PerformanceTab = () => <div className="p-4 text-gray-300">Performance Analytics (Work in Progress)</div>;
const AllocationTab = () => <div className="p-4 text-gray-300">Allocation Charts (Work in Progress)</div>;
const RiskTab = () => <div className="p-4 text-gray-300">Risk Metrics (Work in Progress)</div>;
const HistoryTab = () => <div className="p-4 text-gray-300">Historical Timeline (Work in Progress)</div>;
const ReportsTab = () => <div className="p-4 text-gray-300">Import/Export Reports (Work in Progress)</div>;
const SettingsTab = () => <div className="p-4 text-gray-300">Portfolio Settings (Work in Progress)</div>;

const PortfolioWorkspace = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [portfolios, setPortfolios] = useState([]);
  const [selectedPortfolioId, setSelectedPortfolioId] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInit = async () => {
      try {
        const pts = await getPortfolios();
        setPortfolios(pts);
        if (pts && pts.length > 0) {
          setSelectedPortfolioId(pts[0].id);
        }
      } catch (err) {
        console.error("Failed to fetch portfolios", err);
      } finally {
        setLoading(false);
      }
    };
    fetchInit();
  }, []);

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'holdings', label: 'Holdings' },
    { id: 'transactions', label: 'Transactions' },
    { id: 'performance', label: 'Performance' },
    { id: 'allocation', label: 'Allocation' },
    { id: 'risk', label: 'Risk' },
    { id: 'history', label: 'History' },
    { id: 'reports', label: 'Reports' },
    { id: 'settings', label: 'Settings' }
  ];

  const renderTabContent = () => {
    if (loading) {
      return <div className="p-8 text-center text-gray-400 animate-pulse">Initializing workspace...</div>;
    }
    
    if (!selectedPortfolioId) {
      return <div className="p-8 text-center text-gray-400">No portfolio found. Please create a portfolio first.</div>;
    }

    switch (activeTab) {
      case 'overview': return <OverviewTab portfolioId={selectedPortfolioId} />;
      case 'holdings': return <HoldingsTab portfolioId={selectedPortfolioId} />;
      case 'transactions': return <TransactionsTab portfolioId={selectedPortfolioId} />;
      case 'performance': return <PerformanceTab portfolioId={selectedPortfolioId} />;
      case 'allocation': return <AllocationTab portfolioId={selectedPortfolioId} />;
      case 'risk': return <RiskTab portfolioId={selectedPortfolioId} />;
      case 'history': return <HistoryTab portfolioId={selectedPortfolioId} />;
      case 'reports': return <ReportsTab portfolioId={selectedPortfolioId} />;
      case 'settings': return <SettingsTab portfolioId={selectedPortfolioId} />;
      default: return null;
    }
  };

  return (
    <div className="h-full flex flex-col animate-fade-in bg-[#0B0E14]">
      <div className="mb-2 p-4 border-b border-gray-800 flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Portfolio Management</h1>
          <p className="text-gray-400 text-sm">Institutional-grade portfolio tracking, live valuation, and performance analytics.</p>
        </div>
        
        {/* Portfolio Selector */}
        {portfolios.length > 0 && (
          <div className="flex flex-col items-end">
            <label className="text-xs text-gray-500 mb-1 font-medium">ACTIVE PORTFOLIO</label>
            <select 
              className="bg-gray-800 border border-gray-700 text-white text-sm rounded-lg focus:ring-purple-500 focus:border-purple-500 block p-2 outline-none w-48 appearance-none cursor-pointer"
              value={selectedPortfolioId || ''}
              onChange={(e) => setSelectedPortfolioId(Number(e.target.value))}
            >
              {portfolios.map(p => (
                <option key={p.id} value={p.id}>{p.name} ({p.currency})</option>
              ))}
            </select>
          </div>
        )}
      </div>
      
      <div className="px-4">
        <WorkspaceTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      </div>
      
      <div className="flex-1 overflow-y-auto p-4">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default PortfolioWorkspace;
