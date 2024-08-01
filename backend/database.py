
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException
import asyncio
from bson import json_util
import json


# Replace with your MongoDB connection string (environment variable recommended)
MONGODB_URL = "mongodb+srv://ajiteshdasgupta04:5YK9NKIQfA65cMuy@cluster0.fnv7urt.mongodb.net/bookmymovie?retryWrites=true&w=majority&appName=Cluster0"


class Database:
    client: AsyncIOMotorClient



    def __init__(self):
        self.client = AsyncIOMotorClient(MONGODB_URL)
        self.db = self.client["bookmymovie"]  # Replace with your database name

    async def close(self):
        await self.client.close()

    async def get_collection(self, collection_name):
        """Fetches a collection object from the database"""
        return self.db[collection_name]

    async def find_all(self, collection_name, filter: dict = None):
        """Finds all documents in a collection (optionally with filter)"""
        collection = await self.get_collection(collection_name)
        return await collection.find(filter=filter).to_list()

    async def find_by_id(self, collection_name, document_id):
        """Finds a document by its id in a collection"""
        collection = await self.get_collection(collection_name)
        return await collection.find_one({"_id": document_id})
    
    async def find_cities(self):
        """Finds only the city of the Cinema Hall"""
        collection = await self.get_collection("Cinema_Hall")
        pipeline = [
            {"$project": {"city": "$hall_location.city"}},
            {"$group": {"_id": "$city"}},
            {"$project": {"city": "$_id"}},
            {"$unwind": "$city"},
        ]
        cursor = collection.aggregate(pipeline)
        result = await cursor.to_list(length=1000)  # Materialize the cursor
        cities = [city["city"] for city in result]
        return cities
    

    async def find_shows_by_city(self, city):
        """Find Shows by City"""
        collection = await self.get_collection("Shows")
        pipeline = [
            {
                "$lookup": {
                    "from": "Cinema_Hall",
                    "localField": "cinema_hall_id",
                    "foreignField": "_id",
                    "as": "hall_details"
                }
            },
            {
                "$unwind": "$hall_details"
            },
            {
                "$lookup": {
                    "from": "Movie",
                    "localField": "movie_id",
                    "foreignField": "_id",
                    "as": "movie_details"
                }
            },
            {
                "$unwind": "$movie_details"
            },
            {
                "$match": {
                    "hall_details.hall_location.city": city
                }
            },
            {"$project": {"_id": 0}}

        ]
        cursor = collection.aggregate(pipeline)
        result = await cursor.to_list(length=30)  # Materialize the cursor
        result = json.loads(json_util.dumps(result))
        return result
        

    async def insert_one(self, collection_name, data):
        """Inserts a single document into a collection"""
        collection = await self.get_collection(collection_name)
        result = await collection.insert_one(data)
        return result.inserted_id

    async def insert_many(self, collection_name, data):
        """Inserts multiple documents into a collection"""
        collection = await self.get_collection(collection_name)
        movie_dicts = [movie.dict() for movie in data]
        print (movie_dicts)
        result = await collection.insert_many(movie_dicts)
        inserted_ids = [str(doc_id) for doc_id in result.inserted_ids]
        return inserted_ids
    
    async def update(self, collection_name, document_id, update_data):
        """Updates a document by its id in a collection"""
        collection = await self.get_collection(collection_name)
        await collection.update_one({"_id": document_id}, {"$set": update_data})

    async def delete(self, collection_name, document_id):
        """Deletes a document by its id in a collection"""
        collection = await self.get_collection(collection_name)
        result = await collection.delete_one({"_id": document_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Document not found")

    async def health_check(self):
        """Performs a simple health check on the database connection"""
        try:
            # Attempt a simple database operation (e.g., get one document)
            await self.find_one("Movie", {})  # Replace "items" with your actual collection
            return {"message": "Database connection OK"}
        except Exception as e:
            return {"message": f"Database connection error: {str(e)}"}

database = Database()


