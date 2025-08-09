// Development-specific App component with auth bypass
import React from 'react';
import { Route, Routes } from 'react-router-dom';
import { DevUserProvider } from './context/DevUserContext';
import { isDevelopment } from './utils/environment';

// Import components
import Layout from './components/Layout';
import Home from './pages/Home';
import DevLogin from './pages/DevLogin';
import Dashboard from './pages/Dashboard';
import AdminPanel from './pages/AdminPanel';
import ThreatDetail from './pages/ThreatDetail';
import IncidentDetail from './pages/IncidentDetail';

// Dev-specific protected route (always allows access)
const DevProtectedRoute = ({ children }) => {
  return <Layout>{children}</Layout>;
};

function DevApp() {
  return (
    <DevUserProvider>
      <Routes>
        {/* Development routes - no auth required */}
        <Route path="/" element={<DevLogin />} />
        <Route path="/login" element={<DevLogin />} />
        
        {/* All routes accessible in dev mode */}
        <Route path="/dashboard" element={<DevProtectedRoute><Dashboard /></DevProtectedRoute>} />
        <Route path="/admin" element={<DevProtectedRoute><AdminPanel /></DevProtectedRoute>} />
        <Route path="/threats/:id" element={<DevProtectedRoute><ThreatDetail /></DevProtectedRoute>} />
        <Route path="/incidents/:id" element={<DevProtectedRoute><IncidentDetail /></IncidentDetail>} />
      </Routes>
    </DevUserProvider>
  );
}

export default DevApp;
