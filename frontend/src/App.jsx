import React from 'react';
import { Route, Routes } from 'react-router-dom';
import { UserProvider } from './context/UserContext';
import Login from './pages/Login';
import TestPage from './pages/TestPage'; // Import our new page

function App() {
  return (
    <UserProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<TestPage />} />
      </Routes>
    </UserProvider>
  );
}

export default App;
