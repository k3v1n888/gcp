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



// Simple test page to debug environment detection
import React from 'react';
import { isDevelopment } from '../utils/environment';

const DebugPage = () => {
  const isdev = isDevelopment();
  
  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1>🔧 Development Environment Debug</h1>
      <div>
        <h3>Environment Detection:</h3>
        <p>isDevelopment(): {isdev ? 'TRUE ✅' : 'FALSE ❌'}</p>
        <p>Hostname: {window.location.hostname}</p>
        <p>Full URL: {window.location.href}</p>
        <p>NODE_ENV: {process.env.NODE_ENV}</p>
      </div>
      
      <div>
        <h3>Expected Result:</h3>
        <p>Since hostname is "192.168.64.13", isDevelopment() should return TRUE</p>
      </div>
      
      <div>
        <h3>App State:</h3>
        <p>If you can see this page, the React app is loading</p>
        <p>If environment detection works, you should see DevApp instead of auth</p>
      </div>
    </div>
  );
};

export default DebugPage;
