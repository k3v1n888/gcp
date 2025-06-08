// frontend/src/components/ProtectedRoutes.js

import React, { useContext } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { UserContext } from "../context/UserContext";

export default function ProtectedRoutes() {
  const { user } = useContext(UserContext);

  console.log("ProtectedRoutes: current user state:", user); // ADD THIS

  if (!user) {
    // If not logged in, send to the React “/login” page
    return <Navigate to="/login" />;
  }
  return <Outlet />;
}
