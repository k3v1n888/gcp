import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useUser } from '../context/UserContext';

const ProtectedRoutes = ({ allowedRoles }) => {
  const { user, isLoading } = useUser();

  // 1. While the user's status is being checked, show a loading message.
  if (isLoading) {
    return <div>Loading authentication...</div>;
  }

  // 2. After checking, if there is no user, redirect to the login page.
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  // 3. If there is a user, but their role is not in the allowed list, redirect to an "Unauthorized" page.
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  // 4. If all checks pass, show the page they requested.
  return <Outlet />;
};

export default ProtectedRoutes;
