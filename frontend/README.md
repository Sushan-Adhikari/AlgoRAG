# AlgoRAG Frontend

React-based frontend for the AlgoRAG system - Retrieval-Augmented Generation for Theoretical Computer Science Education.

## Features

- Clean, intuitive interface for asking algorithm and complexity theory questions
- Real-time query processing with loading states
- Display of retrieved evidence sources with pedagogical scoring
- LaTeX/mathematical notation support via MathJax
- Confidence visualization and source analysis
- Support for different query types (proof, complexity analysis, algorithm explanation)

## Prerequisites

- Node.js 16+ and npm
- Backend API running on http://localhost:8000 (or configure REACT_APP_API_URL)

## Installation

```bash
# Install dependencies
npm install
```

## Running the Application

```bash
# Start development server (runs on http://localhost:3000)
npm start

# Build for production
npm run build

# Run tests
npm test
```

## Configuration

Create a `.env` file in this directory to configure the API endpoint:

```env
REACT_APP_API_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── public/
│   ├── index.html          # HTML template with MathJax
│   ├── manifest.json       # PWA manifest
│   ├── robots.txt
│   └── favicon.ico
├── src/
│   ├── index.js            # React app entry point
│   ├── App.jsx             # Main application component
│   └── App.css             # Styling
├── package.json
└── .env                    # Environment configuration
```

## API Integration

The frontend connects to the backend API at the configured URL and expects:

- `GET /api/health` - Health check endpoint
- `POST /api/query` - Query endpoint accepting:
  ```json
  {
    "question": "Your question here",
    "query_type": "proof|complexity_analysis|algorithm|general",
    "top_k": 5
  }
  ```

## Query Types

- **Auto-detect**: System determines the best query type
- **Proof**: For proof-related questions (prioritizes proof templates)
- **Complexity Analysis**: For time/space complexity questions
- **Algorithm Explanation**: For algorithm understanding
- **General**: For general CS theory questions

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### Port already in use
If port 3000 is busy:
```bash
PORT=3001 npm start
```

### Backend connection issues
1. Ensure backend is running on http://localhost:8000
2. Check CORS is enabled on backend
3. Verify REACT_APP_API_URL in .env file

### MathJax not rendering
- Check browser console for MathJax load errors
- Ensure internet connection (MathJax loads from CDN)

## Development

This project was bootstrapped with Create React App and uses:
- React 18
- Functional components with hooks
- CSS modules for styling
- MathJax 3 for LaTeX rendering
