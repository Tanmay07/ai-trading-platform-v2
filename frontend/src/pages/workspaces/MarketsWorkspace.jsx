import React, { useState } from 'react';
import WorkspaceTabs from '../../components/common/WorkspaceTabs';
import DiscoveryView from '../DiscoveryView';
import ScreenerView from '../ScreenerView';
import EventIntelligence from '../EventIntelligence';
import MarketRegime from '../MarketRegime';
import MarketView from '../MarketView';

const MarketsWorkspace = () => {
  const [activeTab, setActiveTab] = useState('discovery');

  const tabs = [
    { id: 'discovery', label: 'AI Discovery' },
    { id: 'screener', label: 'Sector Explorer' },
    { id: 'regime', label: 'Market Regime' },
    { id: 'events', label: 'Events' },
    { id: 'market-view', label: 'Market View (NIFTY)' }
  ];

  return (
    <div className="h-full flex flex-col animate-fade-in">
      <div className="mb-2">
        <h1 className="text-3xl font-bold text-white mb-2">Markets Intelligence</h1>
        <p className="text-gray-400 text-sm">Comprehensive market discovery, sectors, and regime analysis.</p>
      </div>
      
      <WorkspaceTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'discovery' && <DiscoveryView />}
        {activeTab === 'screener' && <ScreenerView />}
        {activeTab === 'regime' && <MarketRegime />}
        {activeTab === 'events' && <EventIntelligence />}
        {activeTab === 'market-view' && <MarketView symbol="^NSEI" />}
      </div>
    </div>
  );
};

export default MarketsWorkspace;
