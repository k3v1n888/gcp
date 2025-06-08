// frontend/src/components/ProtectedRoutes.js

import React, { useContext } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { UserContext } from "../context/UserContext";

export default function ProtectedRoutes() {
  const { user, isLoading } = useContext(UserContext); // <--- GET isLoading from context

  console.log("ProtectedRoutes: current user state:", user, "isLoading:", isLoading); // <--- LOG isLoading

  // <--- ADD THIS LOADING CHECK
  if (isLoading) {
    // While loading, display a simple message or a spinner
    return <div className="min-h-screen flex items-center justify-center text-lg">Loading authentication...</div>;
  }

  if (!user) {
    // If not logged in AND not loading, send to the React “/login” page
    return <Navigate to="/login" />;
  }
  return <Outlet />;
}
