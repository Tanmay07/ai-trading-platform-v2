import React, { useState } from 'react';
import WorkspaceTabs from '../../components/common/WorkspaceTabs';
import DataIntelligence from '../DataIntelligence';
import DatasetIntelligence from '../DatasetIntelligence';
import FeatureIntelligence from '../FeatureIntelligence';
import TradabilityIntelligence from '../TradabilityIntelligence';
import ScenarioIntelligence from '../ScenarioIntelligence';

const DataStudioWorkspace = () => {
  const [activeTab, setActiveTab] = useState('data');

  const tabs = [
    { id: 'data', label: 'Data Intelligence' },
    { id: 'datasets', label: 'Dataset Engineering' },
    { id: 'features', label: 'Feature Intelligence' },
    { id: 'tradability', label: 'Tradability Engine' },
    { id: 'scenarios', label: 'Scenario Generator' }
  ];

  return (
    <div className="h-full flex flex-col animate-fade-in">
      <div className="mb-2">
        <h1 className="text-3xl font-bold text-indigo-400 mb-2">Data Studio</h1>
        <p className="text-gray-400 text-sm">Design features, build datasets, and manage institutional data pipelines.</p>
      </div>
      
      <WorkspaceTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'data' && <DataIntelligence />}
        {activeTab === 'datasets' && <DatasetIntelligence />}
        {activeTab === 'features' && <FeatureIntelligence />}
        {activeTab === 'tradability' && <TradabilityIntelligence />}
        {activeTab === 'scenarios' && <ScenarioIntelligence />}
      </div>
    </div>
  );
};

export default DataStudioWorkspace;
