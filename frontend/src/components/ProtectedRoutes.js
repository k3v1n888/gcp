import React, { useContext } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { UserContext } from '../context/UserContext';

const ProtectedRoutes = () => {
  const { user } = useContext(UserContext);

  if (!user) {
    return <Navigate to="/login" />;
  }

  // Add role-based access control if needed

  return <Outlet />;
};

export default ProtectedRoutes;