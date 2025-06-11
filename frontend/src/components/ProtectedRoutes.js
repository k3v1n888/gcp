import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useUser } from '../context/UserContext';

// This is a simplified version for debugging.
const ProtectedRoutes = () => {
  const { user, isLoading } = useUser();

  // First, we wait until the check is complete.
  // This is the most important step to prevent the race condition.
  if (isLoading) {
    return <div>Verifying login status...</div>;
  }

  // AFTER loading is complete, we decide what to do.
  if (user) {
    // If there IS a user, show the requested page (Dashboard, etc.).
    return <Outlet />;
  } else {
    // If there is NO user, redirect to the login page.
    return <Navigate to="/login" replace />;
  }
};

export default ProtectedRoutes;
