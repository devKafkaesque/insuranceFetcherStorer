import requests
import logging
import difflib
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from pymongo import MongoClient

# Set up logging for debugging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class FetchAPITool(BaseTool):
    name: str = "fetch_api_data"
    description: str = "Fetch data from an API endpoint with the given headers"
    
    class Input(BaseModel):
        endpoint: str = Field(..., description="API endpoint URL")
        headers: dict = Field(..., description="Request headers")
    
    def _run(self, endpoint: str, headers: dict) -> dict:
        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            logging.info(f"Fetched data successfully from {endpoint}")
            return response.json()
        except requests.RequestException as e:
            logging.error(f"API request failed: {e}")
            raise Exception(f"API request failed: {e}")

class StoreMongoTool(BaseTool):
    name: str = "store_in_mongodb"
    description: str = "Store data in a MongoDB collection"
    
    class Input(BaseModel):
        data: list = Field(..., description="Data to store in MongoDB")
        database_uri: str = Field(..., description="MongoDB connection URI")
        collection_name: str = Field(..., description="Name of the MongoDB collection")
    
    def _run(self, data: list, database_uri: str, collection_name: str) -> str:
        try:
            client = MongoClient(
                database_uri,
                tls=True,  # Enable TLS for Atlas
                tlsAllowInvalidCertificates=False,  # Enforce valid certificates
                serverSelectionTimeoutMS=30000
            )
            db = client.get_database()
            collection = db[collection_name]
            result = collection.insert_many(data)
            client.close()
            logging.info(f"Inserted {len(result.inserted_ids)} documents into {collection_name}")
            return f"Inserted {len(result.inserted_ids)} documents"
        except Exception as e:
            logging.error(f"MongoDB insertion failed: {e}")
            raise Exception(f"MongoDB insertion failed: {e}")

class SchemaAdapterTool(BaseTool):
    name: str = "adapt_schema"
    description: str = "Adapt incoming API payload to a canonical schema using fuzzy matching and dynamic column names"
    
    class Input(BaseModel):
        payload: dict = Field(..., description="Incoming API payload")
        column_names: list = Field(..., description="List of expected column names in the canonical schema")
        similarity_cutoff: float = Field(0.6, description="Minimum similarity ratio for matching fields")
        missing_threshold: float = Field(0.5, description="Maximum allowed fraction of missing required fields")
    
    def _run(self, payload: dict, column_names: list, similarity_cutoff: float = 0.6, missing_threshold: float = 0.5) -> list:
        if 'claims' not in payload:
            raise Exception("Payload missing 'claims' key")
        
        claims = payload['claims']
        adapted_claims = []
        
        for claim in claims:
            canonical_schema = {col: True for col in column_names}
            adapted = {}
            missing_required = 0
            payload_keys = list(claim.keys())

            for canonical_field in column_names:
                matches = difflib.get_close_matches(canonical_field, payload_keys, n=1, cutoff=similarity_cutoff)
                if matches:
                    best_match = matches[0]
                    adapted[canonical_field] = claim[best_match]
                else:
                    adapted[canonical_field] = None
                    missing_required += 1
            
            total_required = len(column_names)
            if total_required > 0 and (missing_required / total_required) > missing_threshold:
                logging.warning(f"Claim {claim.get('id', 'unknown')} schema deviates too much from expected; skipping.")
                continue
            
            adapted_claims.append(adapted)
        
        if not adapted_claims:
            raise Exception("No claims adapted successfully; schema deviation too significant.")
        
        logging.info("Schema adaptation completed successfully")
        return adapted_claims

class SchemaForwarderTool(BaseTool):
    name: str = "forward_payload"
    description: str = "Forward the adapted payload to a static endpoint"
    
    class Input(BaseModel):
        payload: list = Field(..., description="List of adapted claim data objects")
        next_agent_endpoint: str = Field(..., description="Static endpoint URL for the next agent")
        headers: dict = Field(default_factory=dict, description="Optional headers for the forwarding request")
    
    def _run(self, payload: list, next_agent_endpoint: str, headers: dict = None) -> list:
        headers = headers or {}
        try:
            response = requests.post(next_agent_endpoint, json=payload, headers=headers)
            response.raise_for_status()
            logging.info(f"Payload successfully forwarded to {next_agent_endpoint}")
            return payload
        except requests.RequestException as e:
            logging.error(f"Forwarding failed: {e}")
            raise Exception(f"Forwarding failed: {e}")