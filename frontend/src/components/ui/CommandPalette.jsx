import React, { useEffect } from 'react';
import { useUIStore } from '../../store/uiStore';
import { Search, X, Activity, Database, ShieldCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const CommandPalette = () => {
  const { isCommandPaletteOpen, setCommandPaletteOpen } = useUIStore();
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setCommandPaletteOpen(!isCommandPaletteOpen);
      }
      if (e.key === 'Escape' && isCommandPaletteOpen) {
        setCommandPaletteOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isCommandPaletteOpen, setCommandPaletteOpen]);

  if (!isCommandPaletteOpen) return null;

  const navigateTo = (path) => {
    setCommandPaletteOpen(false);
    navigate(path);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[10vh] px-4">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/60 backdrop-blur-sm"
        onClick={() => setCommandPaletteOpen(false)}
      />
      
      {/* Palette */}
      <div className="relative w-full max-w-2xl bg-dark-800 border border-dark-600 rounded-xl shadow-2xl overflow-hidden animate-fade-in">
        <div className="flex items-center px-4 border-b border-dark-700">
          <Search className="w-5 h-5 text-gray-400" />
          <input
            type="text"
            className="w-full bg-transparent border-none text-white px-4 py-4 focus:ring-0 focus:outline-none placeholder-gray-500"
            placeholder="Search stocks, models, datasets, commands..."
            autoFocus
          />
          <button 
            onClick={() => setCommandPaletteOpen(false)}
            className="p-1 hover:bg-dark-700 rounded-md text-gray-400"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-2 max-h-[60vh] overflow-y-auto">
          {/* Quick Actions */}
          <div className="px-2 py-1.5 text-xs font-semibold text-gray-500 uppercase tracking-wider">
            Quick Actions
          </div>
          <button onClick={() => navigateTo('/research')} className="w-full text-left px-4 py-3 hover:bg-primary-500/10 hover:text-primary-400 rounded-lg flex items-center gap-3 transition-colors text-gray-300">
            <Activity className="w-5 h-5 text-emerald-500" />
            <div>
              <div className="font-medium">Research Stock</div>
              <div className="text-xs text-gray-500">Open Alpha Research Lab</div>
            </div>
          </button>
          
          <button onClick={() => navigateTo('/portfolio')} className="w-full text-left px-4 py-3 hover:bg-primary-500/10 hover:text-primary-400 rounded-lg flex items-center gap-3 transition-colors text-gray-300">
            <Database className="w-5 h-5 text-indigo-500" />
            <div>
              <div className="font-medium">View Portfolio Risk</div>
              <div className="text-xs text-gray-500">Analyze current allocation</div>
            </div>
          </button>

          <button onClick={() => navigateTo('/ai-studio')} className="w-full text-left px-4 py-3 hover:bg-primary-500/10 hover:text-primary-400 rounded-lg flex items-center gap-3 transition-colors text-gray-300">
            <ShieldCheck className="w-5 h-5 text-primary-500" />
            <div>
              <div className="font-medium">Check Model Drift</div>
              <div className="text-xs text-gray-500">View Champion Model status</div>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default CommandPalette;
