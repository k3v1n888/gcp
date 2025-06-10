// frontend/src/components/ProtectedRoutes.js

import React, { useContext } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { UserContext } from "../context/UserContext";

export default function ProtectedRoutes() {
  const { user, isLoading } = useContext(UserContext);
  
  // --- ADD THIS LINE ---
  console.log("PROTECTED ROUTES: Rendering with user:", user, "and isLoading:", isLoading);

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center text-lg">Loading authentication...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
}
