// Environment-aware App component
import React from 'react';
import { isDevelopment } from './utils/environment';

// Import both app versions
import DevApp from './DevApp';
import ProdApp from './ProdApp';

function App() {
  // Use development app on VM, production app elsewhere
  if (isDevelopment()) {
    console.log('🔧 Loading Development App (No Auth Required)');
    return <DevApp />;
  } else {
    console.log('🔒 Loading Production App (Full Auth Required)');
    return <ProdApp />;
  }
}

export default App;
