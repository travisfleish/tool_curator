"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { ExternalLink } from "lucide-react";
import { Menu, X } from "lucide-react"

const SOURCES = [
  { name: "Future Tools", id: "FutureTools.io" },
  { name: "Toolify", id: "Toolify.ai" },
  { name: "There's an AI for That", id: "There's an AI for That" },
  { name: "AI Top Tools", id: "AI Top Tools" },
  { name: "AI Tools Directory", id: "AI Tools Directory" },
];


const FILTERS = [
  { name: "New Tools", id: "new" },
  { name: "Top Tools", id: "top" },
];

export default function Home() {
  const [tools, setTools] = useState([]);
  const [selectedSource, setSelectedSource] = useState("FutureTools.io");
  const [selectedFilter, setSelectedFilter] = useState("new");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [showNewsletter, setShowNewsletter] = useState(true);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    fetch(`https://tool-curator.onrender.com/api/tools?source=${selectedSource}&filter=${selectedFilter}`)
      .then((response) => response.json())
      .then((data) => {
        // Slice to 8 tools if more than 8 and filter is 'new'
        const processedTools = selectedFilter === 'new'
          ? data.slice(0, 8)
          : data;

        // Randomly certify one tool if desired
        if (processedTools.length > 0) {
          const certifiedIndex = Math.floor(Math.random() * processedTools.length);
          processedTools[certifiedIndex].certified = true;
        }

        setTools(processedTools);
      })
      .catch((error) => console.error("Error fetching tools:", error));
  }, [selectedSource, selectedFilter]);

  useEffect(() => {
  const handleScroll = () => {
    const scrollPosition = window.innerHeight + window.scrollY;
    const pageHeight = document.documentElement.scrollHeight;

    if (scrollPosition >= pageHeight - 50) {
      setShowNewsletter(false); // Hide newsletter when at the bottom
    } else {
      setShowNewsletter(true); // Show newsletter when scrolling up
    }
  };

  window.addEventListener("scroll", handleScroll);
  return () => window.removeEventListener("scroll", handleScroll);
}, []);


  const handleSubscribe = async (e) => {
    e.preventDefault();

    const response = await fetch("/api/subscribe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });

    const data = await response.json();
    setMessage(data.error ? data.error : "Thank you for subscribing!");
    setEmail("");
  };

return (
  <div className="min-h-screen bg-gray-100 text-gray-900 flex flex-col items-center relative">
    {/* Header Section */}
    <header className="relative w-full bg-gradient-to-r from-blue-300 via-indigo-400 to-purple-600 text-white shadow-lg px-4 py-8 md:px-10 md:py-12">
      {/* Top: Logo + Hamburger + Nav */}
      <div className="flex items-center justify-between w-full mb-6">
        {/* Left: Logo + Powered By */}
        <div className="flex flex-col items-center gap-3">
          <span className="text-xs tracking-wider text-black font-semibold leading-tight text-center">
            POWERED BY:
          </span>
          <a href="https://www.twinbrain.ai" target="_blank" rel="noopener noreferrer">
            <Image src="/logo.png" alt="TwinBrain Logo" width={100} height={50} />
          </a>
        </div>



        {/* Desktop Nav */}
        <nav className="hidden sm:flex gap-6 text-sm sm:text-base text-white font-semibold">
          <a href="/submit-tool" className="hover:underline">Submit Tool</a>
          <a href="/advertise" className="hover:underline">Advertise</a>
          <a href="https://www.twinbrain.ai/blog" target="_blank" rel="noopener noreferrer" onClick={() => setMenuOpen(false)}>Blog</a>
          <a href="#fixed-newsletter" className="hover:underline">Newsletter</a>
        </nav>

        {/* Mobile Hamburger */}
        <div className="sm:hidden">
          <button onClick={() => setMenuOpen(!menuOpen)} className="text-white focus:outline-none">
            {menuOpen ? <X size={28} /> : <Menu size={28} />}
          </button>
        </div>
      </div>

      {/* Mobile Dropdown */}
      {menuOpen && (
        <div className="absolute top-0 left-0 right-0 bg-blue-400 text-gray-900 z-40 h-[250px] px-4 shadow-md animate-fade-in border-b border-gray-200 overflow-hidden">
          {/* Top Row: Logo and Close Button */}
          <div className="flex items-center justify-between px-1 pt-3 pb-1">
            <a href="https://www.twinbrain.ai" target="_blank" rel="noopener noreferrer">
              <Image src="/logo.png" alt="TwinBrain Logo" width={80} height={40} />
            </a>
            <button
              onClick={() => setMenuOpen(false)}
              className="text-gray-600 hover:text-red-500 text-2xl font-light"
            >
              ×
            </button>
          </div>

          {/* Nav Links Container */}
          <div className="flex flex-col items-center justify-center h-[190px] space-y-2">
            <h1 className="text-lg font-semibold tracking-tight">ToolCurator.ai</h1>
            <a href="/submit-tool" onClick={() => setMenuOpen(false)} className="hover:underline text-base">Submit Tool</a>
            <a href="/advertise" onClick={() => setMenuOpen(false)} className="hover:underline text-base">Advertise</a>
            <a href="https://www.twinbrain.ai/blog" target="_blank" rel="noopener noreferrer" onClick={() => setMenuOpen(false)} className="hover:underline text-base">Blog</a>
            <a href="#fixed-newsletter" onClick={() => setMenuOpen(false)} className="hover:underline text-base">Newsletter</a>
          </div>
        </div>
      )}

      {/* Centered Title */}
      <div className="text-center">
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold leading-tight mb-2">ToolCurator.ai</h1>
        <p className="hidden sm:block text-md sm:text-lg md:text-xl">We aggregate, curate, and simplify AI tool discovery</p>
        <p className="text-sm sm:text-md mt-1 text-white/90">Spend your time building, not searching</p>
      </div>
    </header>



      {/* Source Selection Bar */}
      <section className="p-4 grid grid-cols-2 sm:flex sm:flex-wrap sm:justify-center gap-3">
        {SOURCES.map((source) => (
          <button
            key={source.id}
            onClick={() => setSelectedSource(source.id)}
            className={`px-3 py-2 border rounded-lg text-sm sm:text-base text-center ${
              selectedSource === source.id ? "bg-blue-500 text-white" : "bg-white text-gray-900"
            } hover:bg-blue-400 hover:text-white transition`}
          >
            {source.name}
          </button>
        ))}
      </section>


      {/* New & Top Tools Selection - Now uncommented */}
      <section className="p-4 flex justify-center space-x-3">
        {FILTERS.map((filter) => (
          <button
            key={filter.id}
            onClick={() => setSelectedFilter(filter.id)}
            className={`px-4 py-2 border rounded-lg ${
              selectedFilter === filter.id ? "bg-blue-500 text-white" : "bg-white text-gray-900"
            } hover:bg-blue-400 hover:text-white transition`}
          >
            {filter.name}
          </button>
        ))}
      </section>

      <section className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {tools.slice(0,8).map((tool, index) => {
            const imageUrl = tool.screenshot_url && tool.screenshot_url.trim() !== ""
              ? tool.screenshot_url
              : "/default-screenshot.png";

            return (
              <div
                key={index}
                className={`relative p-4 border rounded-lg shadow-lg bg-white flex flex-col items-center text-center ${tool.certified ? "border-4 border-yellow-500" : ""}`}
              >
                {tool.certified && (
                  <div className="absolute -top-4 right-1/4 transform translate-x-1/2 flex items-center space-x-2 bg-yellow-500 text-white font-bold text-sm px-3 py-1 rounded-full shadow-lg">
                    <span>⭐ Nik and Travis Certified!</span>
                  </div>
                )}
                <Image
                  src={imageUrl}
                  alt={`${tool.name} Screenshot`}
                  width={1280}
                  height={800}
                  className="w-full h-auto rounded-lg mb-4"
                  unoptimized
                />
                <h3 className="text-lg font-bold flex items-center">
                  <a href={tool.source_url} className="text-blue-500 hover:underline" target="_blank" rel="noopener noreferrer">
                    {tool.name}
                  </a>
                  <ExternalLink className="ml-2 w-4 h-4 text-gray-500" />
                </h3>
                <p className="text-gray-600 text-center">{tool.short_description}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Fixed Newsletter Call to Action Below Tools */}
      <section id="fixed-newsletter" className="w-full bg-gray-200 py-8 flex flex-col items-center shadow-md mt-10">
        <div className="max-w-4xl text-center">
          <h2 className="text-2xl font-bold mb-2">Sign up for our Tool-of-the-Day Newsletter!</h2>
          <p className="text-sm text-gray-600 mb-4">We respect your email inbox and will never spam!</p>
          <form className="mt-2 flex space-x-2 justify-center" onSubmit={handleSubscribe}>
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="px-4 py-2 w-80 rounded-lg text-gray-900 border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
            <button type="submit" className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">
              Subscribe
            </button>
          </form>
          <p className="text-sm mt-2 text-green-600">{message}</p>
        </div>
      </section>

      {/* Floating Newsletter Section */}
     {showNewsletter && (
      <section className="hidden sm:flex fixed bottom-0 w-full bg-blue-400 text-white py-4 flex-col items-center shadow-lg">
        <h2 className="text-xl font-bold">Stay Updated</h2>
        <p className="mt-1 text-sm">Subscribe to our newsletter for the latest AI tools and insights.</p>
        <form className="mt-2 flex space-x-2" onSubmit={handleSubscribe}>
          <input
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="px-4 py-1 rounded-lg text-gray-900 border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <button type="submit" className="px-4 py-1 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition">
            Subscribe
          </button>
        </form>
        <p className="text-sm mt-2">{message}</p>
       </section>
      )}
{/* Embedded YouTube Videos Section */}
<div className="w-full flex flex-col items-center py-8">

  {/* Follow us Header & YouTube Link */}
  <div className="text-center mb-6">
    <a
      href="https://www.youtube.com/channel/UCzpdjfdL0QvehLHxHGCa25A"
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center space-x-2 text-red-600 hover:text-red-700 transition"
    >
      <span className="text-lg font-semibold">Subscribe to the TwinBrainAI YouTube channel!!</span>
    </a>
  </div>

  {/* YouTube Videos */}
  <section className="w-full flex flex-wrap justify-center gap-6 px-4">
    {/* First Video */}
    <iframe
      className="w-4/5 h-[500px] max-w-[900px]"
      src="https://www.youtube.com/embed/Ej9zCLI2ZdY"
      title="YouTube video player"
      frameBorder="0"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowFullScreen
    ></iframe>

    {/* Second Video */}
    <iframe
      className="w-4/5 h-[500px] max-w-[900px]"
      src="https://www.youtube.com/embed/gqqvI1oJdZs"
      title="YouTube video player"
      frameBorder="0"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowFullScreen
    ></iframe>
  </section>
</div>

    <footer className="w-full bg-white text-gray-700 border-t mt-10 py-8 flex flex-col items-center space-y-4">
      {/* Logo */}
      <a href="https://www.twinbrain.ai" target="_blank" rel="noopener noreferrer" className="flex flex-col items-center space-y-2">
        <Image src="/logo.png" alt="TwinBrain Logo" width={120} height={60} />
      </a>

      {/* LinkedIn Icon */}
      <div className="mt-2">
        <a
          href="https://www.linkedin.com/company/twinbrain-ai/"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="LinkedIn"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            role="img"
            viewBox="0 0 24 24"
            width="32"
            height="32"
            fill="#0A66C2"
          >
            <title>LinkedIn</title>
            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.937v5.669H9.351V9h3.414v1.561h.049c.476-.9 1.637-1.852 3.368-1.852 3.6 0 4.266 2.368 4.266 5.452v6.291zM5.337 7.433a2.062 2.062 0 1 1 0-4.124 2.062 2.062 0 0 1 0 4.124zM6.977 20.452H3.696V9h3.281v11.452zM22.225 0H1.771C.792 0 0 .771 0 1.723v20.555C0 23.229.792 24 1.771 24h20.451C23.2 24 24 23.229 24 22.278V1.723C24 .771 23.2 0 22.222 0z"/>
          </svg>
        </a>
      </div>


      <p className="text-xs text-gray-500">&copy; {new Date().getFullYear()} TwinBrain AI. All rights reserved.</p>
    </footer>



    </div>
  );
}