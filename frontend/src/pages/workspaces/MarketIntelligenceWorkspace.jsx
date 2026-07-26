import React, { useState, useEffect } from 'react';
import { Activity, Briefcase, BarChart2, Calendar, Zap, AlertTriangle, Eye, ArrowRight, Play } from 'lucide-react';

const MarketIntelligenceWorkspace = () => {
  const [activeTab, setActiveTab] = useState('today');
  const [events, setEvents] = useState([]);
  const [calendar, setCalendar] = useState([]);
  
  useEffect(() => {
    // Mock Data for frontend demo
    setEvents([
      { id: 1, type: "MACRO", subtype: "RBI_POLICY", priority: "CRITICAL", impact: 95, symbols: ["NIFTY50", "BANKNIFTY"], time: "10 mins ago", narrative: "RBI unexpected rate cut by 25bps." },
      { id: 2, type: "TECHNICAL", subtype: "BREAKOUT", priority: "HIGH", impact: 75, symbols: ["HDFCBANK"], time: "1 hour ago", narrative: "Price broke resistance at 1700." },
      { id: 3, type: "CORPORATE", subtype: "QUARTERLY_RESULTS", priority: "HIGH", impact: 80, symbols: ["TCS"], time: "2 hours ago", narrative: "Q3 Results: Revenue +15%, EPS beat by 5%." },
      { id: 4, type: "PORTFOLIO", subtype: "RISK_INCREASED", priority: "MEDIUM", impact: 60, symbols: ["RELIANCE"], time: "3 hours ago", narrative: "Volatility increased beyond policy threshold." }
    ]);
    
    setCalendar([
      { date: "2026-07-27", event: "Infosys Q1 Results", type: "CORPORATE", impact: "HIGH", symbol: "INFY" },
      { date: "2026-07-28", event: "US Fed Rate Decision", type: "MACRO", impact: "CRITICAL" },
      { date: "2026-08-01", event: "Auto Sales Numbers", type: "SECTOR", impact: "MEDIUM", symbol: "MARUTI, M&M" }
    ]);
  }, []);

  const triggerMockEvent = () => {
    alert("Mock Breakout Event injected into the backend! Check the Alert logs.");
    // In reality, this would hit POST /api/events/mock/technical/breakout
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'CRITICAL': return 'bg-red-900 text-red-400 border-red-700';
      case 'HIGH': return 'bg-orange-900 text-orange-400 border-orange-700';
      case 'MEDIUM': return 'bg-blue-900 text-blue-400 border-blue-700';
      default: return 'bg-gray-800 text-gray-400 border-gray-700';
    }
  };

  const getIcon = (type) => {
    switch(type) {
      case 'MACRO': return <Activity size={16} />;
      case 'TECHNICAL': return <BarChart2 size={16} />;
      case 'CORPORATE': return <Briefcase size={16} />;
      case 'PORTFOLIO': return <Zap size={16} />;
      default: return <Eye size={16} />;
    }
  };

  return (
    <div className="h-full flex flex-col p-6 animate-fade-in bg-[#0B0E14] text-white overflow-y-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-3"><Zap className="text-yellow-400" /> Enterprise Market Intelligence</h1>
          <p className="text-gray-400">Real-time event detection, correlation, and automated response.</p>
        </div>
        <button onClick={triggerMockEvent} className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded font-semibold flex items-center gap-2 transition-colors">
          <Play size={18} /> Inject Mock Event
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 border-b border-gray-800 mb-6">
        {['today', 'portfolio', 'market', 'corporate', 'technical', 'calendar'].map(tab => (
          <button 
            key={tab}
            onClick={() => setActiveTab(tab)} 
            className={`pb-2 px-3 font-medium capitalize transition-colors ${activeTab === tab ? 'text-blue-400 border-b-2 border-blue-400' : 'text-gray-500 hover:text-gray-300'}`}
          >
            {tab.replace('-', ' ')}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 space-y-4">
        {activeTab === 'calendar' ? (
          <div className="bg-gray-900 border border-gray-800 rounded p-4">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2"><Calendar size={20} /> Upcoming Events</h2>
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-gray-800 text-gray-400 text-sm">
                  <th className="pb-2">Date</th>
                  <th className="pb-2">Event</th>
                  <th className="pb-2">Type</th>
                  <th className="pb-2">Impact</th>
                  <th className="pb-2">Symbols</th>
                </tr>
              </thead>
              <tbody>
                {calendar.map((c, i) => (
                  <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-800 transition-colors">
                    <td className="py-3 text-sm text-gray-300 font-mono">{c.date}</td>
                    <td className="py-3 font-medium">{c.event}</td>
                    <td className="py-3 text-sm text-gray-400">{c.type}</td>
                    <td className="py-3">
                      <span className={`text-xs px-2 py-1 rounded border font-bold ${getPriorityColor(c.impact)}`}>{c.impact}</span>
                    </td>
                    <td className="py-3 text-blue-400 text-sm">{c.symbol || 'Market-Wide'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {events.filter(e => activeTab === 'today' || e.type.toLowerCase() === activeTab).map(e => (
              <div key={e.id} className="bg-gray-900 border border-gray-800 rounded p-4 hover:border-gray-600 transition-colors cursor-pointer group">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-full bg-gray-800 text-gray-300 group-hover:text-white transition-colors`}>
                      {getIcon(e.type)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg">{e.subtype.replace('_', ' ')}</h3>
                      <div className="text-xs text-gray-400 flex items-center gap-2">
                        <span>{e.time}</span> • <span>Impact: {e.impact}/100</span>
                      </div>
                    </div>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded border font-bold ${getPriorityColor(e.priority)}`}>
                    {e.priority}
                  </span>
                </div>
                
                <p className="text-gray-300 mb-4">{e.narrative}</p>
                
                <div className="flex justify-between items-center border-t border-gray-800 pt-3">
                  <div className="flex gap-2">
                    {e.symbols.map(sym => (
                      <span key={sym} className="text-xs font-mono bg-blue-900/30 text-blue-400 border border-blue-900 px-2 py-1 rounded">
                        {sym}
                      </span>
                    ))}
                  </div>
                  <button className="text-sm font-semibold text-gray-400 hover:text-white flex items-center gap-1 transition-colors">
                    Analyze Impact <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MarketIntelligenceWorkspace;
