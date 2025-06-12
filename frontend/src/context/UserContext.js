import React, { createContext, useState, useEffect, useContext } from 'react';

export const UserContext = createContext(null);

export function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // This effect will now only run ONCE when the component first mounts.
    // It will not re-run on page navigation, which will break the loop.
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
      
  }, []); // <-- This empty array is the critical change.

  return (
    <UserContext.Provider value={{ user, setUser, isLoading }}>
      {children}
    </UserContext.Provider>
  );
}

export const useUser = () => useContext(UserContext);
