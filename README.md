# CityEatsInsight 🍛

**Discover food culture and restaurant insights from Reddit discussions worldwide.**

CityEatsInsight is a full-stack web application that analyzes Reddit discussions to provide AI-powered food recommendations for cities around the world. It fetches recent posts from city-specific subreddits, filters for food-related content, and uses Google Gemini AI to generate structured insights.

## ✨ Features

- 🔍 **Smart City Search** - Autocomplete suggestions for cities worldwide
- 📍 **Location Detection** - Auto-detect your current city
- 🤖 **AI-Powered Analysis** - Google Gemini AI summarizes Reddit discussions
- ⏱️ **Recent Data Only** - Fetches posts from the last 6 months for fresh recommendations
- 💾 **Intelligent Caching** - 6-hour cache to reduce API calls and improve performance
- 🎨 **Beautiful UI** - Modern, responsive design with dark mode support
- 🔄 **Fallback Mechanism** - Simple NLP analyzer when AI quota is exceeded

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **Reddit Scraper** - Fetches food-related posts using PRAW (Python Reddit API Wrapper)
- **NLP Analyzer** - Sentiment analysis and entity extraction using TextBlob
- **AI Integration** - Google Gemini AI for intelligent summarization
- **Caching System** - Time-based caching with automatic expiry
- **REST API** - FastAPI with CORS support for frontend integration

### Frontend (React + Vite)
- **React 19** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **Framer Motion** - Smooth animations
- **Radix UI** - Accessible component primitives

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** - For backend
- **Node.js 16+** - For frontend
- **Reddit API Credentials** - Create an app at [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
- **Google Gemini API Key** - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Backend Setup

1. **Navigate to Backend directory**
   ```bash
   cd Backend
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file** with your API credentials
   ```env
   # Reddit API Credentials
   REDDIT_CLIENT_ID=your_reddit_client_id
   REDDIT_CLIENT_SECRET=your_reddit_client_secret
   USER_AGENT=CityEatsInsight/1.0

   # Google Gemini API Key
   GEMINI_API_KEY=your_gemini_api_key
   ```

5. **Run the backend server**
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to Frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Run the development server**
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:5173`

## 📚 API Documentation

### Endpoints

#### `GET /health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "ok",
  "service": "CityEatsInsight Backend"
}
```

#### `GET /city/{name}`
Get raw Reddit posts for a city without AI analysis.

**Parameters:**
- `name` (path) - City name

**Response:**
```json
{
  "city": "hyderabad",
  "posts": [
    {
      "title": "Best biryani places?",
      "url": "https://reddit.com/r/hyderabad/...",
      "score": 245,
      "comments_text": "Try Paradise..."
    }
  ],
  "count": 10
}
```

#### `GET /insights/{city}`
Get AI-analyzed food insights for a city (main endpoint).

**Parameters:**
- `city` (path) - City name

**Response:**
```json
{
  "city": "hyderabad",
  "insights": [
    {
      "title": "Best biryani places?",
      "url": "https://reddit.com/r/hyderabad/...",
      "score": 245,
      "summary": {
        "city_overview": "Hyderabad discussions focus on biryani and local cafes",
        "top_recommendations": [
          {
            "category": "Biryani",
            "restaurant_name": "Paradise",
            "popular_dish": "Chicken Biryani",
            "reason": "Authentic flavor and generous portions"
          }
        ],
        "major_complaints": []
      }
    }
  ],
  "count": 5
}
```

#### `GET /city_suggestions/{query}`
Get city autocomplete suggestions.

**Parameters:**
- `query` (path) - Search query

**Response:**
```json
{
  "results": ["Hyderabad", "Ahmedabad", "Secunderabad"]
}
```

## 🔧 Configuration

### Time Filtering
By default, the scraper fetches posts from the last **6 months**. You can adjust this in `reddit_scraper.py`:

```python
MONTHS_TO_SEARCH = 6  # Change this value
```

### Cache Expiry
Cache expires after **6 hours** by default. Adjust in `cache_manager.py`:

```python
CACHE_EXPIRY_HOURS = 6  # Change this value
```

### AI Model
The app uses **Gemini 2.0 Flash** by default. Change in `google_genai.py`:

```python
model = genai.GenerativeModel("gemini-2.0-flash")  # Change model here
```

## 📁 Project Structure

```
CityEatsInsight/
├── Backend/
│   ├── main.py                 # FastAPI app and endpoints
│   ├── reddit_scraper.py       # Reddit data fetching with time filtering
│   ├── google_genai.py         # Google Gemini AI integration
│   ├── nlp_analyzer.py         # Sentiment analysis and entity extraction
│   ├── nlp_filter.py           # Data aggregation and JSON cleaning
│   ├── simple_analyzer.py      # Fallback NLP analyzer
│   ├── cache_manager.py        # Caching system
│   ├── requirements.txt        # Python dependencies
│   └── data/
│       └── cities.json         # List of cities for autocomplete
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── CitySearch.jsx  # Search page with autocomplete
│   │   │   └── CityInsights.jsx # Results page
│   │   ├── components/         # Reusable UI components
│   │   └── App.jsx             # Main app component
│   ├── package.json            # Node dependencies
│   └── vite.config.js          # Vite configuration
└── README.md                   # This file
```

## 🐛 Troubleshooting

### "cities.json not found" warning
- Make sure `Backend/data/cities.json` exists
- The file should contain a JSON array of city names

### Reddit API errors
- Check your Reddit API credentials in `.env`
- Ensure your Reddit app is set to "script" type
- Verify you're not hitting rate limits (60 requests/minute)

### Gemini API quota exceeded
- The app automatically falls back to simple NLP analyzer
- Consider upgrading your Gemini API quota
- Reduce the number of posts analyzed (change `posts[:5]` in `main.py`)

### No posts found for a city
- Verify the city has an active subreddit (e.g., r/hyderabad)
- Try a different city name
- Check if the subreddit has recent food-related posts

## 🚢 Deployment

### Backend (Vercel)
The backend is configured for Vercel serverless deployment:
- `vercel.json` is already configured
- Deploy with: `vercel --prod`

### Frontend (Vercel)
- Deploy with: `vercel --prod` from the frontend directory
- Update `FRONTEND_URL` environment variable in backend

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Reddit** - For providing the PRAW API
- **Google** - For Gemini AI API
- **TextBlob** - For sentiment analysis
- **FastAPI** - For the excellent Python web framework
- **React & Vite** - For the modern frontend stack
