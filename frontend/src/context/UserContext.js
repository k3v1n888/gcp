// frontend/src/context/UserContext.js

import React, { createContext, useState, useEffect } from "react";

export const UserContext = createContext({
  user: null,
  setUser: () => {}
});

export function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true); // <--- ADD THIS LINE

  useEffect(() => {
    console.log("UserContext: Attempting to fetch /api/auth/me");
    fetch("/api/auth/me", {
      method: "GET",
      credentials: "include"
    })
      .then((res) => {
        console.log("UserContext: Response status:", res.status, "ok:", res.ok);
        if (res.ok) {
          return res.json();
        }
        throw new Error("Not authenticated");
      })
      .then((data) => {
        console.log("UserContext: User data received:", data);
        setUser(data);
      })
      .catch((error) => {
        console.error("UserContext: Error fetching user:", error);
        setUser(null);
      })
      .finally(() => { // <--- ADD THIS BLOCK
        setIsLoading(false); // Set loading to false after fetch completes (success or error)
      });
  }, []);

  useEffect(() => {
    console.log("UserContext: 'user' state changed to:", user);
  }, [user]);

  return (
    // <--- ADD isLoading to the context value
    <UserContext.Provider value={{ user, setUser, isLoading }}>
      {children}
    </UserContext.Provider>
  );
}
