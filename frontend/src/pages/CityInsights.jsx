import { Card, CardContent } from "@/components/ui/card";
import { motion } from "framer-motion";

export default function CityInsights({ data }) {
  if (!data) {
    return (
      <div className="flex items-center justify-center h-[80vh] text-neutral-500">
        No data found. Please search a city first.
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
      className="p-6 max-w-5xl mx-auto space-y-8"
    >
      <h2 className="text-3xl font-bold text-center mb-4 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
        {data.city.toUpperCase()} — Food Insights 🍴
      </h2>

      <p className="text-base text-center text-neutral-600 dark:text-neutral-400 mb-8 max-w-2xl mx-auto">
        Discover where locals eat, which restaurants stand out, and what food trends are buzzing in this city.
      </p>

      <div className="space-y-6">
        {data.insights.map((item, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: i * 0.1 }}
          >
            <Card className="border border-neutral-200 dark:border-neutral-800 rounded-2xl shadow-sm hover:shadow-md transition bg-white/80 dark:bg-neutral-900/60 backdrop-blur-sm">
              <CardContent className="p-5">
                <h3 className="font-semibold text-lg text-neutral-800 dark:text-neutral-100 mb-2">
                  {item.title}
                </h3>

                <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-3 leading-relaxed">
                  {item.summary.city_overview}
                </p>

                {item.summary.top_recommendations?.length > 0 && (
                  <ul className="list-disc pl-5 space-y-1">
                    {item.summary.top_recommendations.map((rec, j) => (
                      <li key={j} className="text-neutral-700 dark:text-neutral-300">
                        <strong>{rec.restaurant_name}</strong> — {rec.popular_dish}  
                        <span className="text-neutral-500"> ({rec.reason})</span>
                      </li>
                    ))}
                  </ul>
                )}

                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 dark:text-blue-400 mt-3 inline-block hover:underline"
                >
                  View on Reddit ↗
                </a>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
