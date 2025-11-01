import { Skeleton } from "@/components/ui/skeleton";

export default function CityInsightsSkeleton() {
  return (
    <div className="max-w-2xl mx-auto p-4 space-y-4">
      <div className="space-y-2 text-center">
        <Skeleton className="h-8 w-1/2 mx-auto bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 animate-pulse" />
        <Skeleton className="h-4 w-3/4 mx-auto" />
      </div>

      {[...Array(3)].map((_, i) => (
        <div key={i} className="border rounded-xl p-4 bg-white shadow-sm">
          <Skeleton className="h-5 w-3/4 mb-2" />
          <Skeleton className="h-4 w-full mb-1" />
          <Skeleton className="h-4 w-2/3" />
        </div>
      ))}
    </div>
  );
}
