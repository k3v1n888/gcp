// e.g. in src/context/UserContext.js

import React, { createContext, useEffect, useState } from "react";

export const UserContext = createContext({ user: null, setUser: () => {} });

export function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // On mount, ask “/api/auth/me”
    fetch("/api/auth/me", {
      method: "GET",
      credentials: "include", 
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then(async (resp) => {
        if (resp.status === 200) {
          const info = await resp.json();
          setUser(info);
        } else {
          setUser(null);
        }
      })
      .catch(() => {
        setUser(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  // While waiting for this first request, you might render a spinner:
  if (loading) {
    return <div>Loading…</div>;
  }

  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
}
