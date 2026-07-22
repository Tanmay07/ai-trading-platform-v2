import React, { useState } from 'react';
import WorkspaceTabs from '../../components/common/WorkspaceTabs';
import LiveTradingDesk from '../LiveTradingDesk';
import PaperTradingEngine from '../PaperTradingEngine';
import ExecutionIntelligence from '../ExecutionIntelligence';

const PaperTradingWorkspace = () => {
  const [activeTab, setActiveTab] = useState('live');

  const tabs = [
    { id: 'live', label: 'Live Trading Desk' },
    { id: 'paper', label: 'Paper Portfolios' },
    { id: 'execution', label: 'Execution Intelligence' }
  ];

  return (
    <div className="h-full flex flex-col animate-fade-in">
      <div className="mb-2">
        <h1 className="text-3xl font-bold text-white mb-2">Execution & Paper Trading</h1>
        <p className="text-gray-400 text-sm">Manage live execution and track paper portfolios.</p>
      </div>
      
      <WorkspaceTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'live' && <LiveTradingDesk />}
        {activeTab === 'paper' && <PaperTradingEngine />}
        {activeTab === 'execution' && <ExecutionIntelligence />}
      </div>
    </div>
  );
};

export default PaperTradingWorkspace;
