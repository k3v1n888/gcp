

// Environment-aware App component
import React from 'react';
import { isDevelopment } from './utils/environment';

// Import both app versions
import DevApp from './DevApp';
import ProdApp from './ProdApp';

function App() {
  // Debug environment detection
  console.log('🔍 Window location:', window.location);
  console.log('🔍 Hostname:', window.location.hostname);
  console.log('🔍 isDevelopment():', isDevelopment());
  
  // Force development app on VM for now
  const hostname = window.location.hostname;
  const isVM = hostname === '192.168.64.13';
  
  if (isVM || isDevelopment()) {
    console.log('🔧 Loading Development App (No Auth Required)');
    return <DevApp />;
  } else {
    console.log('🔒 Loading Production App (Full Auth Required)');
    return <ProdApp />;
  }
}

export default App;
