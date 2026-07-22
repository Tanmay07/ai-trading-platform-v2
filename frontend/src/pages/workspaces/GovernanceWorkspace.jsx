import React, { useState } from 'react';
import WorkspaceTabs from '../../components/common/WorkspaceTabs';
import DecisionIntelligenceDashboard from '../DecisionIntelligenceDashboard';
import MetaDecisionIntelligence from '../MetaDecisionIntelligence';
import TradeValidationDashboard from '../TradeValidationDashboard';
import TradeOutcomeIntelligence from '../TradeOutcomeIntelligence';

const GovernanceWorkspace = () => {
  const [activeTab, setActiveTab] = useState('decision');

  const tabs = [
    { id: 'decision', label: 'Decision Governance' },
    { id: 'meta', label: 'Meta Decision Engine' },
    { id: 'validation', label: 'Trade Validation' },
    { id: 'outcomes', label: 'Outcome Auditing' }
  ];

  return (
    <div className="h-full flex flex-col animate-fade-in">
      <div className="mb-2">
        <h1 className="text-3xl font-bold text-indigo-400 mb-2">Governance & Trust</h1>
        <p className="text-gray-400 text-sm">Monitor decision intelligence, validate trades, and ensure AI compliance.</p>
      </div>
      
      <WorkspaceTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'decision' && <DecisionIntelligenceDashboard />}
        {activeTab === 'meta' && <MetaDecisionIntelligence />}
        {activeTab === 'validation' && <TradeValidationDashboard />}
        {activeTab === 'outcomes' && <TradeOutcomeIntelligence />}
      </div>
    </div>
  );
};

export default GovernanceWorkspace;
