import React, { useState, useEffect } from 'react';
import { Settings, PlusCircle, Save, Sliders, PlayCircle, Clock } from 'lucide-react';

const PolicyAdminWorkspace = () => {
  const [policies, setPolicies] = useState([]);
  const [activeTab, setActiveTab] = useState('library'); // library, editor, audit
  const [auditLogs, setAuditLogs] = useState([]);

  useEffect(() => {
    // Mocking API fetch for policies
    setPolicies([
      { id: 1, name: "Growth Default v1.0", style: "Growth", active: true, weights: {tech: 25, val: 25, ctx: 25, risk: 25} },
      { id: 2, name: "Aggressive Momentum v2.1", style: "Momentum", active: false, weights: {tech: 60, val: 0, ctx: 10, risk: 30} },
      { id: 3, name: "Value Investing v1.5", style: "Value", active: false, weights: {tech: 10, val: 50, ctx: 20, risk: 20} }
    ]);

    setAuditLogs([
      { id: 1, symbol: "HDFCBANK", decision: "Strong Buy", policy: "Growth Default v1.0", time: "10 mins ago" },
      { id: 2, symbol: "RELIANCE", decision: "Trim Position", policy: "Growth Default v1.0", time: "12 mins ago" },
      { id: 3, symbol: "TCS", decision: "Buy More", policy: "Aggressive Momentum v2.1", time: "1 hour ago" }
    ]);
  }, []);

  return (
    <div className="h-full flex flex-col p-6 animate-fade-in bg-[#0B0E14] text-white overflow-y-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">Policy Engine Administration</h1>
          <p className="text-gray-400">Configure and version-control the investment decision logic.</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded font-semibold flex items-center gap-2 transition-colors">
          <PlusCircle size={18} /> New Policy
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 border-b border-gray-800 mb-6">
        <button onClick={() => setActiveTab('library')} className={`pb-2 px-2 font-medium ${activeTab === 'library' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-gray-500 hover:text-gray-300'}`}>Policy Library</button>
        <button onClick={() => setActiveTab('editor')} className={`pb-2 px-2 font-medium ${activeTab === 'editor' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-gray-500 hover:text-gray-300'}`}>Policy Editor</button>
        <button onClick={() => setActiveTab('audit')} className={`pb-2 px-2 font-medium ${activeTab === 'audit' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-gray-500 hover:text-gray-300'}`}>Decision Audit Trail</button>
      </div>

      {/* Tab Content */}
      {activeTab === 'library' && (
        <div className="bg-gray-900 border border-gray-800 rounded p-4">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-gray-700 text-gray-400 text-sm">
                <th className="p-2">Policy Name</th>
                <th className="p-2">Style</th>
                <th className="p-2">Weights (T/V/C/R)</th>
                <th className="p-2">Status</th>
                <th className="p-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {policies.map(p => (
                <tr key={p.id} className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors">
                  <td className="p-2 font-medium">{p.name}</td>
                  <td className="p-2">{p.style}</td>
                  <td className="p-2 font-mono text-sm">{p.weights.tech}% / {p.weights.val}% / {p.weights.ctx}% / {p.weights.risk}%</td>
                  <td className="p-2">
                    {p.active ? <span className="text-green-400 text-xs font-bold bg-green-900/30 px-2 py-1 rounded border border-green-800">ACTIVE</span> : <span className="text-gray-500 text-xs font-bold bg-gray-800 px-2 py-1 rounded">INACTIVE</span>}
                  </td>
                  <td className="p-2 flex gap-2">
                    <button className="text-blue-400 hover:text-blue-300 p-1"><Settings size={16} /></button>
                    {!p.active && <button className="text-green-400 hover:text-green-300 p-1" title="Activate"><PlayCircle size={16} /></button>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'editor' && (
        <div className="grid grid-cols-2 gap-6">
          <div className="bg-gray-900 border border-gray-800 rounded p-6">
            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2"><Sliders size={20} /> Weight Configuration</h2>
            
            <div className="space-y-6">
              <div>
                <label className="flex justify-between text-sm font-medium mb-2 text-gray-300">
                  <span>Technical Intelligence</span>
                  <span className="text-blue-400">25%</span>
                </label>
                <input type="range" min="0" max="100" defaultValue="25" className="w-full accent-blue-500" />
              </div>
              <div>
                <label className="flex justify-between text-sm font-medium mb-2 text-gray-300">
                  <span>Valuation Intelligence</span>
                  <span className="text-blue-400">25%</span>
                </label>
                <input type="range" min="0" max="100" defaultValue="25" className="w-full accent-blue-500" />
              </div>
              <div>
                <label className="flex justify-between text-sm font-medium mb-2 text-gray-300">
                  <span>Portfolio Context Penalty</span>
                  <span className="text-blue-400">25%</span>
                </label>
                <input type="range" min="0" max="100" defaultValue="25" className="w-full accent-blue-500" />
              </div>
              <div>
                <label className="flex justify-between text-sm font-medium mb-2 text-gray-300">
                  <span>Risk Metrics (Vol/Beta)</span>
                  <span className="text-blue-400">25%</span>
                </label>
                <input type="range" min="0" max="100" defaultValue="25" className="w-full accent-blue-500" />
              </div>
            </div>
            
            <div className="mt-8 flex justify-end">
               <button className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded font-semibold flex items-center gap-2 transition-colors">
                  <Save size={16} /> Save as v1.1
               </button>
            </div>
          </div>
          
          <div className="bg-gray-900 border border-gray-800 rounded p-6">
            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2"><Settings size={20} /> Methodologies</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-400">Target Price Methodology</label>
                <select className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-white">
                  <option>Risk/Reward Dynamic Spread</option>
                  <option>ATR Projection (1.5x)</option>
                  <option>Historical Valuation Fair Price</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-400">Stop Loss Methodology</label>
                <select className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-white">
                  <option>Percentage (Fixed 10%)</option>
                  <option>ATR Multiplier (2.0x)</option>
                  <option>Trailing Stop (15%)</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {activeTab === 'audit' && (
        <div className="bg-gray-900 border border-gray-800 rounded p-4">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-gray-700 text-gray-400 text-sm">
                <th className="p-2">Timestamp</th>
                <th className="p-2">Symbol</th>
                <th className="p-2">Policy Traced</th>
                <th className="p-2">Decision</th>
                <th className="p-2">Action</th>
              </tr>
            </thead>
            <tbody>
              {auditLogs.map(log => (
                <tr key={log.id} className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors">
                  <td className="p-2 text-sm text-gray-400 flex items-center gap-2"><Clock size={14} /> {log.time}</td>
                  <td className="p-2 font-medium">{log.symbol}</td>
                  <td className="p-2 text-sm">{log.policy}</td>
                  <td className="p-2">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      log.decision.includes('Buy') ? 'bg-green-900 text-green-400' :
                      log.decision.includes('Sell') || log.decision.includes('Trim') ? 'bg-red-900 text-red-400' :
                      'bg-gray-700 text-gray-300'
                    }`}>
                      {log.decision}
                    </span>
                  </td>
                  <td className="p-2">
                    <button className="text-blue-400 hover:text-blue-300 text-sm font-semibold">View JSON Log</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default PolicyAdminWorkspace;
