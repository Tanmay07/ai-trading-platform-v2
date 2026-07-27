import React from 'react';
import GlassCard from '../GlassCard';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Target, TrendingUp, AlertTriangle } from 'lucide-react';

const PerformanceTab = ({ portfolioId }) => {
  // Mock performance data since the backend doesn't have historical time-series endpoints yet.
  const monthlyData = [
    { name: 'Jan', 'Portfolio Return': 2.4, 'Benchmark (NIFTY50)': 1.8 },
    { name: 'Feb', 'Portfolio Return': -1.2, 'Benchmark (NIFTY50)': -2.1 },
    { name: 'Mar', 'Portfolio Return': 3.1, 'Benchmark (NIFTY50)': 2.5 },
    { name: 'Apr', 'Portfolio Return': 1.5, 'Benchmark (NIFTY50)': 1.0 },
    { name: 'May', 'Portfolio Return': 4.2, 'Benchmark (NIFTY50)': 3.5 },
    { name: 'Jun', 'Portfolio Return': 2.1, 'Benchmark (NIFTY50)': 1.9 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold text-white">Performance Analytics</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <GlassCard className="flex flex-col items-center justify-center p-6 text-center">
          <TrendingUp className="w-8 h-8 text-green-400 mb-2" />
          <h3 className="text-gray-400 text-sm font-medium">Alpha Generated</h3>
          <p className="text-2xl font-bold text-white mt-1">+2.45%</p>
          <p className="text-xs text-gray-500 mt-2">vs NIFTY50 (YTD)</p>
        </GlassCard>
        
        <GlassCard className="flex flex-col items-center justify-center p-6 text-center">
          <Target className="w-8 h-8 text-blue-400 mb-2" />
          <h3 className="text-gray-400 text-sm font-medium">Sharpe Ratio</h3>
          <p className="text-2xl font-bold text-white mt-1">1.82</p>
          <p className="text-xs text-gray-500 mt-2">Risk-adjusted return</p>
        </GlassCard>

        <GlassCard className="flex flex-col items-center justify-center p-6 text-center">
          <AlertTriangle className="w-8 h-8 text-orange-400 mb-2" />
          <h3 className="text-gray-400 text-sm font-medium">Max Drawdown</h3>
          <p className="text-2xl font-bold text-white mt-1">-8.4%</p>
          <p className="text-xs text-gray-500 mt-2">Peak to trough decline</p>
        </GlassCard>
      </div>

      <GlassCard title="Monthly Return vs Benchmark">
        <div className="h-80 w-full mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={monthlyData}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
              <XAxis dataKey="name" stroke="#6b7280" tick={{fill: '#6b7280', fontSize: 12}} />
              <YAxis 
                stroke="#6b7280" 
                tick={{fill: '#6b7280', fontSize: 12}}
                tickFormatter={(val) => `${val}%`}
              />
              <Tooltip 
                contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', color: '#fff' }}
                itemStyle={{ color: '#fff' }}
                cursor={{ fill: '#1f2937', opacity: 0.4 }}
              />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Bar dataKey="Portfolio Return" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Benchmark (NIFTY50)" fill="#4b5563" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </GlassCard>
    </div>
  );
};

export default PerformanceTab;
