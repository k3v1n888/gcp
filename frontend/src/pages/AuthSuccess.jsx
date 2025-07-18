// frontend/src/pages/AuthSuccess.jsx

import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';

const AuthSuccess = () => {
  const { user, isLoading } = useUser();
  const navigate = useNavigate();

  useEffect(() => {
    // This effect runs when the loading status or user status changes.
    if (!isLoading) {
      if (user) {
        // If loading is finished AND we have a user, it's safe to go to the dashboard.
        navigate('/dashboard');
      } else {
        // If loading is finished and there's still no user, something went wrong.
        navigate('/login?error=session_error');
      }
    }
  }, [isLoading, user, navigate]); // Dependencies that trigger the effect

  return <div>Finalizing login, please wait...</div>;
};

export default AuthSuccess;
