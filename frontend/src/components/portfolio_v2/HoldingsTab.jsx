import React, { useEffect, useState } from 'react';
import { getPortfolioHoldings } from '../../services/portfolioV2Api';
import GlassCard from '../GlassCard';
import { TrendingUp, TrendingDown, RefreshCw, Edit2, Trash2, Plus } from 'lucide-react';

const HoldingsTab = ({ portfolioId }) => {
  const [holdings, setHoldings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortField, setSortField] = useState('portfolio_weight');
  const [sortOrder, setSortOrder] = useState('desc');

  const fetchHoldings = async () => {
    try {
      setLoading(true);
      setError(null);
      if (portfolioId) {
        const data = await getPortfolioHoldings(portfolioId);
        setHoldings(data);
      }
    } catch (err) {
      setError(err.message || 'Failed to load holdings');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHoldings();
  }, [portfolioId]);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const handleAction = (action, symbol) => {
    alert(`${action} action for ${symbol || 'new holding'} coming soon!`);
  };

  const sortedHoldings = [...holdings].sort((a, b) => {
    const aVal = a[sortField] || 0;
    const bVal = b[sortField] || 0;
    if (typeof aVal === 'string') {
      return sortOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    }
    return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
  });

  const formatCurrency = (val) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(val || 0);
  const formatPct = (val) => `${(val || 0).toFixed(2)}%`;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold text-white">Current Holdings</h2>
        <div className="flex items-center gap-3">
          <button 
            onClick={() => handleAction('Add')}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors text-sm font-medium shadow-lg"
          >
            <Plus className="w-4 h-4" />
            Add Holding
          </button>
          <button 
            onClick={fetchHoldings} 
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg transition-colors text-sm font-medium disabled:opacity-50 border border-gray-700"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-900/30 border border-red-500/50 rounded-lg text-red-400">
          {error}
        </div>
      )}

      <GlassCard className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-300">
            <thead className="bg-gray-800/50 text-gray-400 uppercase text-xs">
              <tr>
                <th className="px-4 py-3 cursor-pointer hover:text-white transition-colors" onClick={() => handleSort('symbol')}>Symbol</th>
                <th className="px-4 py-3 cursor-pointer hover:text-white transition-colors" onClick={() => handleSort('quantity')}>Quantity</th>
                <th className="px-4 py-3 cursor-pointer hover:text-white transition-colors" onClick={() => handleSort('average_buy_price')}>Avg Price</th>
                <th className="px-4 py-3 cursor-pointer hover:text-white transition-colors" onClick={() => handleSort('current_price')}>LTP</th>
                <th className="px-4 py-3 cursor-pointer hover:text-white transition-colors text-right" onClick={() => handleSort('total_invested')}>Invested</th>
                <th className="px-4 py-3 cursor-pointer hover:text-white transition-colors text-right" onClick={() => handleSort('current_value')}>Current Value</th>
                <th className="px-4 py-3 cursor-pointer hover:text-white transition-colors text-right" onClick={() => handleSort('unrealized_pnl')}>P&L</th>
                <th className="px-4 py-3 cursor-pointer hover:text-white transition-colors text-right" onClick={() => handleSort('portfolio_weight')}>Weight</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/50">
              {loading && holdings.length === 0 ? (
                <tr>
                  <td colSpan="9" className="px-4 py-8 text-center text-gray-500 animate-pulse">Loading holdings...</td>
                </tr>
              ) : sortedHoldings.length === 0 ? (
                <tr>
                  <td colSpan="9" className="px-4 py-8 text-center text-gray-500">No holdings found in this portfolio.</td>
                </tr>
              ) : (
                sortedHoldings.map((holding) => {
                  const isPositive = holding.unrealized_pnl >= 0;
                  return (
                    <tr key={holding.symbol} className="hover:bg-gray-800/30 transition-colors group">
                      <td className="px-4 py-3 font-medium text-white">{holding.symbol}</td>
                      <td className="px-4 py-3">{holding.quantity}</td>
                      <td className="px-4 py-3">{formatCurrency(holding.average_buy_price)}</td>
                      <td className="px-4 py-3">{formatCurrency(holding.current_price)}</td>
                      <td className="px-4 py-3 text-right text-gray-400">{formatCurrency(holding.total_invested)}</td>
                      <td className="px-4 py-3 text-right font-medium">{formatCurrency(holding.current_value)}</td>
                      <td className={`px-4 py-3 text-right font-medium flex items-center justify-end gap-1 ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                        {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                        {formatCurrency(holding.unrealized_pnl)}
                        <span className="text-xs ml-1 opacity-70">({formatPct(holding.unrealized_pct)})</span>
                      </td>
                      <td className="px-4 py-3 text-right text-purple-400 font-medium">{formatPct(holding.portfolio_weight)}</td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button 
                            onClick={() => handleAction('Edit', holding.symbol)}
                            className="p-1.5 text-blue-400 hover:text-blue-300 hover:bg-blue-400/10 rounded transition-colors"
                            title="Edit Holding"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button 
                            onClick={() => handleAction('Delete', holding.symbol)}
                            className="p-1.5 text-red-400 hover:text-red-300 hover:bg-red-400/10 rounded transition-colors"
                            title="Delete Holding"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
};

export default HoldingsTab;
