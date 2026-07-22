import React, { useState } from 'react';
import WorkspaceTabs from '../../components/common/WorkspaceTabs';
import AlphaResearchLab from '../AlphaResearchLab';
import ResearchLab from '../ResearchLab';
import BacktestView from '../BacktestView';
import FullAnalysisDashboard from '../FullAnalysisDashboard';

const ResearchWorkspace = () => {
  const [activeTab, setActiveTab] = useState('alpha');

  const tabs = [
    { id: 'alpha', label: 'Alpha Research' },
    { id: 'lab', label: 'Research Lab' },
    { id: 'backtest', label: 'Backtesting' },
    { id: 'full-analysis', label: 'Deep Analysis' }
  ];

  return (
    <div className="h-full flex flex-col animate-fade-in">
      <div className="mb-2">
        <h1 className="text-3xl font-bold text-white mb-2">Research Workspace</h1>
        <p className="text-gray-400 text-sm">Design, backtest, and analyze alpha strategies.</p>
      </div>
      
      <WorkspaceTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'alpha' && <AlphaResearchLab />}
        {activeTab === 'lab' && <ResearchLab />}
        {activeTab === 'backtest' && <BacktestView />}
        {activeTab === 'full-analysis' && <FullAnalysisDashboard symbol="RELIANCE.NS" />}
      </div>
    </div>
  );
};

export default ResearchWorkspace;
