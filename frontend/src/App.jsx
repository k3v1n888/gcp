// frontend/src/App.jsx

import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import FeedControl from "./pages/FeedControl";
import AdminPanel from "./pages/AdminPanel";
import Unauthorized from "./pages/Unauthorized";
// import Home if you have a public home, otherwise root can redirect:
import Home from "./pages/Home";

import ProtectedRoutes from "./components/ProtectedRoutes";

export default function App() {
  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/unauthorized" element={<Unauthorized />} />

        {/* All private routes go under this wrapper */}
        <Route element={<ProtectedRoutes />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/feed" element={<FeedControl />} />
          <Route path="/admin" element={<AdminPanel />} />
          {/* add other protected routes here */}
        </Route>

        {/* Fallback: redirect everything else to home */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}
