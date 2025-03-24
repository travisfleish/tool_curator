"use client";

import { useState } from "react";

export default function Subscribe() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    const response = await fetch("/api/subscribe", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email }),
    });

    const data = await response.json();
    setMessage(data.message);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 text-gray-900">
      <h1 className="text-3xl font-bold mb-4">Join Our Free Newsletter</h1>
      <p className="text-gray-600 mb-4">Get the latest AI tools and trends delivered straight to your inbox.</p>

      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-lg">
        <input
          type="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="p-2 border rounded w-full mb-4"
        />
        <button type="submit" className="px-6 py-3 bg-blue-500 text-white font-bold rounded-lg hover:bg-blue-700 transition">
          Subscribe
        </button>
      </form>

      {message && <p className="mt-4 text-green-600">{message}</p>}
    </div>
  );
}