import React from 'react';

const WorkspaceTabs = ({ tabs, activeTab, onTabChange }) => {
  return (
    <div className="flex gap-2 border-b border-glass-border/40 mb-8 pb-1 overflow-x-auto custom-scrollbar relative z-10">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={`px-6 py-2.5 rounded-lg font-medium text-sm transition-all duration-300 whitespace-nowrap relative group border border-transparent
            ${activeTab === tab.id 
              ? 'bg-glass-border/10 text-primary-400 border-glass-border/30 shadow-[0_4px_12px_rgba(0,0,0,0.5)]' 
              : 'text-gray-400 hover:text-white hover:bg-glass-border/5'
            }
          `}
        >
          {tab.label}
          
          {/* Hover highlight */}
          <div className="absolute inset-0 bg-primary-500/5 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg"></div>
        </button>
      ))}
    </div>
  );
};

export default WorkspaceTabs;
