import os
import yaml
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from src.insurerai.tools.custom_tool import (
    FetchAPITool,
    StoreMongoTool,
    SchemaAdapterTool,
    SchemaForwarderTool
)

@CrewBase
class Insurerai:
    """Insurerai crew for fetching, adapting, forwarding, and storing insurance claim data."""
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        agents_config_path = os.path.join(current_dir, 'config', 'agents.yaml')
        tasks_config_path = os.path.join(current_dir, 'config', 'tasks.yaml')
        with open(agents_config_path, 'r') as f:
            self.agents_config = yaml.safe_load(f)
        with open(tasks_config_path, 'r') as f:
            self.tasks_config = yaml.safe_load(f)
        self.inputs = None  # Store inputs for access

    def set_inputs(self, inputs):
        self.inputs = inputs

    @agent
    def data_fetcher(self) -> Agent:
        return Agent(
            config=self.agents_config['data_fetcher'],
            tools=[FetchAPITool()],
            verbose=True
        )

    @agent
    def schema_adapter(self) -> Agent:
        return Agent(
            config=self.agents_config['schema_adapter'],
            tools=[SchemaAdapterTool()],
            verbose=True
        )

    @agent
    def schema_forwarder(self) -> Agent:
        return Agent(
            config=self.agents_config['schema_forwarder'],
            tools=[SchemaForwarderTool()],
            verbose=True
        )

    @agent
    def data_storer(self) -> Agent:
        return Agent(
            config=self.agents_config['data_storer'],
            tools=[StoreMongoTool()],
            verbose=True
        )

    @task
    def fetch_claims_task(self) -> Task:
        return Task(
            config=self.tasks_config['fetch_claims'],
            agent=self.data_fetcher()
        )

    @task
    def adapt_schema_task(self) -> Task:
        return Task(
            config=self.tasks_config['adapt_schema'],
            agent=self.schema_adapter(),
            context=[self.fetch_claims_task()]
        )

    @task
    def forward_payload_task(self) -> Task:
        return Task(
            config=self.tasks_config['forward_payload'],
            agent=self.schema_forwarder(),
            context=[self.adapt_schema_task()],
            additional_context={'next_agent_endpoint': self.inputs['next_agent_endpoint']}  # Explicitly pass endpoint
        )

    @task
    def store_claims_task(self) -> Task:
        return Task(
            config=self.tasks_config['store_claims'],
            agent=self.data_storer(),
            context=[self.forward_payload_task()]
        )

    @crew
    def crew(self) -> Crew:
        self.set_inputs(self.inputs)  # Set inputs before creating crew
        return Crew(
            agents=self.agents,
            tasks=[
                self.fetch_claims_task(),
                self.adapt_schema_task(),
                self.forward_payload_task(),
                self.store_claims_task()
            ],
            process=Process.sequential,
            verbose=True
        )