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



// Production App component with full authentication
import React from 'react';
import { Route, Routes } from 'react-router-dom';
import { UserProvider } from './context/UserContext';
import ProtectedRoutes from './components/ProtectedRoutes';
import Layout from './components/Layout';
import Home from './pages/Home';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import AdminPanel from './pages/AdminPanel';
import Unauthorized from './pages/Unauthorized';
import AuthSuccess from './pages/AuthSuccess';
import ThreatDetail from './pages/ThreatDetail';
import IncidentDetail from './pages/IncidentDetail';
import MultiTenantDashboard from './components/MultiTenantDashboard';

function ProdApp() {
  return (
    <UserProvider>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/unauthorized" element={<Unauthorized />} />
        <Route path="/auth/success" element={<AuthSuccess />} />

        {/* Protected Routes with full authentication */}
        <Route element={<Layout />}>
          <Route element={<ProtectedRoutes allowedRoles={['admin', 'user', 'analyst', 'viewer']} />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/multi-tenant" element={<MultiTenantDashboard />} />
            <Route path="/threats/:id" element={<ThreatDetail />} />
            <Route path="/incidents/:id" element={<IncidentDetail />} />
          </Route>
          <Route element={<ProtectedRoutes allowedRoles={['admin']} />}>
            <Route path="/admin" element={<AdminPanel />} />
          </Route>
        </Route>
      </Routes>
    </UserProvider>
  );
}

export default ProdApp;
