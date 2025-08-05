// frontend/src/App.jsx
import React, { useEffect } from 'react';
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
import IncidentDetail from './pages/IncidentDetail'; // <-- 1. Import the new page
import { getAuthToken } from './utils/auth'; // <-- Import the auth token utility

function App() {
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch('/api/user/profile', {
          headers: { Authorization: `Bearer ${getAuthToken()}` },
        });

        if (!response.ok) {
          // DON'T immediately redirect - this might cause a loop
          // setIsAuthenticated(false);
          console.log('Auth check failed');
        } else {
          setIsAuthenticated(true);
        }
      } catch (error) {
        console.error('Auth check error:', error);
      }
    };

    checkAuth();
  }, []); // Make sure this doesn't run on every render

  return (
    <UserProvider>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/unauthorized" element={<Unauthorized />} />
        <Route path="/auth/success" element={<AuthSuccess />} />

        {/* Protected Routes now wrapped in the Layout */}
        <Route element={<Layout />}>
          <Route
            element={
              <ProtectedRoutes
                allowedRoles={['admin', 'user', 'analyst', 'viewer']}
              />
            }
          >
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/threats/:id" element={<ThreatDetail />} />
            <Route path="/incidents/:id" element={<IncidentDetail />} /> {/* <-- 2. ADD THIS ROUTE */}
          </Route>
          <Route element={<ProtectedRoutes allowedRoles={['admin']} />}>
            <Route path="/admin" element={<AdminPanel />} />
          </Route>
        </Route>
      </Routes>
    </UserProvider>
  );
}

export default App;