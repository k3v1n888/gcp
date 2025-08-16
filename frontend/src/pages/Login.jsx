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



// frontend/src/pages/Login.jsx

import React from "react";

export default function Login() {
  const handleLogin = () => {
    // Redirect browser to our FastAPI /api/auth/login
    window.location.href = "/api/auth/login";
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded-lg shadow-lg w-96 text-center">
        <h2 className="text-2xl font-bold mb-4">Log In with Google</h2>
        <button
          onClick={handleLogin}
          className="w-full py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition"
        >
          Sign in with Google
        </button>
      </div>
    </div>
  );
}
