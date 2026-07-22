import React from 'react';
import { Search, Bell, Sun, Moon, Sparkles } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { useUIStore } from '../../store/uiStore';

const GlobalHeader = () => {
  const { userProfile, toggleAdmin, isAdmin } = useAuthStore();
  const { toggleCommandPalette } = useUIStore();

  return (
    <header className="h-16 bg-bg-surface/80 backdrop-blur-md border-b border-glass-border flex items-center justify-between px-6 sticky top-0 z-40">
      <div className="flex-1 flex items-center">
        {/* Universal Search Trigger */}
        <button 
          onClick={toggleCommandPalette}
          className="flex items-center gap-2 px-4 py-2 bg-dark-800 border border-dark-700 rounded-lg text-sm text-gray-400 hover:text-gray-200 hover:border-dark-600 transition-colors w-64"
        >
          <Search className="w-4 h-4" />
          <span>Search workspaces...</span>
          <div className="ml-auto flex items-center gap-1 opacity-60">
            <kbd className="font-mono text-xs bg-dark-700 px-1.5 py-0.5 rounded">Ctrl</kbd>
            <kbd className="font-mono text-xs bg-dark-700 px-1.5 py-0.5 rounded">K</kbd>
          </div>
        </button>
      </div>

      <div className="flex items-center gap-4">
        {/* Market Status Mock */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-xs font-medium text-emerald-400">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
          Markets Open
        </div>

        {/* AI Assistant Hook */}
        <button className="p-2 text-gray-400 hover:text-primary-400 transition-colors relative group">
          <Sparkles className="w-5 h-5" />
          <div className="absolute top-0 right-0 w-2 h-2 rounded-full bg-primary-500 border border-bg-surface"></div>
        </button>

        {/* Notifications */}
        <button className="p-2 text-gray-400 hover:text-gray-200 transition-colors relative">
          <Bell className="w-5 h-5" />
          <div className="absolute top-1 right-1 w-2 h-2 rounded-full bg-red-500 border border-bg-surface"></div>
        </button>

        <div className="w-px h-6 bg-glass-border mx-2"></div>

        {/* Profile / Admin Toggle Mock */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:block text-right">
            <p className="text-sm font-medium text-white leading-none">{userProfile.name}</p>
            <p className="text-xs text-gray-400 mt-1">{userProfile.role}</p>
          </div>
          <button onClick={toggleAdmin} className="relative rounded-full overflow-hidden w-8 h-8 ring-2 ring-transparent hover:ring-primary-500/50 transition-all cursor-pointer" title="Toggle Admin Role">
            <img src={userProfile.avatar} alt="Profile" className="w-full h-full object-cover" />
            {isAdmin && (
              <div className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-indigo-500 border border-bg-surface rounded-full"></div>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};

export default GlobalHeader;
