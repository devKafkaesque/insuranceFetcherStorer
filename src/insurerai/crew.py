from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import requests
from pymongo import MongoClient

from src.insurerai.tools.custom_tool import FetchAPITool, StoreMongoTool

# Define tools for the agents
def fetch_api_data(endpoint, headers):
    """Fetch data from an API endpoint with the given headers."""
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status {response.status_code}")

def store_in_mongodb(data, database_uri, collection_name):
    """Store data in a MongoDB collection."""
    client = MongoClient(database_uri)
    db = client.get_database()
    collection = db[collection_name]
    result = collection.insert_many(data)
    client.close()
    return f"Inserted {len(result.inserted_ids)} documents"

@CrewBase
class Insurerai:
    """Insurerai crew for fetching and storing insurance claim data."""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def data_fetcher(self) -> Agent:
        """Agent responsible for fetching insurance claim data from the API."""
        return Agent(
            config=self.agents_config['data_fetcher'],
            tools=[FetchAPITool()],
            verbose=True
        )

    @agent
    def data_storer(self) -> Agent:
        """Agent responsible for storing fetched data in MongoDB."""
        return Agent(
            config=self.agents_config['data_storer'],
            tools=[StoreMongoTool()],
            verbose=True
        )


    @task
    def fetch_claims_task(self) -> Task:
        """Task to fetch insurance claim data from the API."""
        return Task(
            config=self.tasks_config['fetch_claims'],
            agent=self.data_fetcher()
        )

    @task
    def store_claims_task(self) -> Task:
        """Task to store fetched claim data in MongoDB."""
        return Task(
            config=self.tasks_config['store_claims'],
            agent=self.data_storer(),
            context=[self.fetch_claims_task()]  # Depends on fetch_claims_task output
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Insurerai crew to execute the tasks sequentially."""
        return Crew(
            agents=self.agents,  # Populated by @agent decorators
            tasks=[self.fetch_claims_task(), self.store_claims_task()],  # Task order matters for sequential process
            process=Process.sequential,
            verbose=True
        )