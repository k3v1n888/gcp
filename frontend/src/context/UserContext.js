import React, { createContext, useState, useEffect, useContext } from 'react';
import { useLocation } from 'react-router-dom';

export const UserContext = createContext({
  user: null,
  setUser: () => {},
  isLoading: true,
});

export function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const location = useLocation();

  useEffect(() => {
    // On every URL change, we re-check the user's status.
    setIsLoading(true);
    
    fetch('/api/auth/me', {
      method: 'GET',
      credentials: 'include',
    })
      .then(res => {
        if (res.ok) {
          return res.json();
        }
        // If not authenticated, throw an error to be caught below
        throw new Error('Not authenticated');
      })
      .then(data => {
        setUser(data);
      })
      .catch(() => {
        // If any error occurs (including the 401 Not authenticated), set user to null
        setUser(null);
      })
      .finally(() => {
        // This always runs, ensuring we don't get stuck in a loading state
        setIsLoading(false);
      });
  }, [location.pathname]); // The key: re-run this effect when the URL path changes

  return (
    <UserContext.Provider value={{ user, setUser, isLoading }}>
      {children}
    </UserContext.Provider>
  );
}

export const useUser = () => useContext(UserContext);
