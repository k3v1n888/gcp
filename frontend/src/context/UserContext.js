// frontend/src/context/UserContext.js

import React, { createContext, useState, useEffect } from "react";

export const UserContext = createContext(null);

export function UserProvider({ children }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // check “me” endpoint as soon as the app mounts
    fetch("/api/auth/me", {
      method: "GET",
      credentials: "include",    // ← MUST include cookies
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((res) => {
        if (!res.ok) {
          setUser(null);
          return null;
        }
        return res.json();
      })
      .then((data) => {
        if (data) setUser(data);
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
