// frontend/src/context/UserContext.js

import React, { createContext, useState, useEffect } from "react";

export const UserContext = createContext({
  user: null,
  setUser: () => {}
});

export function UserProvider({ children }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    console.log("UserContext: Attempting to fetch /api/auth/me"); // ADD THIS
    fetch("/api/auth/me", {
      method: "GET",
      credentials: "include"
    })
      .then((res) => {
        console.log("UserContext: Response status:", res.status, "ok:", res.ok); // ADD THIS
        if (res.ok) {
          return res.json();
        }
        throw new Error("Not authenticated");
      })
      .then((data) => {
        console.log("UserContext: User data received:", data); // ADD THIS
        setUser(data);
      })
      .catch((error) => {
        console.error("UserContext: Error fetching user:", error); // ADD THIS
        setUser(null);
      });
  }, []);

  // ADD THIS: Observe changes in 'user' state
  useEffect(() => {
    console.log("UserContext: 'user' state changed to:", user);
  }, [user]);

  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
}