import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import Accordionui from './components/Page/shadcn/Accordionui'  
import {Card, CardContent} from "@/components/ui/card";
import { Button } from "@/components/ui/button"


function App() {
  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center p-4">
      <Card className="max-w-md w-full text-center p-6 shadow-lg">
        <CardContent>
          <h1 className="text-2xl font-semibold mb-4">CityEats Insight 🍴</h1>
          <p className="text-muted-foreground mb-4">
            Explore food insights from Indian cities.
          </p>
          <Button>Get Started</Button>
        </CardContent>
      </Card>
    </div>
  );
}

export default App;