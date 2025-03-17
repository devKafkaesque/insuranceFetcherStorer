from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import requests

class FetchAPITool(BaseTool):
    name: str = "fetch_api_data"
    description: str = "Fetch data from an API endpoint with the given headers"
    
    class Input(BaseModel):
        endpoint: str = Field(..., description="API endpoint URL")
        headers: dict = Field(..., description="Request headers")
    
    def _run(self, endpoint: str, headers: dict) -> dict:
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API request failed with status {response.status_code}")

class StoreMongoTool(BaseTool):
    name: str = "store_in_mongodb"
    description: str = "Store data in a MongoDB collection"
    
    class Input(BaseModel):
        data: list = Field(..., description="Data to store in MongoDB")
        database_uri: str = Field(..., description="MongoDB connection URI")
        collection_name: str = Field(..., description="Name of the MongoDB collection")
    
    def _run(self, data: list, database_uri: str, collection_name: str) -> str:
        from pymongo import MongoClient  # import here to keep the tool self-contained
        client = MongoClient(database_uri)
        db = client.get_database()
        collection = db[collection_name]
        result = collection.insert_many(data)
        client.close()
        return f"Inserted {len(result.inserted_ids)} documents"
