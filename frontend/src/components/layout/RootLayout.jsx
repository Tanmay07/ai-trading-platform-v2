import React from 'react';
import GlobalSidebar from './GlobalSidebar';
import GlobalHeader from './GlobalHeader';
import ContextPanel from './ContextPanel';
import CommandPalette from '../ui/CommandPalette';
import { Outlet } from 'react-router-dom';

const RootLayout = () => {
  return (
    <div className="flex h-screen overflow-hidden bg-[#050505] text-text-primary relative selection:bg-primary-500/30 selection:text-white">
      {/* Background Ambient Glows */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-indigo-500/10 blur-[120px] pointer-events-none mix-blend-screen"></div>
      <div className="absolute bottom-[-10%] right-[-5%] w-[30%] h-[40%] rounded-full bg-cyan-500/10 blur-[120px] pointer-events-none mix-blend-screen"></div>
      
      {/* 1. Left Sidebar */}
      <GlobalSidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        {/* 2. Top Header */}
        <GlobalHeader />

        {/* Workspace Container */}
        <div className="flex-1 flex overflow-hidden">
          {/* 3. Main Workspace Area */}
          <main className="flex-1 overflow-y-auto custom-scrollbar p-6">
            <Outlet />
          </main>

          {/* 4. Right Context Panel */}
          <ContextPanel />
        </div>
      </div>

      {/* Global Modals */}
      <CommandPalette />
    </div>
  );
};

export default RootLayout;
