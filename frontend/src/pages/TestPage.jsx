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



import React from 'react';
import { useUser } from '../context/UserContext';
import { Link } from 'react-router-dom';

const TestPage = () => {
  const { user, isLoading } = useUser();

  if (isLoading) {
    return <h1 style={{ fontFamily: 'monospace', margin: '20px' }}>Test Page: Checking login status...</h1>;
  }

  if (!user) {
    return (
        <div>
            <h1 style={{ fontFamily: 'monospace', margin: '20px' }}>Test Page: No user is logged in.</h1>
            <Link to="/login" style={{ fontFamily: 'monospace', margin: '20px' }}>Go to Login</Link>
        </div>
    );
  }

  return (
    <div>
      <h1 style={{ fontFamily: 'monospace', margin: '20px' }}>Test Page: Login Successful!</h1>
      <h2 style={{ fontFamily: 'monospace', margin: '20px' }}>User Data:</h2>
      <pre style={{ fontFamily: 'monospace', margin: '20px', border: '1px solid #ccc', padding: '10px' }}>
        {JSON.stringify(user, null, 2)}
      </pre>
    </div>
  );
};

export default TestPage;
