import React, { useState } from 'react';
import WorkspaceTabs from '../../components/common/WorkspaceTabs';
import AIDecisionCenter from '../AIDecisionCenter';
import CommitteeIntelligence from '../CommitteeIntelligence';
import TargetProfitSuggestions from '../TargetProfitSuggestions';

const CommitteeWorkspace = () => {
  const [activeTab, setActiveTab] = useState('decision');

  const tabs = [
    { id: 'decision', label: 'AI Decision Center' },
    { id: 'committee', label: 'Investment Committee' },
    { id: 'targets', label: 'Weekly Targets' }
  ];

  return (
    <div className="h-full flex flex-col animate-fade-in">
      <div className="mb-2">
        <h1 className="text-3xl font-bold text-white mb-2">Investment Committee</h1>
        <p className="text-gray-400 text-sm">Review AI recommendations, approve trades, and set profit targets.</p>
      </div>
      
      <WorkspaceTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'decision' && <AIDecisionCenter />}
        {activeTab === 'committee' && <CommitteeIntelligence />}
        {activeTab === 'targets' && <TargetProfitSuggestions />}
      </div>
    </div>
  );
};

export default CommitteeWorkspace;
