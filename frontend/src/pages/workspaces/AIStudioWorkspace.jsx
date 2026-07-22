import React, { useState } from 'react';
import WorkspaceTabs from '../../components/common/WorkspaceTabs';
import ModelArenaIntelligence from '../ModelArenaIntelligence';
import ContinuousLearningDashboard from '../ContinuousLearningDashboard';
import PredictionIntelligence from '../PredictionIntelligence';
import ModelIntelligence from '../ModelIntelligence';

const AIStudioWorkspace = () => {
  const [activeTab, setActiveTab] = useState('arena');

  const tabs = [
    { id: 'arena', label: 'Model Arena (G7.3)' },
    { id: 'learning', label: 'Continuous Learning (G7.4)' },
    { id: 'registry', label: 'Model Registry' },
    { id: 'predictions', label: 'Prediction Engine' }
  ];

  return (
    <div className="h-full flex flex-col animate-fade-in">
      <div className="mb-2">
        <h1 className="text-3xl font-bold text-indigo-400 mb-2">AI Studio</h1>
        <p className="text-gray-400 text-sm">Manage machine learning pipelines, evaluate models, and monitor drift.</p>
      </div>
      
      <WorkspaceTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'arena' && <ModelArenaIntelligence />}
        {activeTab === 'learning' && <ContinuousLearningDashboard />}
        {activeTab === 'registry' && <ModelIntelligence />}
        {activeTab === 'predictions' && <PredictionIntelligence />}
      </div>
    </div>
  );
};

export default AIStudioWorkspace;
