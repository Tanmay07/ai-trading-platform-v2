import React, { useState } from 'react';
import WorkspaceTabs from '../../components/common/WorkspaceTabs';
import StrategyCenter from '../StrategyCenter';
import CommandCenter from '../CommandCenter';

const AICopilotWorkspace = () => {
  const [activeTab, setActiveTab] = useState('command');

  const tabs = [
    { id: 'command', label: 'Command Center' },
    { id: 'strategy', label: 'Strategy Builder' }
  ];

  return (
    <div className="h-full flex flex-col animate-fade-in">
      <div className="mb-2">
        <h1 className="text-3xl font-bold text-white mb-2">AI Copilot</h1>
        <p className="text-gray-400 text-sm">Conversational AI for building strategies and querying the platform.</p>
      </div>
      
      <WorkspaceTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'command' && <CommandCenter />}
        {activeTab === 'strategy' && <StrategyCenter />}
      </div>
    </div>
  );
};

export default AICopilotWorkspace;
