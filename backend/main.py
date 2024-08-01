from enum import Enum
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
from database import database
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Movies (BaseModel):
    _id: str
    movie_name: str
    cast: List[str] = []
    crew: dict = {}
    date_of_release: datetime
    languages: List[str] = []

@app.get("/health")
async def health_check():
    try:
        # Attempt a simple database operation (e.g., get one document)
        await database.health_check()  # Replace "items" with your actual collection
        return {"message": "Database connection OK"}
    except Exception as e:
        return {"message": f"Database connection error: {str(e)}"}
 

@app.post("/newMovie")
async def add_movie(movie_data: Movies):
    new_id = await database.insert_one("Movie", movie_data.dict())
    return {"id": new_id, "message" : "Movie inserted successfully!"}


@app.post("/newMovies")
async def add_movies(movie_data: list[Movies]):
    inserted_ids = await database.insert_many("Movie", movie_data)
    return {"inserted_ids": inserted_ids, "message" : "Movies inserted successfully!"}


@app.get("/all/cities")
async def get_cities():
    cities = await database.find_cities()
    return cities

@app.get("/all/shows/{city}")
async def get_shows_by_city(city):
    shows_by_city = await database.find_shows_by_city(city)
    return shows_by_city
