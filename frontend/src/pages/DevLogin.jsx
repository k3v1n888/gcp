// Development-only login bypass
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function DevLogin() {
  const navigate = useNavigate();

  useEffect(() => {
    // Auto-login in development mode
    fetch('/api/auth/dev-login', {
      method: 'GET',
      credentials: 'include'
    })
    .then(response => {
      if (response.ok) {
        // Redirect to dashboard after successful dev login
        window.location.href = '/dashboard?dev_login=success';
      } else {
        console.error('Dev login failed');
      }
    })
    .catch(error => {
      console.error('Dev login error:', error);
    });
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900">
      <div className="bg-slate-800 p-8 rounded-lg shadow-lg w-96 text-center border border-slate-700">
        <h2 className="text-2xl font-bold mb-4 text-sky-400">Development Mode</h2>
        <p className="text-slate-300 mb-4">Auto-logging in with dev user...</p>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-400 mx-auto"></div>
      </div>
    </div>
  );
}
