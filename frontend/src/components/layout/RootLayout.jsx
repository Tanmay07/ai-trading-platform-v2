import React from 'react';
import GlobalSidebar from './GlobalSidebar';
import GlobalHeader from './GlobalHeader';
import ContextPanel from './ContextPanel';
import CommandPalette from '../ui/CommandPalette';
import { Outlet } from 'react-router-dom';

const RootLayout = () => {
  return (
    <div className="flex h-screen overflow-hidden bg-bg-base text-text-primary">
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
