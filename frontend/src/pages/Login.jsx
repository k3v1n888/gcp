// frontend/src/pages/Login.jsx

import React from "react";

export default function Login() {
  const handleGoogleLogin = () => {
    // Simply redirect browser to the backend route
    window.location.href = "/api/auth/login";
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-6 rounded-md shadow-md w-80 text-center">
        <h2 className="text-2xl font-semibold mb-4">Log In with Google</h2>
        <button
          onClick={handleGoogleLogin}
          className="w-full bg-red-600 text-white p-2 rounded hover:bg-red-700"
        >
          Log in with Google
        </button>
      </div>
    </div>
  );
}
