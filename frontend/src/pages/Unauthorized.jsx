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

export default function Unauthorized() {
  return (
    <div className="flex justify-center items-center h-screen">
      <h1 className="text-2xl font-bold text-red-600">Unauthorized Access</h1>
    </div>
  );
}