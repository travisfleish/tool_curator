"use client";

import { useState } from "react";

export default function SubmitTool() {
  const [formData, setFormData] = useState({
    name: "",
    website: "",
    description: "",
    email: "",
  });

  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Send form data to an API endpoint (to be implemented)
    const response = await fetch("/api/submit-tool", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    if (response.ok) {
      setMessage("✅ Thank you! Your AI tool has been submitted.");
      setFormData({ name: "", website: "", description: "", email: "" });
    } else {
      setMessage("❌ Error submitting the tool. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900 flex flex-col items-center py-12">
      <h1 className="text-4xl font-bold mb-6">Submit Your Request to Advertise</h1>
      <p className="text-lg text-gray-700 mb-6">Fill out the form below to advertise on our platform.</p>

      <form className="bg-white shadow-md rounded-lg p-6 w-full max-w-lg" onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-gray-700 font-bold mb-2">Company Name</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            className="w-full p-3 border rounded-lg"
            placeholder="Enter company or tool name"
          />
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 font-bold mb-2">Website URL</label>
          <input
            type="url"
            name="website"
            value={formData.website}
            onChange={handleChange}
            required
            className="w-full p-3 border rounded-lg"
            placeholder="https://your-tool.com"
          />
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 font-bold mb-2">Description</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            required
            className="w-full p-3 border rounded-lg"
            placeholder="Describe your company or product in a few sentences..."
            rows="4"
          ></textarea>
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 font-bold mb-2">Your Email</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            className="w-full p-3 border rounded-lg"
            placeholder="Enter your email"
          />
        </div>

        <button
          type="submit"
          className="w-full bg-blue-500 text-white font-bold py-3 rounded-lg hover:bg-blue-600 transition"
        >
          Submit Tool
        </button>

        {message && <p className="mt-4 text-center font-semibold">{message}</p>}
      </form>
    </div>
  );
}
