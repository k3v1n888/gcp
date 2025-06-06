// frontend/src/context/UserContext.js

import React, { createContext, useState, useEffect } from "react";

export const UserContext = createContext({
  user: null,
  setUser: () => {}
});

export function UserProvider({ children }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // On mount, ask backend “who am I?” and send cookies
    fetch("/api/auth/me", {
      method: "GET",
      credentials: "include"      // ★ include cookies so the session is sent
    })
      .then((res) => {
        if (!res.ok) throw new Error("Not authenticated");
        return res.json();
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
