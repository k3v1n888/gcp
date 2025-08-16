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



// frontend/src/pages/Home.jsx

import React from "react";
import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 text-gray-800">
      <h1 className="text-4xl font-bold mb-4">Welcome to AI Cyber Platform</h1>
      <p className="mb-6 text-lg">
        This is a public homepage. To view the dashboard or manage feeds, please{" "}
        <Link to="/login" className="text-blue-600 underline">
          log in
        </Link>.
      </p>
      <div>
        <Link
          to="/login"
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Log In
        </Link>
      </div>
    </div>
  );
}
