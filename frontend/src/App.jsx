import { useState, useEffect } from 'react'
import './App.css'

const TMDB_API_KEY = '8265bd1679663a7ea12ac168da84d2e8';

function App() {
  const [movies, setMovies] = useState([])
  const [selectedMovie, setSelectedMovie] = useState('')
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchMovies()
  }, [])

  const fetchMovies = async () => {
    try {
      const response = await fetch('/api/movies')
      if (!response.ok) throw new Error('Failed to fetch movies')
      const data = await response.json()
      setMovies(data.movies)
    } catch (err) {
      setError('Could not connect to the API. Are you running the backend server?')
    }
  }

  const fetchPoster = async (movieId) => {
    try {
      const response = await fetch(`https://api.themoviedb.org/3/movie/${movieId}?api_key=${TMDB_API_KEY}&language=en-US`);
      const data = await response.json();
      return data.poster_path ? `https://image.tmdb.org/t/p/w500${data.poster_path}` : null;
    } catch (err) {
      return null;
    }
  }

  const handleRecommend = async () => {
    if (!selectedMovie) return
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`/api/recommend/${encodeURIComponent(selectedMovie)}`)
      if (!response.ok) throw new Error('Recommendation failed (Movie might not exist)')
      const data = await response.json()
      
      const recsWithPosters = await Promise.all(
        data.recommendations.map(async (rec) => {
          const posterUrl = await fetchPoster(rec.id);
          return { ...rec, posterUrl };
        })
      );
      
      setRecommendations(recsWithPosters)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <div className="glass-panel">
        <h1 className="title">CineMatch AI</h1>
        <p className="subtitle">Discover your next cinematic journey.</p>
        
        <div className="input-group">
          <input 
            type="text"
            list="movies-list"
            value={selectedMovie} 
            onChange={(e) => setSelectedMovie(e.target.value)}
            className="movie-select"
            placeholder="Type a movie name..."
          />
          <datalist id="movies-list">
            {movies.map((m, idx) => (
              <option key={idx} value={m} />
            ))}
          </datalist>

          <button 
            onClick={handleRecommend} 
            disabled={!selectedMovie || loading || movies.length === 0}
            className="recommend-btn"
          >
            {loading ? 'Analyzing...' : 'Recommend'}
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {recommendations.length > 0 && (
          <div className="recommendations-container">
            <h2 className="recommendations-title">We recommend:</h2>
            <div className="movie-grid">
              {recommendations.map((rec) => (
                <div key={rec.id} className="movie-card">
                  {rec.posterUrl ? (
                    <img src={rec.posterUrl} alt={rec.title} className="movie-poster" />
                  ) : (
                    <div className="movie-poster-placeholder">
                      <span>No Poster</span>
                    </div>
                  )}
                  <h3 className="movie-card-title">{rec.title}</h3>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
