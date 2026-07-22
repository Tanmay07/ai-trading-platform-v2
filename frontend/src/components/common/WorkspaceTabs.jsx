import React from 'react';

const WorkspaceTabs = ({ tabs, activeTab, onTabChange }) => {
  return (
    <div className="flex border-b border-dark-700/50 mb-6 overflow-x-auto custom-scrollbar">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={`px-6 py-3 font-medium text-sm transition-colors whitespace-nowrap relative
            ${activeTab === tab.id ? 'text-primary-400' : 'text-gray-400 hover:text-gray-200'}
          `}
        >
          {tab.label}
          {activeTab === tab.id && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500 rounded-t-full shadow-[0_0_8px_rgba(56,189,248,0.5)]" />
          )}
        </button>
      ))}
    </div>
  );
};

export default WorkspaceTabs;
