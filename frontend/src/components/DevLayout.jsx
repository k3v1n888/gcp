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



// Development-aware Layout component
import React, { useState } from 'react';
import { Link, Outlet } from 'react-router-dom';
import { useDevUser } from '../context/DevUserContext';
import { isDevelopment } from '../utils/environment';

export default function DevLayout({ children }) {
  const { user } = useDevUser();
  const [isSidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    if (isDevelopment()) {
      // In dev mode, just reload to reset
      window.location.reload();
    } else {
      window.location.href = '/api/auth/logout';
    }
  };

  return (
    <div className="flex h-screen bg-slate-900 text-slate-200">
      {/* Sidebar Navigation */}
      <div className={`w-64 bg-gray-900 flex-col absolute inset-y-0 left-0 transform ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:relative md:translate-x-0 z-30 transition-transform duration-300 ease-in-out`}>
        <div className="p-4 border-b border-slate-700">
          <h1 className="text-xl font-bold text-sky-400">Sentient AI</h1>
          <p className="text-sm text-slate-400">Welcome, {user?.username}</p>
          {isDevelopment() && (
            <p className="text-xs text-yellow-400 mt-1">🔧 Development Mode</p>
          )}
        </div>
        <nav className="flex-grow p-2">
          <Link to="/dashboard" onClick={() => setSidebarOpen(false)} className="block py-2.5 px-4 rounded hover:bg-slate-800">Dashboard</Link>
          <Link to="/admin" onClick={() => setSidebarOpen(false)} className="block py-2.5 px-4 rounded hover:bg-slate-800">Admin Panel</Link>
        </nav>
        <div className="p-4 border-t border-slate-700">
          <button onClick={handleLogout} className="w-full text-left py-2 px-4 rounded bg-red-600 hover:bg-red-700 transition-colors">
            {isDevelopment() ? 'Reset Dev Session' : 'Logout'}
          </button>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-gray-900/70 backdrop-blur-sm p-4 border-b border-slate-700 md:hidden sticky top-0 z-10">
          <button
            onClick={() => setSidebarOpen(!isSidebarOpen)}
            className="text-slate-300 hover:text-white"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </header>
        
        <main className="flex-1 overflow-auto p-0">
          {children || <Outlet />}
        </main>
      </div>
      
      {/* Overlay for mobile */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black opacity-50 z-20 md:hidden"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}
    </div>
  );
}
