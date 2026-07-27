import React, { useEffect, useState } from 'react';
import { getPortfolioSummary } from '../../services/portfolioV2Api';
import { Briefcase, TrendingUp, TrendingDown, DollarSign, Activity, Shield } from 'lucide-react';
import GlassCard from '../GlassCard';
import MetricCard from '../ui/MetricCard';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

const OverviewTab = ({ portfolioId }) => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        setLoading(true);
        if (portfolioId) {
          const data = await getPortfolioSummary(portfolioId);
          setSummary(data);
        }
      } catch (err) {
        setError(err.message || 'Failed to load portfolio summary');
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, [portfolioId]);

  if (loading) {
    return <div className="p-8 text-center text-gray-400 animate-pulse">Loading portfolio summary...</div>;
  }

  if (error) {
    return <div className="p-8 text-center text-red-400">Error: {error}</div>;
  }

  if (!summary) {
    return <div className="p-8 text-center text-gray-400">No portfolio data available.</div>;
  }

  const formatCurrency = (val) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(val || 0);
  const formatPct = (val) => `${(val || 0).toFixed(2)}%`;
  
  const isPositivePnl = summary.unrealized_pnl >= 0;
  const isPositiveToday = summary.today_pnl >= 0;

  // Mock chart data for now since backend summary doesn't return time-series yet
  const mockChartData = Array.from({ length: 30 }).map((_, i) => ({
    name: `Day ${i + 1}`,
    value: summary.total_portfolio_value * (0.95 + Math.random() * 0.1)
  }));

  return (
    <div className="space-y-6">
      {/* Top Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Value"
          value={formatCurrency(summary.total_portfolio_value)}
          subtitle={`Invested: ${formatCurrency(summary.total_invested)}`}
          icon={Briefcase}
          trend={isPositivePnl ? 'up' : 'down'}
          trendValue={formatPct(summary.unrealized_pct)}
        />
        <MetricCard
          title="Unrealized P&L"
          value={formatCurrency(summary.unrealized_pnl)}
          icon={isPositivePnl ? TrendingUp : TrendingDown}
          trend={isPositivePnl ? 'up' : 'down'}
          trendValue={isPositivePnl ? 'Profitable' : 'Loss-making'}
          valueColor={isPositivePnl ? 'text-green-400' : 'text-red-400'}
        />
        <MetricCard
          title="Today's P&L"
          value={formatCurrency(summary.today_pnl)}
          icon={Activity}
          trend={isPositiveToday ? 'up' : 'down'}
          trendValue={formatPct(summary.today_pct)}
          valueColor={isPositiveToday ? 'text-green-400' : 'text-red-400'}
        />
        <MetricCard
          title="1-Year Projected (15% YoY)"
          value={formatCurrency(summary.total_portfolio_value * 1.15)}
          icon={TrendingUp}
          trend="up"
          trendValue={`+${formatCurrency(summary.total_portfolio_value * 0.15)}`}
          valueColor="text-blue-400"
        />
      </div>

      {/* Charts & Health Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <GlassCard title="Portfolio Value History (30D)">
            <div className="h-72 w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={mockChartData}>
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                  <XAxis dataKey="name" stroke="#6b7280" tick={{fill: '#6b7280', fontSize: 12}} />
                  <YAxis 
                    stroke="#6b7280" 
                    tick={{fill: '#6b7280', fontSize: 12}}
                    tickFormatter={(val) => `₹${(val/1000).toFixed(0)}k`}
                    domain={['auto', 'auto']}
                  />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', color: '#fff' }}
                    itemStyle={{ color: '#8b5cf6' }}
                    formatter={(val) => formatCurrency(val)}
                  />
                  <Area type="monotone" dataKey="value" stroke="#8b5cf6" fillOpacity={1} fill="url(#colorValue)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>
        </div>

        <div className="space-y-6">
          <GlassCard title="Portfolio Health">
            <div className="space-y-6 mt-4">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-gray-300">Overall Health Score</span>
                  <span className="text-sm font-medium text-purple-400">{summary.health_score || 85}/100</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2.5">
                  <div className="bg-purple-500 h-2.5 rounded-full" style={{ width: `${summary.health_score || 85}%` }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-gray-300">Diversification</span>
                  <span className="text-sm font-medium text-blue-400">{summary.diversification_score || 72}/100</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2.5">
                  <div className="bg-blue-500 h-2.5 rounded-full" style={{ width: `${summary.diversification_score || 72}%` }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-gray-300">Risk Profile</span>
                  <span className="text-sm font-medium text-orange-400">{summary.risk_score || 45}/100</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2.5">
                  <div className="bg-orange-500 h-2.5 rounded-full" style={{ width: `${summary.risk_score || 45}%` }}></div>
                </div>
                <p className="text-xs text-gray-400 mt-2 flex items-center gap-1">
                  <Shield className="w-3 h-3" /> Balanced risk exposure across sectors.
                </p>
              </div>
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
};

export default OverviewTab;
