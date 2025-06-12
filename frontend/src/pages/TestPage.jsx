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
