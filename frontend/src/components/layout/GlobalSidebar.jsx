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
    <div className="w-64 bg-bg-surface-elevated/40 backdrop-blur-2xl border-r border-glass-border flex flex-col h-screen shrink-0 hidden md:flex relative z-10">
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-glass-border">
        <div className="w-8 h-8 rounded bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-primary-500/20 mr-3">
          PF
        </div>
        <span className="font-semibold text-lg text-white tracking-wide">PFOS</span>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar py-6">
        <nav className="px-4 space-y-2">
          {primaryNav.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `
                flex items-center gap-3 px-4 py-3 rounded-xl text-sm transition-all duration-300 relative group
                ${isActive 
                  ? 'bg-gradient-to-r from-primary-500/20 to-transparent text-white font-semibold shadow-inner' 
                  : 'text-gray-400 hover:text-gray-100 hover:bg-white/5'
                }
              `}
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-primary-500 rounded-r-full shadow-[0_0_12px_rgba(99,102,241,0.8)]" />
                  )}
                  {item.icon}
                  {item.label}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {isAdmin && (
          <div className="mt-8">
            <div className="px-7 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Administration
            </div>
            <nav className="px-4 space-y-2">
              {adminNav.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) => `
                    flex items-center gap-3 px-4 py-3 rounded-xl text-sm transition-all duration-300 relative group
                    ${isActive 
                      ? 'bg-gradient-to-r from-indigo-500/20 to-transparent text-white font-semibold shadow-inner' 
                      : 'text-gray-400 hover:text-gray-100 hover:bg-white/5'
                    }
                  `}
                >
                  {({ isActive }) => (
                    <>
                      {isActive && (
                        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-indigo-500 rounded-r-full shadow-[0_0_12px_rgba(99,102,241,0.8)]" />
                      )}
                      {item.icon}
                      {item.label}
                    </>
                  )}
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
