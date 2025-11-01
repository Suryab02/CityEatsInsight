import { useState } from "react";
import { motion } from "framer-motion";
import { Search } from "lucide-react";
import CityInsights from "./CityInsights";
import CityInsightsSkeleton from "@/components/CityInsightsSkeleton";

export default function Home() {
  const [city, setCity] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchInsights = async () => {
    if (!city.trim()) return;
    setLoading(true);
    setData(null);
    try {
      const res = await fetch(`http://localhost:8000/insights/${city}`);
      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error("Error fetching:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
      className="min-h-screen bg-gradient-to-b from-neutral-50 to-white text-gray-900"
    >
      <div className="max-w-3xl mx-auto px-4 py-10 space-y-6">
        <motion.div
          initial={{ y: 10, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="text-center space-y-2"
        >
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight">
            CityEats 🍽️
          </h1>
          <p className="text-gray-600 text-sm sm:text-base">
            Discover the best and worst food spots from real Reddit chatter
          </p>
        </motion.div>

        <div className="flex items-center gap-2 justify-center">
          <input
            value={city}
            onChange={(e) => setCity(e.target.value)}
            placeholder="Enter a city (e.g. Hyderabad)"
            className="border border-gray-300 rounded-lg px-4 py-2 w-3/4 focus:ring-2 focus:ring-black text-sm sm:text-base"
          />
          <button
            onClick={fetchInsights}
            className="bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-900 flex items-center gap-2 transition"
          >
            <Search className="h-4 w-4" />
            Search
          </button>
        </div>

        {loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <CityInsightsSkeleton />
          </motion.div>
        )}

        {!loading && data && <CityInsights data={data} />}
      </div>
    </motion.div>
  );
}
