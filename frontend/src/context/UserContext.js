import React, { createContext, useState, useEffect, useContext } from 'react';
import { useLocation } from 'react-router-dom';

export const UserContext = createContext(null);

export function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const location = useLocation();

  useEffect(() => {
    // On every URL change, we re-check the user's status.
    setIsLoading(true);
    
    fetch('/api/auth/me', { credentials: 'include' })
      .then(res => {
        if (res.ok) {
          return res.json();
        }
        throw new Error('Not authenticated');
      })
      .then(data => setUser(data))
      .catch(() => setUser(null))
      .finally(() => setIsLoading(false));
      
  }, [location.pathname]); // This dependency array is the key to the fix.

  return (
    <UserContext.Provider value={{ user, setUser, isLoading }}>
      {children}
    </UserContext.Provider>
  );
}

export const useUser = () => useContext(UserContext);
