from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pickle
import pandas as pd
import os

app = FastAPI(title="Movie Recommendation API")

# Setup CORS to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data at startup
try:
    dict_path = os.path.join(os.path.dirname(__file__), '..', 'movies_dict.pkl')
    sim_path = os.path.join(os.path.dirname(__file__), '..', 'similarity16.pkl')
    
    with open(dict_path, 'rb') as f:
        movies_dict = pickle.load(f)
    movies = pd.DataFrame(movies_dict)
    
    with open(sim_path, 'rb') as f:
        similarity = pickle.load(f)
        
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    movies = pd.DataFrame()
    similarity = []

@app.get("/")
def read_root():
    return {"message": "Movie Recommendation API is running!"}

@app.get("/movies")
def get_movie_list():
    """Returns a list of all movie titles for the dropdown."""
    if movies.empty:
        raise HTTPException(status_code=500, detail="Movies data not loaded")
    return {"movies": movies['title'].tolist()}

@app.get("/recommend/{movie}")
def recommend(movie: str):
    """Returns 5 recommended movies based on the input movie."""
    if movies.empty:
        raise HTTPException(status_code=500, detail="Data not loaded properly.")
    
    try:
        # Find index of the movie
        mov_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        raise HTTPException(status_code=404, detail="Movie not found in the dataset.")
        
    distances = similarity[mov_index]
    # Enumerate and sort by similarity score
    mov_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommendations = []
    for i in mov_list:
        idx = i[0]
        recommendations.append({
            "id": int(movies.iloc[idx].id),
            "title": str(movies.iloc[idx].title)
        })
        
    return {"recommendations": recommendations}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
