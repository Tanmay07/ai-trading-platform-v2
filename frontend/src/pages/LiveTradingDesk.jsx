import React, { useState, useEffect } from 'react';
import { 
  Activity, DollarSign, ShieldCheck, PlayCircle, StopCircle, 
  CheckCircle, XCircle, Clock, Check
} from 'lucide-react';
import api from '../services/api';

const LiveTradingDesk = () => {
  const [portfolio, setPortfolio] = useState(null);
  const [orders, setOrders] = useState([]);
  const [broker, setBroker] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTradingData();
    const interval = setInterval(fetchTradingData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchTradingData = async () => {
    try {
      const [portfolioRes, ordersRes, brokerRes] = await Promise.all([
        api.get('/trading/portfolio'),
        api.get('/trading/orders'),
        api.get('/trading/broker/status')
      ]);
      setPortfolio(portfolioRes.data);
      setOrders(ordersRes.data);
      setBroker(brokerRes.data);
      setError(null);
    } catch (err) {
      console.error("Error fetching trading data:", err);
      setError("Failed to fetch live trading data. Is the execution engine running?");
    } finally {
      setLoading(false);
    }
  };

  const approveOrder = async (orderId) => {
    try {
      await api.post('/trading/execute/approve', { order_id: orderId });
      fetchTradingData();
    } catch (err) {
      alert("Failed to execute order.");
    }
  };

  const executeMockSignal = async () => {
    try {
      await api.post('/trading/execute/signal', {
        symbol: "RELIANCE",
        action: "BUY",
        confidence: 0.92,
        current_price: 2950.0
      });
      fetchTradingData();
    } catch (err) {
      alert("Error sending mock signal");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-fade-in pb-20">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Live Trading Desk</h1>
          <p className="text-gray-400">Phase 5: Execution Engine & OMS</p>
        </div>
        
        <div className="flex gap-4 items-center">
          <div className="bg-dark-800 border border-dark-700 rounded-xl p-4 flex items-center gap-3">
            <div className={`p-2 rounded-lg ${broker?.broker === 'PAPER_TRADING' ? 'bg-indigo-500/20 text-indigo-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase font-semibold">Active Broker</p>
              <p className="text-white font-medium">{broker?.broker || 'DISCONNECTED'}</p>
            </div>
          </div>
          
          <button 
            onClick={executeMockSignal}
            className="btn-primary py-3 px-5 flex items-center gap-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 border-none shadow-lg shadow-emerald-500/20 transition-all active:scale-95"
          >
            <PlayCircle className="w-5 h-5" />
            Inject AI Signal
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/50 text-red-400 p-4 rounded-xl flex items-center gap-3">
          <XCircle className="w-5 h-5 flex-shrink-0" />
          <p>{error}</p>
        </div>
      )}

      {/* Overview Cards */}
      {portfolio && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card bg-dark-800/80 backdrop-blur-xl border border-dark-700/50 rounded-2xl p-6 relative overflow-hidden group hover:border-primary-500/50 transition-all duration-300">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <DollarSign className="w-24 h-24 text-primary-500" />
            </div>
            <div className="relative z-10">
              <div className="flex items-center gap-2 mb-2 text-gray-400">
                <p className="text-sm font-semibold uppercase tracking-wider">Available Margin</p>
              </div>
              <h3 className="text-4xl font-bold text-white font-mono">
                ₹{portfolio.margins.available.toLocaleString(undefined, {minimumFractionDigits: 2})}
              </h3>
            </div>
          </div>
          
          <div className="card bg-dark-800/80 backdrop-blur-xl border border-dark-700/50 rounded-2xl p-6 relative overflow-hidden group hover:border-emerald-500/50 transition-all duration-300">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Activity className="w-24 h-24 text-emerald-500" />
            </div>
            <div className="relative z-10">
              <div className="flex items-center gap-2 mb-2 text-gray-400">
                <p className="text-sm font-semibold uppercase tracking-wider">Live PnL</p>
              </div>
              <h3 className={`text-4xl font-bold font-mono ${portfolio.total_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {portfolio.total_pnl >= 0 ? '+' : '-'}₹{Math.abs(portfolio.total_pnl).toLocaleString(undefined, {minimumFractionDigits: 2})}
              </h3>
            </div>
          </div>

          <div className="card bg-dark-800/80 backdrop-blur-xl border border-dark-700/50 rounded-2xl p-6 relative overflow-hidden group hover:border-indigo-500/50 transition-all duration-300">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <ShieldCheck className="w-24 h-24 text-indigo-500" />
            </div>
            <div className="relative z-10">
              <div className="flex items-center gap-2 mb-2 text-gray-400">
                <p className="text-sm font-semibold uppercase tracking-wider">Total Investment</p>
              </div>
              <h3 className="text-4xl font-bold text-white font-mono">
                ₹{portfolio.total_investment.toLocaleString(undefined, {minimumFractionDigits: 2})}
              </h3>
            </div>
          </div>
        </div>
      )}

      {/* Grid: Orders & Positions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Positions Table */}
        <div className="card bg-dark-800 border border-dark-700 rounded-2xl p-6 flex flex-col h-full shadow-lg">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <Activity className="w-5 h-5 text-emerald-400" />
            Active Positions
          </h2>
          
          <div className="overflow-x-auto flex-grow">
            {portfolio?.positions?.length > 0 ? (
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-dark-600 text-sm font-medium text-gray-400 uppercase tracking-wider">
                    <th className="pb-3 px-4 font-semibold">Symbol</th>
                    <th className="pb-3 px-4 font-semibold">Qty</th>
                    <th className="pb-3 px-4 font-semibold">Avg Price</th>
                    <th className="pb-3 px-4 font-semibold">Live PnL</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-dark-700">
                  {portfolio.positions.map((pos, idx) => (
                    <tr key={idx} className="hover:bg-dark-700/30 transition-colors group">
                      <td className="py-4 px-4 font-semibold text-white">{pos.symbol}</td>
                      <td className="py-4 px-4 text-gray-300 font-mono">{pos.quantity}</td>
                      <td className="py-4 px-4 text-gray-300 font-mono">₹{pos.avg_price.toFixed(2)}</td>
                      <td className="py-4 px-4">
                        <span className={`px-2 py-1 rounded-md font-mono text-sm ${pos.pnl >= 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
                          {pos.pnl >= 0 ? '+' : '-'}₹{Math.abs(pos.pnl).toFixed(2)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-gray-500 py-12">
                <StopCircle className="w-12 h-12 mb-3 opacity-20" />
                <p>No active positions.</p>
              </div>
            )}
          </div>
        </div>

        {/* Order Book */}
        <div className="card bg-dark-800 border border-dark-700 rounded-2xl p-6 flex flex-col h-full shadow-lg">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <Clock className="w-5 h-5 text-indigo-400" />
            Order Book
          </h2>
          
          <div className="overflow-x-auto flex-grow max-h-[500px] overflow-y-auto custom-scrollbar">
            {orders?.length > 0 ? (
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-dark-600 text-sm font-medium text-gray-400 uppercase tracking-wider sticky top-0 bg-dark-800">
                    <th className="pb-3 px-4 font-semibold">Time</th>
                    <th className="pb-3 px-4 font-semibold">Order</th>
                    <th className="pb-3 px-4 font-semibold">Status</th>
                    <th className="pb-3 px-4 font-semibold">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-dark-700">
                  {orders.map((order, idx) => (
                    <tr key={order.id || idx} className="hover:bg-dark-700/30 transition-colors group">
                      <td className="py-4 px-4 text-xs text-gray-500 font-mono">
                        {new Date(order.timestamp).toLocaleTimeString()}
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${order.side === 'BUY' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                            {order.side}
                          </span>
                          <span className="font-semibold text-white">{order.quantity} {order.symbol}</span>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        {order.status === 'COMPLETED' && <span className="flex items-center gap-1 text-xs text-emerald-400"><CheckCircle className="w-3 h-3"/> Executed</span>}
                        {order.status === 'REJECTED' && <span className="flex items-center gap-1 text-xs text-red-400"><XCircle className="w-3 h-3"/> Rejected</span>}
                        {order.status === 'PENDING_APPROVAL' && <span className="flex items-center gap-1 text-xs text-amber-400"><Clock className="w-3 h-3"/> Action Required</span>}
                      </td>
                      <td className="py-4 px-4">
                        {order.status === 'PENDING_APPROVAL' && (
                          <button 
                            onClick={() => approveOrder(order.id)}
                            className="bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 p-1.5 rounded transition-colors"
                            title="Execute Order"
                          >
                            <Check className="w-4 h-4" />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-gray-500 py-12">
                <StopCircle className="w-12 h-12 mb-3 opacity-20" />
                <p>No orders today.</p>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default LiveTradingDesk;
