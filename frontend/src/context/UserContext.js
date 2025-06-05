// frontend/src/context/UserContext.js

import React, { createContext, useState, useEffect } from "react";

export const UserContext = createContext({
  user: null,
  setUser: () => {}
});

export function UserProvider({ children }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // On mount, ask backend “who am I?”
    fetch("/api/auth/me", {
      method: "GET",
      credentials: "include"   // ← IMPORTANT: send the session cookie
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
      });
  }, []);

  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
}
