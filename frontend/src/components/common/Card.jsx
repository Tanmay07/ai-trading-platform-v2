import React from 'react';

export const Card = ({ children, className = '', noPadding = false }) => {
  return (
    <div className={`bg-dark-800/80 backdrop-blur-xl border border-dark-700/50 rounded-2xl ${noPadding ? '' : 'p-6'} ${className}`}>
      {children}
    </div>
  );
};

export const AICard = ({ title, children, icon, confidence }) => {
  return (
    <div className="bg-gradient-to-br from-dark-800 to-dark-900 border border-primary-500/30 rounded-2xl p-6 relative overflow-hidden group">
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary-600 to-indigo-500"></div>
      
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-3">
          {icon && <div className="text-primary-400 bg-primary-500/10 p-2 rounded-lg">{icon}</div>}
          <h3 className="font-semibold text-white">{title}</h3>
        </div>
        {confidence && (
          <div className="text-xs font-mono px-2 py-1 bg-emerald-500/10 text-emerald-400 rounded-md border border-emerald-500/20">
            {confidence}% CONF
          </div>
        )}
      </div>
      
      <div className="text-gray-300">
        {children}
      </div>
    </div>
  );
};
