from enum import Enum
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
from database import database

app = FastAPI()


class Movies (BaseModel):
    _id: str
    movie_name: str
    cast: List[str] = []
    crew: dict = {}
    date_of_release: datetime

@app.get("/health")
async def health_check():
    try:
        # Attempt a simple database operation (e.g., get one document)
        await database.find_one("Movie", {})  # Replace "items" with your actual collection
        return {"message": "Database connection OK"}
    except Exception as e:
        return {"message": f"Database connection error: {str(e)}"}
 



@app.post("/newMovie")
async def add_movie(movie_data: Movies):
    new_id = await database.insert_one("Movie", movie_data.dict())
    return {"id": new_id, "message" : "Movie inserted successfully!"}