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
      {/* Header */}
      <div className="text-center space-y-2 mb-10">
        <h2 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
          {data.city.charAt(0).toUpperCase() + data.city.slice(1)}
        </h2>
        <p className="text-neutral-600 dark:text-neutral-400">
          Food insights from {data.count} local discussions
        </p>
      </div>

      {/* Insights Cards */}
      <div className="space-y-8">
        {data.insights.map((item, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: i * 0.1 }}
          >
            <Card className="overflow-hidden border-neutral-200 dark:border-neutral-800 shadow-lg">
              {/* Card Header with gradient background */}
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/30 dark:to-purple-950/30 p-6 border-b border-neutral-200 dark:border-neutral-800">
                <h3 className="text-xl font-bold text-neutral-900 dark:text-white mb-2">
                  {item.title}
                </h3>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">
                  {item.summary.city_overview}
                </p>
              </div>

              <CardContent className="p-6 space-y-6">
                {/* Top Recommendations - Card Grid Style */}
                {item.summary.top_recommendations?.length > 0 && (
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <div className="h-8 w-1 bg-green-500 rounded-full"></div>
                      <h4 className="text-lg font-semibold text-neutral-900 dark:text-white">
                        Must Try Places
                      </h4>
                    </div>
                    
                    <div className="grid gap-4 md:grid-cols-2">
                      {item.summary.top_recommendations.map((rec, j) => (
                        <motion.div
                          key={j}
                          initial={{ opacity: 0, scale: 0.95 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: 0.2 + j * 0.05 }}
                          className="relative p-4 rounded-xl bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20 border border-green-200 dark:border-green-800 hover:shadow-md transition-shadow"
                        >
                          {/* Restaurant Name */}
                          <div className="mb-2">
                            <h5 className="font-bold text-neutral-900 dark:text-white text-base">
                              {rec.restaurant_name}
                            </h5>
                            {rec.category && (
                              <span className="text-xs text-green-700 dark:text-green-300 font-medium">
                                {rec.category}
                              </span>
                            )}
                          </div>

                          {/* Popular Dish */}
                          <div className="mb-3">
                            <p className="text-sm font-medium text-neutral-800 dark:text-neutral-200">
                              🍽️ {rec.popular_dish}
                            </p>
                          </div>

                          {/* Reason */}
                          <div className="pt-3 border-t border-green-200 dark:border-green-800/50">
                            <p className="text-xs text-neutral-600 dark:text-neutral-400 italic">
                              "{rec.reason}"
                            </p>
                          </div>

                          {/* Corner decoration */}
                          <div className="absolute top-3 right-3 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
                            ✓
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Complaints - Simple Alert Style */}
                {item.summary.major_complaints?.length > 0 && (
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <div className="h-8 w-1 bg-red-500 rounded-full"></div>
                      <h4 className="text-lg font-semibold text-neutral-900 dark:text-white">
                        Be Aware
                      </h4>
                    </div>
                    
                    <div className="space-y-2">
                      {item.summary.major_complaints.map((complaint, j) => (
                        <div
                          key={j}
                          className="p-3 rounded-lg bg-red-50 dark:bg-red-950/20 border-l-4 border-red-500 dark:border-red-400"
                        >
                          <p className="font-semibold text-neutral-900 dark:text-white text-sm">
                            {complaint.restaurant_name}
                          </p>
                          <p className="text-xs text-neutral-700 dark:text-neutral-300 mt-1">
                            {complaint.issue}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Reddit Link */}
                <div className="pt-4 border-t border-neutral-200 dark:border-neutral-800">
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 text-sm font-medium text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    <span>View full discussion on Reddit</span>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
