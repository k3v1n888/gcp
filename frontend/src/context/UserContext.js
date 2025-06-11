import React, { createContext, useState, useEffect } from "react";
// 1. Import useLocation from the router library
import { useLocation } from "react-router-dom";

export const UserContext = createContext({
  user: null,
  setUser: () => {},
  isLoading: true,
});

export function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // 2. Get the current page location
  const location = useLocation();

  useEffect(() => {
    setIsLoading(true); // Set loading to true before each check

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
  // 3. Add location.pathname to the dependency array
  // This tells React to re-run this code every time the URL path changes.
  }, [location.pathname]);

  return (
    <UserContext.Provider value={{ user, setUser, isLoading }}>
      {children}
    </UserContext.Provider>
  );
}
