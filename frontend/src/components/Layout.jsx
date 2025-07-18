import React, { useState } from 'react';
import { Outlet, Link } from 'react-router-dom';
import { useUser } from '../context/UserContext';

export default function Layout() {
  const { user } = useUser();
  const [isSidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    window.location.href = '/api/auth/logout';
  };

  return (
    <div className="flex h-screen bg-slate-900 text-slate-200">
      {/* Sidebar Navigation */}
      <div className={`w-64 bg-gray-900 flex-col absolute inset-y-0 left-0 transform ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:relative md:translate-x-0 z-30 transition-transform duration-300 ease-in-out`}>
        <div className="p-4 border-b border-slate-700">
          <h1 className="text-xl font-bold text-sky-400">Quantum AI</h1>
          <p className="text-sm text-slate-400">Welcome, {user?.username}</p>
        </div>
        <nav className="flex-grow p-2">
          <Link to="/dashboard" onClick={() => setSidebarOpen(false)} className="block py-2.5 px-4 rounded hover:bg-slate-800">Dashboard</Link>
          {user?.role === 'admin' && (
            <Link to="/admin" onClick={() => setSidebarOpen(false)} className="block py-2.5 px-4 rounded hover:bg-slate-800">Admin Panel</Link>
          )}
        </nav>
        <div className="p-4 border-t border-slate-700">
          <button onClick={handleLogout} className="w-full text-left py-2 px-4 rounded bg-red-600 hover:bg-red-700 transition-colors">
            Logout
          </button>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-gray-900/70 backdrop-blur-sm p-4 border-b border-slate-700 md:hidden sticky top-0 z-10">
          {/* Hamburger Menu Button */}
          <button onClick={() => setSidebarOpen(!isSidebarOpen)} className="text-slate-200">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
          </button>
        </header>
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
