// frontend/src/App.jsx

import React from 'react';
import { Route, Routes } from 'react-router-dom';
import { UserProvider } from './context/UserContext';
import ProtectedRoutes from './components/ProtectedRoutes';
import Layout from './components/Layout'; // <-- Import the new Layout
import Home from './pages/Home';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import AdminPanel from './pages/AdminPanel';
import Unauthorized from './pages/Unauthorized';
import AuthSuccess from './pages/AuthSuccess';

function App() {
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
          <Route element={<ProtectedRoutes allowedRoles={['admin', 'user', 'analyst', 'viewer']} />}>
            <Route path="/dashboard" element={<Dashboard />} />
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
