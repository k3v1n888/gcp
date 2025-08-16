/*
 * Copyright (c) 2025 Kevin Zachary
 * All rights reserved.
 *
 * This software and associated documentation files (the "Software") are the 
 * exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
 * modification, or use of this software is strictly prohibited.
 *
 * For licensing inquiries, contact: kevin@zachary.com
 */

/*
 * Author: Kevin Zachary
 * Copyright: Sentient Spire
 */



import React, { useState } from 'react';
import CyberSidebar from './CyberSidebar';

const CyberLayout = ({ children }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="cyber-layout flex h-screen bg-slate-900">
      <CyberSidebar 
        isCollapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />
      
      <div className={`
        flex-1 flex flex-col transition-all duration-300 ease-in-out
        ${sidebarCollapsed ? 'ml-16' : 'ml-64'}
      `}>
        {/* Main Content */}
        <main className="flex-1 overflow-y-auto bg-slate-900">
          {children}
        </main>
      </div>
    </div>
  );
};

export default CyberLayout;
