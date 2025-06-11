import React from 'react';
import { Route, Routes } from 'react-router-dom';
import { UserProvider } from './context/UserContext';
import ProtectedRoutes from './components/ProtectedRoutes';
import Home from './pages/Home';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import AdminPanel from './pages/AdminPanel';
import Unauthorized from './pages/Unauthorized';

function App() {
  return (
    <UserProvider>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/unauthorized" element={<Unauthorized />} />

        {/* Protected Routes for any logged-in user */}
        <Route element={<ProtectedRoutes allowedRoles={['admin', 'user', 'analyst', 'viewer']} />}>
          <Route path="/dashboard" element={<Dashboard />} />
        </Route>
        
        {/* Admin-Only Protected Route */}
        <Route element={<ProtectedRoutes allowedRoles={['admin']} />}>
          <Route path="/admin" element={<AdminPanel />} />
        </Route>
      </Routes>
    </UserProvider>
  );
}

export default App;
