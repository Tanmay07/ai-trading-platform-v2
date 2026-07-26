import React, { useState } from 'react';
import { Send, User, Sparkles, BrainCircuit, Activity, BarChart2, CheckCircle } from 'lucide-react';

const AICIOWorkspace = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Good morning. I am your AI Chief Investment Officer. I have reviewed your portfolio and today\'s market events. How can I assist you today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = () => {
    if (!input.trim()) return;
    
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    // Mock API call
    setTimeout(() => {
      const responseContent = input.toLowerCase().includes('summarize') 
        ? "The portfolio currently holds 12 positions with a total value of ₹15,40,000. Your largest holding is HDFCBANK. Based on the allocation, you are heavily overweight in the Financials sector. From a market perspective, today's market is driven by 2 key events, notably an RBI policy update."
        : "I have analyzed your request based on current market conditions and your portfolio constraints. Please review the Daily Briefing for more context.";
        
      setMessages(prev => [...prev, { role: 'assistant', content: responseContent }]);
      setLoading(false);
    }, 1500);
  };

  return (
    <div className="h-full flex bg-[#0B0E14] text-white overflow-hidden animate-fade-in">
      
      {/* Left Sidebar - Briefings & Health */}
      <div className="w-1/3 border-r border-gray-800 p-6 flex flex-col gap-6 overflow-y-auto">
        <div>
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <BrainCircuit className="text-purple-400" /> AI-CIO Overview
          </h2>
          <div className="bg-purple-900/20 border border-purple-900 rounded p-4 text-sm text-purple-200">
            <h3 className="font-semibold text-purple-300 mb-2">Morning Briefing</h3>
            <p className="mb-2">Your portfolio is heavily skewed towards Financials. Cash reserve is currently at 12%.</p>
            <p>The NIFTY 50 gap-opened lower due to global macroeconomic pressures, specifically the US Fed rate commentary overnight.</p>
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">Action Items</h3>
          <ul className="space-y-2">
            <li className="flex items-start gap-2 text-sm text-gray-300">
              <CheckCircle size={16} className="text-yellow-500 mt-0.5" /> Review HDFCBANK exposure due to RBI policy.
            </li>
            <li className="flex items-start gap-2 text-sm text-gray-300">
              <CheckCircle size={16} className="text-green-500 mt-0.5" /> Consider increasing IT sector allocation on TCS earnings beat.
            </li>
          </ul>
        </div>
        
        <div>
          <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">Suggested Queries</h3>
          <div className="flex flex-col gap-2">
            <button onClick={() => setInput("Summarize my portfolio.")} className="text-left text-sm bg-gray-900 border border-gray-800 p-2 rounded hover:bg-gray-800 transition-colors">
              "Summarize my portfolio."
            </button>
            <button onClick={() => setInput("Which holdings have the highest conviction?")} className="text-left text-sm bg-gray-900 border border-gray-800 p-2 rounded hover:bg-gray-800 transition-colors">
              "Which holdings have the highest conviction?"
            </button>
          </div>
        </div>
      </div>

      {/* Right Side - Chat Interface */}
      <div className="flex-1 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center flex-shrink-0">
                  <Sparkles size={16} />
                </div>
              )}
              
              <div className={`max-w-[80%] rounded-lg p-4 ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-900 border border-gray-800 text-gray-200'
              }`}>
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>

              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-blue-800 flex items-center justify-center flex-shrink-0">
                  <User size={16} />
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex gap-4 justify-start">
              <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center animate-pulse">
                <Sparkles size={16} />
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 text-gray-400">
                Synthesizing insights from agents...
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 bg-gray-900 border-t border-gray-800">
          <div className="relative flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask your AI-CIO (e.g., 'What if the market falls 10%?')"
              className="w-full bg-black border border-gray-700 rounded-lg py-3 pl-4 pr-12 text-white focus:outline-none focus:border-purple-500 transition-colors"
            />
            <button 
              onClick={handleSend}
              disabled={!input.trim() || loading}
              className="absolute right-2 p-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50 transition-colors"
            >
              <Send size={18} />
            </button>
          </div>
          <p className="text-center text-xs text-gray-500 mt-2">
            AI-CIO uses a multi-agent architecture. Responses are grounded in live portfolio and event data.
          </p>
        </div>
      </div>

    </div>
  );
};

export default AICIOWorkspace;
