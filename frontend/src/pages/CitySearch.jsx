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
    "Jaipur",
    "Goa",
  ];

const API_BASE_URL = "https://cityeatsinsight-backend.vercel.app"


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
      className="flex flex-col items-center justify-center min-h-[90vh] px-4 text-center relative"
      ref={containerRef}
    >
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent"
      >
        Discover India’s Best Food Spots 🍛
      </motion.h1>

      <p className="text-base text-neutral-600 dark:text-neutral-400 max-w-md mb-8">
        Explore food culture, hidden gems, and restaurant insights from Reddit
        discussions in cities across India.
      </p>

      {/* Input + Search + Auto Detect */}
      <div className="flex w-full max-w-md flex-col gap-2 relative">
        <div className="flex gap-2">
          <Input
            placeholder="Enter a city (e.g. Hyderabad, Pune, Delhi)"
            value={city}
            onChange={(e) => {
              setCity(e.target.value);
              setActiveIndex(-1);
            }}
            onKeyDown={handleKeyDown}
            className="flex-1 text-neutral-900 dark:text-neutral-100 placeholder:text-neutral-400 dark:placeholder:text-neutral-500"
          />
          <Button
            onClick={() => handleSearch()}
            disabled={loading}
            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:opacity-90"
          >
            {loading ? "Searching..." : "Search"}
          </Button>
        </div>

        <Button
          variant="outline"
          onClick={handleDetectLocation}
          disabled={detecting}
          className="text-sm mt-1 border-neutral-300 dark:border-neutral-700 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition"
        >
          {detecting ? "Detecting..." : "📍 Detect My Location"}
        </Button>

        {/* Dropdown suggestions */}
        {suggestions.length > 0 && (
          <ul className="absolute top-full mt-1 w-full bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-lg shadow-md z-10 text-left max-h-56 overflow-y-auto">
            {suggestions.map((s, i) => (
              <li
                key={i}
                onClick={() => handleSelectCity(s)}
                className={`px-4 py-2 cursor-pointer text-sm transition-colors duration-150 ${
                  i === activeIndex
                    ? "bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100"
                    : "hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-700 dark:text-neutral-200"
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
        className="mt-10"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <p className="text-sm text-neutral-500 mb-3">🔥 Trending Cities</p>
        <motion.div
          className="flex flex-wrap justify-center gap-2"
          initial="hidden"
          animate="visible"
          variants={{
            hidden: { opacity: 0 },
            visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
          }}
        >
          {trendingCities.map((cityName) => (
            <motion.button
              key={cityName}
              onClick={() => handleSelectCity(cityName)}
              variants={{
                hidden: { opacity: 0, scale: 0.9 },
                visible: { opacity: 1, scale: 1 },
              }}
              whileHover={{ scale: 1.06 }}
              className="px-4 py-2 bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-200 rounded-full text-sm 
              hover:bg-neutral-200 dark:hover:bg-neutral-700 hover:text-neutral-900 dark:hover:text-neutral-100 
              transition-all duration-200 shadow-sm hover:shadow-md"
            >
              {cityName}
            </motion.button>
          ))}
        </motion.div>
      </motion.div>

      {/* Recently Searched */}
      {recentCities.length > 0 && (
        <motion.div
          className="mt-8"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <p className="text-sm text-neutral-500 mb-3">🕒 Recently Searched</p>
          <div className="flex flex-wrap justify-center gap-2">
            {recentCities.map((recent, i) => (
              <motion.button
                key={i}
                onClick={() => handleSelectCity(recent)}
                whileHover={{ scale: 1.05 }}
                className="px-4 py-2 bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-200 rounded-full text-sm 
                hover:bg-neutral-200 dark:hover:bg-neutral-700 hover:text-neutral-900 dark:hover:text-neutral-100 
                transition-all duration-200 shadow-sm hover:shadow-md"
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
