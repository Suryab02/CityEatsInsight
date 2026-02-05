import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";

export default function CitySearch({ onSearch }) {
  const [city, setCity] = useState("");
  const [loading, setLoading] = useState(false);
  const [detecting, setDetecting] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [recentCities, setRecentCities] = useState([]);
  const [activeIndex, setActiveIndex] = useState(-1);
  const navigate = useNavigate();
  const containerRef = useRef(null);

  const trendingCities = [
    "Delhi",
    "Mumbai",
    "Bangalore",
    "Hyderabad",
    "Chennai",
    "Pune",
    "Kolkata",
    "Ahmedabad",
  ];


  // Use localhost for local development, production URL otherwise
  const API_BASE_URL = import.meta.env.DEV
    ? "http://localhost:8000"
    : "https://cityeatsinsight-backend.vercel.app"


  // Load recent cities
  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem("recentCities")) || [];
    setRecentCities(stored);
  }, []);

  // Fetch suggestions (debounced)
  useEffect(() => {
    if (city.trim().length < 2) {
      setSuggestions([]);
      return;
    }

    const fetchSuggestions = async () => {
      try {
        const res = await fetch(
          `${API_BASE_URL}/city_suggestions/${city.toLowerCase()}`
        );
        const data = await res.json();
        setSuggestions(data.results || []);
      } catch (err) {
        console.error("Error fetching suggestions:", err);
      }
    };

    const delay = setTimeout(fetchSuggestions, 400);
    return () => clearTimeout(delay);
  }, [city]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setSuggestions([]);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Add to recent cities
  const addToRecent = (selectedCity) => {
    let updated = [selectedCity, ...recentCities.filter((c) => c !== selectedCity)];
    if (updated.length > 5) updated = updated.slice(0, 5);
    setRecentCities(updated);
    localStorage.setItem("recentCities", JSON.stringify(updated));
  };

  const handleSelectCity = (selectedCity) => {
    setCity(selectedCity);
    setSuggestions([]);
    addToRecent(selectedCity);
    handleSearch(selectedCity);
  };

  const handleSearch = async (selected) => {
    const searchCity = selected || city;
    if (!searchCity.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(
        `${API_BASE_URL}/insights/${searchCity.toLowerCase()}`
      );
      const data = await res.json();
      onSearch(data);
      navigate("/insights");
    } catch (err) {
      console.error("Error fetching city insights:", err);
    } finally {
      setLoading(false);
    }
  };

  // Keyboard navigation
  const handleKeyDown = (e) => {
    if (suggestions.length === 0) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex((prev) => (prev + 1) % suggestions.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((prev) =>
        prev === 0 ? suggestions.length - 1 : prev - 1
      );
    } else if (e.key === "Enter") {
      if (activeIndex >= 0) {
        e.preventDefault();
        handleSelectCity(suggestions[activeIndex]);
      } else {
        handleSearch();
      }
    }
  };

  // 🌍 Auto Detect Location
  const handleDetectLocation = async () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser.");
      return;
    }

    setDetecting(true);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const { latitude, longitude } = pos.coords;
          const res = await fetch(
            `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${latitude}&longitude=${longitude}&localityLanguage=en`
          );
          const data = await res.json();

          const detectedCity =
            data.city || data.locality || data.principalSubdivision;

          if (detectedCity) {
            setCity(detectedCity);
            console.log("Detected city:", detectedCity);
          } else {
            alert("Could not detect city accurately.");
          }
        } catch (error) {
          console.error("Error detecting city:", error);
        } finally {
          setDetecting(false);
        }
      },
      (err) => {
        console.error("Location access denied:", err);
        alert("Please allow location access to auto-detect your city.");
        setDetecting(false);
      }
    );
  };

  return (
    <div
      className="flex flex-col items-center justify-center min-h-[90vh] px-6 text-center relative"
      ref={containerRef}
    >
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent"
      >
        Discover Food Spots 🍛
      </motion.h1>

      <p className="text-lg text-neutral-600 dark:text-neutral-400 max-w-xl mb-12">
        Explore food culture and restaurant insights from Reddit discussions worldwide.
      </p>

      {/* Input + Search + Auto Detect */}
      <div className="flex w-full max-w-lg flex-col gap-3 relative">
        <div className="flex gap-3">
          <Input
            placeholder="Enter a city (e.g. Hyderabad, Paris, Tokyo)"
            value={city}
            onChange={(e) => {
              setCity(e.target.value);
              setActiveIndex(-1);
            }}
            onKeyDown={handleKeyDown}
            className="flex-1 h-12 text-base shadow-sm"
          />
          <Button
            onClick={() => handleSearch()}
            disabled={loading}
            className="h-12 px-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:opacity-90 shadow-md"
          >
            {loading ? "Searching..." : "Search"}
          </Button>
        </div>

        <Button
          variant="outline"
          onClick={handleDetectLocation}
          disabled={detecting}
          className="text-sm h-10 shadow-sm"
        >
          {detecting ? "Detecting..." : "📍 Detect My Location"}
        </Button>

        {/* Dropdown suggestions */}
        {suggestions.length > 0 && (
          <ul className="absolute top-full mt-2 w-full bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-lg shadow-lg z-10 text-left max-h-60 overflow-y-auto">
            {suggestions.map((s, i) => (
              <li
                key={i}
                onClick={() => handleSelectCity(s)}
                className={`px-4 py-3 cursor-pointer text-sm transition-colors ${i === activeIndex
                    ? "bg-neutral-100 dark:bg-neutral-800"
                    : "hover:bg-neutral-50 dark:hover:bg-neutral-800"
                  }`}
              >
                {s}
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Trending Cities */}
      <motion.div
        className="mt-16"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <p className="text-sm text-neutral-500 mb-4">🔥 Trending Cities</p>
        <div className="flex flex-wrap justify-center gap-3">
          {trendingCities.map((cityName) => (
            <motion.button
              key={cityName}
              onClick={() => handleSelectCity(cityName)}
              whileHover={{ scale: 1.05 }}
              className="px-5 py-2.5 bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-200 rounded-full text-sm font-medium hover:bg-neutral-200 dark:hover:bg-neutral-700 transition-all shadow-sm"
            >
              {cityName}
            </motion.button>
          ))}
        </div>
      </motion.div>

      {/* Recently Searched */}
      {recentCities.length > 0 && (
        <motion.div
          className="mt-12"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <p className="text-sm text-neutral-500 mb-4">🕒 Recently Searched</p>
          <div className="flex flex-wrap justify-center gap-3">
            {recentCities.map((recent, i) => (
              <motion.button
                key={i}
                onClick={() => handleSelectCity(recent)}
                whileHover={{ scale: 1.05 }}
                className="px-5 py-2.5 bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-200 rounded-full text-sm font-medium hover:bg-neutral-200 dark:hover:bg-neutral-700 transition-all shadow-sm"
              >
                {recent}
              </motion.button>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
