import React, { useState } from 'react';
import WorkspaceTabs from '../../components/common/WorkspaceTabs';
import OperationsCenter from '../OperationsCenter';
import PlatformHealth from '../PlatformHealth';
import BootstrapWizard from '../BootstrapWizard';

const PlatformWorkspace = () => {
  const [activeTab, setActiveTab] = useState('health');

  const tabs = [
    { id: 'health', label: 'Platform Health' },
    { id: 'operations', label: 'Operations Center' },
    { id: 'bootstrap', label: 'System Bootstrap' }
  ];

  return (
    <div className="h-full flex flex-col animate-fade-in">
      <div className="mb-2">
        <h1 className="text-3xl font-bold text-indigo-400 mb-2">Platform Operations</h1>
        <p className="text-gray-400 text-sm">System infrastructure, microservices health, and core orchestration.</p>
      </div>
      
      <WorkspaceTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'health' && <PlatformHealth />}
        {activeTab === 'operations' && <OperationsCenter />}
        {activeTab === 'bootstrap' && <BootstrapWizard />}
      </div>
    </div>
  );
};

export default PlatformWorkspace;
