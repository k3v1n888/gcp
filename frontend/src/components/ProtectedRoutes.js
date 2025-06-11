import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useUser } from '../context/UserContext';

const ProtectedRoutes = ({ allowedRoles }) => {
  const { user, isLoading } = useUser();

  // 1. Wait for the user check to complete
  if (isLoading) {
    return <div>Loading...</div>; // Or a spinner component
  }

  // 2. After loading, check if there is a user and if their role is allowed
  if (!user) {
    // If no user, redirect to login
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    // If user's role is not allowed, redirect to unauthorized page
    return <Navigate to="/unauthorized" replace />;
  }
  
  // 3. If all checks pass, render the child route (e.g., Dashboard or AdminPanel)
  return <Outlet />;
};

export default ProtectedRoutes;
