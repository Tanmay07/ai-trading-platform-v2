import React from 'react';
import { useUIStore } from '../../store/uiStore';
import { X, Sparkles } from 'lucide-react';

const ContextPanel = () => {
  const { isContextPanelOpen, closeContextPanel, contextPanelContent } = useUIStore();

  if (!isContextPanelOpen) return null;

  return (
    <div className="w-80 border-l border-glass-border bg-bg-surface-elevated/50 backdrop-blur-xl shrink-0 hidden lg:flex flex-col h-full animate-fade-in">
      <div className="h-16 border-b border-glass-border flex items-center justify-between px-4">
        <div className="flex items-center gap-2 text-primary-400">
          <Sparkles className="w-4 h-4" />
          <span className="font-semibold text-sm">AI Insights</span>
        </div>
        <button 
          onClick={closeContextPanel}
          className="p-1.5 text-gray-400 hover:text-white rounded-md hover:bg-dark-700 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto custom-scrollbar p-4">
        {contextPanelContent || (
          <div className="text-sm text-gray-400 flex flex-col items-center justify-center h-full text-center">
            <Sparkles className="w-8 h-8 opacity-20 mb-3" />
            <p>Select an item to view contextual AI intelligence.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ContextPanel;
