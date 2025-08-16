/*
 * Copyright (c) 2025 Kevin Zachary
 * All rights reserved.
 *
 * This software and associated documentation files (the "Software") are the 
 * exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
 * modification, or use of this software is strictly prohibited.
 *
 * For licensing inquiries, contact: kevin@zachary.com
 */

/*
 * Author: Kevin Zachary
 * Copyright: Sentient Spire
 */



// Development-specific User Context with auto-login
import React, { createContext, useContext, useState, useEffect } from 'react';
import { isDevelopment } from '../utils/environment';

const DevUserContext = createContext();

export const useDevUser = () => {
  const context = useContext(DevUserContext);
  if (!context) {
    throw new Error('useDevUser must be used within DevUserProvider');
  }
  return context;
};

export const DevUserProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (isDevelopment()) {
      // Auto-create dev user
      const devUser = {
        id: 1,
        email: 'dev@localhost.com',
        username: 'Developer',
        role: 'admin',
        tenant_id: 1,
        status: 'active'
      };
      
      console.log('🔧 Development mode: Auto-login as dev user');
      setUser(devUser);
      setIsLoading(false);
      
    } else {
      // Production behavior - check actual auth
      fetch('/api/auth/me', {
        credentials: 'include'
      })
      .then(response => response.ok ? response.json() : null)
      .then(userData => {
        setUser(userData);
        setIsLoading(false);
      })
      .catch(() => {
        setUser(null);
        setIsLoading(false);
      });
    }
  }, []);

  return (
    <DevUserContext.Provider value={{ user, isLoading, setUser }}>
      {children}
    </DevUserContext.Provider>
  );
};
