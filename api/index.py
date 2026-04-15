from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pickle
import os

app = FastAPI(title="Movie Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to store the data
movies_dict = None
similarity = None
titles_list = []
title_to_index = {}

# We do lazy loading to help with Serverless memory initialization and limits
def load_data():
    global movies_dict, similarity, titles_list, title_to_index
    if movies_dict is not None and similarity is not None:
        return
        
    dict_path = os.path.join(os.path.dirname(__file__), '..', 'movies_dict.pkl')
    sim_path = os.path.join(os.path.dirname(__file__), '..', 'similarity16.pkl')
    
    with open(dict_path, 'rb') as f:
        movies_dict = pickle.load(f)
        
    with open(sim_path, 'rb') as f:
        similarity = pickle.load(f)

    # Build an index lookup for highly optimal Serverless inference
    for idx, title_key in movies_dict['title'].items():
        title_str = str(title_key)
        titles_list.append(title_str)
        title_to_index[title_str] = idx

@app.get("/api/movies")
def get_movie_list():
    try:
        load_data()
        return {"movies": titles_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recommend/{movie}")
def recommend(movie: str):
    try:
        load_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Data not loaded properly.")
    
    if movie not in title_to_index:
        raise HTTPException(status_code=404, detail="Movie not found in the dataset.")
        
    mov_index = title_to_index[movie]
    # To handle float16 or standard iterables
    distances = similarity[mov_index]
    
    # Enumerate and sort by similarity score
    mov_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommendations = []
    for i in mov_list:
        idx = i[0]
        recommendations.append({
            "id": int(movies_dict['id'][idx]),
            "title": str(movies_dict['title'][idx])
        })
        
    return {"recommendations": recommendations}
