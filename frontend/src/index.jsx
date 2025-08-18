

import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';
import './styles/theme-fixes.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  // By commenting out StrictMode, we simplify the rendering cycle for this final debug step.
  // <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  // </React.StrictMode>
);