import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { 
  LayoutDashboard, LineChart, FlaskConical, Target, 
  Briefcase, ShieldCheck, Activity, Cpu, 
  Database, Settings, Gavel
} from 'lucide-react';

const GlobalSidebar = () => {
  const { isAdmin } = useAuthStore();

  const primaryNav = [
    { path: '/', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
    { path: '/markets', label: 'Markets', icon: <LineChart size={20} /> },
    { path: '/research', label: 'Research', icon: <FlaskConical size={20} /> },
    { path: '/committee', label: 'Investment Committee', icon: <Gavel size={20} /> },
    { path: '/portfolio', label: 'Portfolio', icon: <Briefcase size={20} /> },
    { path: '/paper-trading', label: 'Paper Trading', icon: <Target size={20} /> },
    { path: '/copilot', label: 'AI Copilot', icon: <Cpu size={20} /> },
  ];

  const adminNav = [
    { path: '/platform', label: 'Platform Operations', icon: <Settings size={20} /> },
    { path: '/ai-studio', label: 'AI Studio', icon: <Activity size={20} /> },
    { path: '/data-studio', label: 'Data Studio', icon: <Database size={20} /> },
    { path: '/governance', label: 'Governance', icon: <ShieldCheck size={20} /> },
  ];

  return (
    <div className="w-64 bg-bg-surface border-r border-glass-border flex flex-col h-screen shrink-0 hidden md:flex">
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-glass-border">
        <div className="w-8 h-8 rounded bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-primary-500/20 mr-3">
          PF
        </div>
        <span className="font-semibold text-lg text-white tracking-wide">PFOS</span>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar py-6">
        <nav className="px-4 space-y-1">
          {primaryNav.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `
                flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors
                ${isActive 
                  ? 'bg-primary-500/10 text-primary-400 font-medium' 
                  : 'text-gray-400 hover:text-gray-200 hover:bg-dark-700/50'
                }
              `}
            >
              {item.icon}
              {item.label}
            </NavLink>
          ))}
        </nav>

        {isAdmin && (
          <div className="mt-8">
            <div className="px-7 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Administration
            </div>
            <nav className="px-4 space-y-1">
              {adminNav.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) => `
                    flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors
                    ${isActive 
                      ? 'bg-indigo-500/10 text-indigo-400 font-medium' 
                      : 'text-gray-400 hover:text-gray-200 hover:bg-dark-700/50'
                    }
                  `}
                >
                  {item.icon}
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>
        )}
      </div>
      
      {/* User Profile Hook */}
      <div className="p-4 border-t border-glass-border">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-dark-700 flex items-center justify-center text-xs font-bold text-gray-300">
            AI
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">Connected</p>
            <p className="text-xs text-emerald-400 truncate">System Healthy</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GlobalSidebar;
