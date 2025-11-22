import { useState } from "react";
import { motion } from "framer-motion";
import { Search, MapPin, TrendingUp } from "lucide-react";
import CityInsights from "./CityInsights";
import CityInsightsSkeleton from "@/components/CityInsightsSkeleton";

export default function Home() {
  const [city, setCity] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const API_BASE_URL = "https://cityeatsinsight-backend.vercel.app";

  const fetchInsights = async () => {
    if (!city.trim()) return;
    
    setLoading(true);
    setData(null);
    setError(null);
    
    try {
      const res = await fetch(`${API_BASE_URL}/insights/${city}`);
      if (!res.ok) throw new Error("Failed to fetch insights");
      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error("Error fetching:", err);
      setError("Failed to load insights. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      fetchInsights();
    }
  };

  const popularCities = ["Hyderabad", "Bangalore", "Mumbai", "Delhi", "Chennai"];

  const handleCityClick = (cityName) => {
    setCity(cityName);
    setData(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800">
      <div className="max-w-6xl mx-auto px-4 py-12 space-y-8">
        {/* Header Section */}
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6 }}
          className="text-center space-y-4"
        >
          <h1 className="text-5xl sm:text-6xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
            CityEatsInsight
          </h1>
          <p className="text-neutral-600 dark:text-neutral-400 text-lg max-w-2xl mx-auto">
            Discover authentic food recommendations powered by real discussions from local Reddit communities
          </p>
        </motion.div>

        {/* Search Section */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="max-w-2xl mx-auto space-y-4"
        >
          <div className="flex items-center gap-3 bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-2">
            <div className="flex items-center gap-2 flex-1">
              <MapPin className="h-5 w-5 text-neutral-400 ml-3" />
              <input
                value={city}
                onChange={(e) => setCity(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter a city (e.g., Hyderabad, Bangalore)"
                className="flex-1 bg-transparent border-none outline-none px-2 py-3 text-neutral-900 dark:text-white placeholder:text-neutral-400"
              />
            </div>
            <button
              onClick={fetchInsights}
              disabled={!city.trim() || loading}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-medium transition-all shadow-md hover:shadow-lg"
            >
              <Search className="h-5 w-5" />
              <span className="hidden sm:inline">Search</span>
            </button>
          </div>

          {/* Popular Cities */}
          <div className="flex flex-wrap items-center justify-center gap-2">
            <span className="text-sm text-neutral-500 dark:text-neutral-400 flex items-center gap-1">
              <TrendingUp className="h-4 w-4" />
              Popular:
            </span>
            {popularCities.map((cityName) => (
              <button
                key={cityName}
                onClick={() => handleCityClick(cityName)}
                className="px-3 py-1.5 text-sm bg-white dark:bg-gray-800 border border-neutral-200 dark:border-neutral-700 rounded-full hover:border-purple-400 dark:hover:border-purple-600 hover:text-purple-600 dark:hover:text-purple-400 transition-colors"
              >
                {cityName}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Error Message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-2xl mx-auto"
          >
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-center">
              <p className="text-red-600 dark:text-red-400">{error}</p>
            </div>
          </motion.div>
        )}

        {/* Loading State */}
        {loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <CityInsightsSkeleton />
          </motion.div>
        )}

        {/* Results */}
        {!loading && data && <CityInsights data={data} />}

        {/* Empty State */}
        {!loading && !data && !error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-center py-20"
          >
            <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900/20 dark:to-purple-900/20 rounded-full flex items-center justify-center">
              <Search className="h-12 w-12 text-purple-600 dark:text-purple-400" />
            </div>
            <h3 className="text-xl font-semibold text-neutral-900 dark:text-white mb-2">
              Ready to explore?
            </h3>
            <p className="text-neutral-600 dark:text-neutral-400">
              Enter a city name to discover the best food spots based on real local insights
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
