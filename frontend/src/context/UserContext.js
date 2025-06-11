import React, { createContext, useState, useEffect } from "react";
import { useLocation } from "react-router-dom";

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
    setIsLoading(true);
    fetch("/api/auth/me", {
      method: "GET",
      credentials: "include"
    })
      .then((res) => {
        if (res.ok) {
          return res.json();
        }
        throw new Error("Not authenticated");
      })
      .then((data) => {
        setUser(data);
      })
      .catch(() => {
        setUser(null);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [location.pathname]);

  return (
    // --- THIS IS THE FIX: The closing tag was incorrect ---
    <UserContext.Provider value={{ user, setUser, isLoading }}>
      {children}
    </UserContext.Provider> 
  );
}
