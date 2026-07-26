import React, { useState } from 'react';
import WorkspaceTabs from '../../components/common/WorkspaceTabs';

// Placeholder components for the new tabs
const OverviewTab = () => <div className="p-4 text-gray-300">Overview Dashboard (Work in Progress)</div>;
const HoldingsTab = () => <div className="p-4 text-gray-300">Holdings Grid (Work in Progress)</div>;
const TransactionsTab = () => <div className="p-4 text-gray-300">Transaction Ledger (Work in Progress)</div>;
const PerformanceTab = () => <div className="p-4 text-gray-300">Performance Analytics (Work in Progress)</div>;
const AllocationTab = () => <div className="p-4 text-gray-300">Allocation Charts (Work in Progress)</div>;
const RiskTab = () => <div className="p-4 text-gray-300">Risk Metrics (Work in Progress)</div>;
const HistoryTab = () => <div className="p-4 text-gray-300">Historical Timeline (Work in Progress)</div>;
const ReportsTab = () => <div className="p-4 text-gray-300">Import/Export Reports (Work in Progress)</div>;
const SettingsTab = () => <div className="p-4 text-gray-300">Portfolio Settings (Work in Progress)</div>;

const PortfolioWorkspace = () => {
  const [activeTab, setActiveTab] = useState('overview');

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
    switch (activeTab) {
      case 'overview': return <OverviewTab />;
      case 'holdings': return <HoldingsTab />;
      case 'transactions': return <TransactionsTab />;
      case 'performance': return <PerformanceTab />;
      case 'allocation': return <AllocationTab />;
      case 'risk': return <RiskTab />;
      case 'history': return <HistoryTab />;
      case 'reports': return <ReportsTab />;
      case 'settings': return <SettingsTab />;
      default: return null;
    }
  };

  return (
    <div className="h-full flex flex-col animate-fade-in bg-[#0B0E14]">
      <div className="mb-2 p-4 border-b border-gray-800">
        <h1 className="text-3xl font-bold text-white mb-2">Portfolio Management</h1>
        <p className="text-gray-400 text-sm">Institutional-grade portfolio tracking, live valuation, and performance analytics.</p>
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
