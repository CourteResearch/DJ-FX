import { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Main Home Page Component
const Home = () => {
  const [genres, setGenres] = useState([]);
  const [selectedGenre, setSelectedGenre] = useState("");
  const [mixTitle, setMixTitle] = useState("Automated DJ Mix");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [mixes, setMixes] = useState([]);
  const [currentMix, setCurrentMix] = useState(null);
  const [currentMixStatus, setCurrentMixStatus] = useState(null);
  
  // Fetch available genres
  useEffect(() => {
    const fetchGenres = async () => {
      try {
        const response = await axios.get(`${API}/genres`);
        setGenres(response.data.genres);
        if (response.data.genres.length > 0) {
          setSelectedGenre(response.data.genres[0]);
        }
      } catch (error) {
        console.error("Failed to fetch genres:", error);
        setError("Failed to load music genres. Please try again later.");
      }
    };
    
    fetchGenres();
  }, []);
  
  // Fetch existing mixes
  useEffect(() => {
    fetchMixes();
  }, []);
  
  // Poll for mix status updates if there's a current mix being processed
  useEffect(() => {
    if (currentMix && currentMix.status === "processing") {
      const interval = setInterval(() => {
        checkMixStatus(currentMix.id);
      }, 5000);
      
      return () => clearInterval(interval);
    }
  }, [currentMix]);
  
  const fetchMixes = async () => {
    try {
      const response = await axios.get(`${API}/mixes`);
      setMixes(response.data);
    } catch (error) {
      console.error("Failed to fetch mixes:", error);
    }
  };
  
  const checkMixStatus = async (mixId) => {
    try {
      const response = await axios.get(`${API}/mixes/${mixId}`);
      setCurrentMixStatus(response.data.status);
      
      // If the mix is completed, refresh the mixes list
      if (response.data.status === "completed") {
        fetchMixes();
        setCurrentMix(response.data);
      }
    } catch (error) {
      console.error("Failed to check mix status:", error);
    }
  };
  
  const createMix = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API}/mixes`, {
        genre: selectedGenre,
        title: mixTitle,
        duration_minutes: 50
      });
      
      setCurrentMix(response.data);
      setCurrentMixStatus(response.data.status);
      setLoading(false);
      
      // Refresh the mixes list
      fetchMixes();
    } catch (error) {
      console.error("Failed to create mix:", error);
      setError("Failed to create mix. Please try again later.");
      setLoading(false);
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <header className="text-center mb-12">
        <h1 className="text-4xl font-bold text-violet-700 mb-4">Automated DJ</h1>
        <p className="text-xl text-gray-600">Create AI-generated DJ mixes with your favorite music genres</p>
      </header>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Mix Creation Form */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold mb-6">Create a New Mix</h2>
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}
          
          <div className="mb-4">
            <label className="block text-gray-700 mb-2">Mix Title</label>
            <input
              type="text"
              value={mixTitle}
              onChange={(e) => setMixTitle(e.target.value)}
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-violet-500"
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 mb-2">Genre</label>
            <select
              value={selectedGenre}
              onChange={(e) => setSelectedGenre(e.target.value)}
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-violet-500"
            >
              {genres.map((genre) => (
                <option key={genre} value={genre}>
                  {genre}
                </option>
              ))}
            </select>
          </div>
          
          <button
            onClick={createMix}
            disabled={loading || !selectedGenre}
            className={`w-full py-2 px-4 rounded-md text-white font-medium ${
              loading || !selectedGenre
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-violet-600 hover:bg-violet-700"
            }`}
          >
            {loading ? "Creating Mix..." : "Create Mix"}
          </button>
          
          {currentMix && currentMixStatus === "processing" && (
            <div className="mt-4 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-violet-600 mr-2"></div>
              <p className="text-gray-700">Processing your mix... This may take a few minutes.</p>
            </div>
          )}
        </div>
        
        {/* Mix Player */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold mb-6">Your Mixes</h2>
          
          {mixes.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              You haven't created any mixes yet. Create your first mix to get started!
            </p>
          ) : (
            <div className="space-y-4">
              {mixes.map((mix) => (
                <div 
                  key={mix.id} 
                  className={`border p-4 rounded-lg cursor-pointer hover:bg-gray-50 ${
                    currentMix && currentMix.id === mix.id ? "border-violet-500 bg-violet-50" : ""
                  }`}
                  onClick={() => setCurrentMix(mix)}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-medium">{mix.title}</h3>
                      <p className="text-sm text-gray-500">Genre: {mix.genre}</p>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      mix.status === "completed" 
                        ? "bg-green-100 text-green-800" 
                        : mix.status === "processing" 
                        ? "bg-yellow-100 text-yellow-800" 
                        : "bg-gray-100 text-gray-800"
                    }`}>
                      {mix.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {currentMix && currentMix.status === "completed" && (
            <div className="mt-6">
              <h3 className="font-semibold mb-3">Now Playing: {currentMix.title}</h3>
              <audio 
                controls 
                className="w-full" 
                src={`${API}/mixes/${currentMix.id}/stream`}
              >
                Your browser does not support the audio element.
              </audio>
              <div className="mt-2 text-sm text-gray-500">
                <p>Duration: {Math.floor(currentMix.duration / 60)}:{String(Math.floor(currentMix.duration % 60)).padStart(2, "0")}</p>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* How It Works Section */}
      <div className="mt-16">
        <h2 className="text-2xl font-semibold mb-6 text-center">How It Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <div className="bg-violet-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-violet-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-medium mb-2">1. Find Music</h3>
            <p className="text-gray-600">Our system searches for the best tracks in your selected genre.</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <div className="bg-violet-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-violet-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-medium mb-2">2. Analyze Tracks</h3>
            <p className="text-gray-600">We analyze each track to find the best sections and create smooth transitions.</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <div className="bg-violet-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-violet-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
              </svg>
            </div>
            <h3 className="text-xl font-medium mb-2">3. Create Mix</h3>
            <p className="text-gray-600">Our AI DJ creates a seamless mix with professional transitions between tracks.</p>
          </div>
        </div>
      </div>
      
      {/* Footer */}
      <footer className="mt-20 text-center text-gray-500 text-sm">
        <p>© {new Date().getFullYear()} Automated DJ. All rights reserved.</p>
      </footer>
    </div>
  );
};

function App() {
  return (
    <div className="App bg-gray-100 min-h-screen">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />}>
            <Route index element={<Home />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;