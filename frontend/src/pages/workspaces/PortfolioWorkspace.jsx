import React, { useState } from 'react';
import WorkspaceTabs from '../../components/common/WorkspaceTabs';
import PortfolioIntelligence from '../PortfolioIntelligence';
import PortfolioOptimizer from '../PortfolioOptimizer';
import StrategyIntelligence from '../StrategyIntelligence';

const PortfolioWorkspace = () => {
  const [activeTab, setActiveTab] = useState('intelligence');

  const tabs = [
    { id: 'intelligence', label: 'Portfolio Intelligence' },
    { id: 'optimizer', label: 'Optimizer' },
    { id: 'multi-strategy', label: 'Multi-Strategy Allocation' }
  ];

  return (
    <div className="h-full flex flex-col animate-fade-in">
      <div className="mb-2">
        <h1 className="text-3xl font-bold text-white mb-2">Portfolio Workspace</h1>
        <p className="text-gray-400 text-sm">Analyze holdings, optimize allocations, and review risk attribution.</p>
      </div>
      
      <WorkspaceTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'intelligence' && <PortfolioIntelligence />}
        {activeTab === 'optimizer' && <PortfolioOptimizer />}
        {activeTab === 'multi-strategy' && <StrategyIntelligence />}
      </div>
    </div>
  );
};

export default PortfolioWorkspace;
