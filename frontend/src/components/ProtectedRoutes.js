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



// frontend/src/components/ProtectedRoutes.js

import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useUser } from '../context/UserContext';

const ProtectedRoutes = ({ allowedRoles }) => {
  const { user, isLoading } = useUser();

  // 1. While the user's status is being checked, show a loading message.
  if (isLoading) {
    return <div>Loading...</div>;
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
