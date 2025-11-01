import { Routes, Route } from "react-router-dom";
import { useState } from "react";
import Navbar from "./components/Navbar";
import CitySearch from "./pages/CitySearch";
import CityInsights from "./pages/CityInsights";

function App() {
  const [data, setData] = useState(null);

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-neutral-950 text-neutral-900 dark:text-neutral-100 transition-colors">
      <Navbar />
      <main className="pt-4">
        <Routes>
          <Route path="/" element={<CitySearch onSearch={setData} />} />
          <Route path="/insights" element={<CityInsights data={data} />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
