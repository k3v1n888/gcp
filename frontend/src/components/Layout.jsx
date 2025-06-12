// frontend/src/components/Layout.jsx

import React from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';

export default function Layout() {
  const { user } = useUser();
  const navigate = useNavigate();

  const handleLogout = () => {
    // This simply redirects to the backend logout endpoint
    window.location.href = '/api/auth/logout';
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar Navigation */}
      <div className="w-64 bg-gray-800 text-white flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <h1 className="text-xl font-bold">Quantum AI</h1>
          <p className="text-sm text-gray-400">Welcome, {user?.username}</p>
        </div>
        <nav className="flex-grow p-2">
          <Link to="/dashboard" className="block py-2 px-4 rounded hover:bg-gray-700">Dashboard</Link>
          {user?.role === 'admin' && (
            <Link to="/admin" className="block py-2 px-4 rounded hover:bg-gray-700">Admin Panel</Link>
          )}
        </nav>
        <div className="p-4 border-t border-gray-700">
          <button onClick={handleLogout} className="w-full text-left py-2 px-4 rounded bg-red-600 hover:bg-red-700">
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 p-6 overflow-y-auto">
        <Outlet /> {/* This is where the page content (Dashboard, AdminPanel) will be rendered */}
      </main>
    </div>
  );
}
