/**
 * CityInsights Component
 * 
 * Displays AI-analyzed food insights for a city from Reddit discussions.
 * Shows recommendations, complaints, and city overview in a card-based layout.
 * 
 * @param {Object} props
 * @param {Object} props.data - Insights data from the API
 * @param {string} props.data.city - City name
 * @param {number} props.data.count - Number of posts analyzed
 * @param {Array} props.data.insights - Array of insight objects
 * @param {string} props.data.error - Error message if any
 */

import { Card, CardContent } from "@/components/ui/card";
import { motion } from "framer-motion";

export default function CityInsights({ data }) {
  // Handle case when no data is available (user hasn't searched yet)
  if (!data) {
    return (
      <div className="flex items-center justify-center h-[80vh] text-neutral-500">
        No data found. Please search a city first.
      </div>
    );
  }

  // Handle error responses from the backend API
  // Shows user-friendly error message with option to try another city
  if (data.error) {
    return (
      <div className="flex flex-col items-center justify-center h-[80vh] text-center px-6">
        <div className="max-w-md">
          <h2 className="text-2xl font-bold text-red-600 dark:text-red-400 mb-4">
            ⚠️ Error
          </h2>
          <p className="text-neutral-700 dark:text-neutral-300 mb-6">
            {data.error}
          </p>
          <a
            href="/"
            className="inline-block px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:opacity-90 transition"
          >
            Try Another City
          </a>
        </div>
      </div>
    );
  }

  // Main insights display with fade-in animation
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
      className="p-6 max-w-6xl mx-auto space-y-6"
    >
      {/* Header Section - City name and post count */}
      <div className="text-center space-y-2 mb-8">
        <h2 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
          {data.city.charAt(0).toUpperCase() + data.city.slice(1)}
        </h2>
        <p className="text-neutral-600 dark:text-neutral-400">
          Food insights from {data.count} local discussions
        </p>
      </div>

      {/* Insights Cards Grid - Responsive layout */}
      {/* Each card represents one Reddit post with AI-generated insights */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {data.insights.map((item, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            // Staggered animation for each card
            transition={{ duration: 0.5, delay: i * 0.1 }}
          >
            <Card className="h-full flex flex-col border-neutral-200 dark:border-neutral-800 shadow-md hover:shadow-lg transition-shadow">
              {/* Card Header */}
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/30 dark:to-purple-950/30 p-4 border-b border-neutral-200 dark:border-neutral-800">
                <h3 className="text-base font-bold text-neutral-900 dark:text-white line-clamp-2">
                  {item.title}
                </h3>
              </div>

              <CardContent className="p-4 flex-1 flex flex-col space-y-4">
                {/* City Overview */}
                {item.summary?.city_overview && (
                  <p className="text-sm text-neutral-600 dark:text-neutral-400 italic">
                    "{item.summary.city_overview}"
                  </p>
                )}

                {/* Top Recommendations */}
                {item.summary?.top_recommendations?.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-sm font-semibold text-green-700 dark:text-green-400 flex items-center gap-1">
                      <span>🍽️</span> Must Try
                    </h4>
                    <div className="space-y-2">
                      {item.summary.top_recommendations.slice(0, 3).map((rec, j) => (
                        <div
                          key={j}
                          className="p-2 rounded-lg bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800"
                        >
                          <p className="text-sm font-bold text-neutral-900 dark:text-white">
                            {rec.popular_dish}
                          </p>
                          {rec.restaurant_name && rec.restaurant_name !== `${data.city} Local Favorites` && (
                            <p className="text-xs text-green-700 dark:text-green-300">
                              at {rec.restaurant_name}
                            </p>
                          )}
                          <p className="text-xs text-neutral-600 dark:text-neutral-400 mt-1">
                            {rec.reason}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Complaints */}
                {item.summary?.major_complaints?.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-sm font-semibold text-red-700 dark:text-red-400 flex items-center gap-1">
                      <span>⚠️</span> Be Aware
                    </h4>
                    <div className="space-y-2">
                      {item.summary.major_complaints.slice(0, 2).map((complaint, j) => (
                        <div
                          key={j}
                          className="p-2 rounded-lg bg-red-50 dark:bg-red-950/20 border-l-2 border-red-500"
                        >
                          <p className="text-xs font-semibold text-neutral-900 dark:text-white">
                            {complaint.restaurant_name}
                          </p>
                          <p className="text-xs text-neutral-600 dark:text-neutral-400">
                            {complaint.issue}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Reddit Link */}
                <div className="mt-auto pt-3 border-t border-neutral-200 dark:border-neutral-800">
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
                  >
                    <span>View discussion</span>
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
