#!/usr/bin/env python
import sys
import warnings
from datetime import datetime
from insurerai.crew import Insurerai

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    inputs = {
        'topic': 'Insurance Claims Data',
        'current_year': str(datetime.now().year),
        'api_endpoint': 'https://run.mocky.io/v3/faf2b832-e8bd-43f5-b10c-1a529a82f289',
        'database_uri': 'mongodb+srv://parasharvishist:yR7qtXETouPUcDpA@insuranceaicluster.k5phe.mongodb.net/insurance_db?retryWrites=true&w=majority&appName=insuranceAIcluster',
        'collection_name': 'insurance_claims',
        'similarity_cutoff': 0.6,
        'missing_threshold': 0.5,
        'next_agent_endpoint': 'http://localhost:8000/store_claims',
        'column_names': ['id', 'policy_number', 'claim_amount', 'status']
    }
    
    try:
        insurerai = Insurerai()
        insurerai.inputs = inputs  # Set inputs explicitly
        insurerai.crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'topic': 'Insurance Claims Data',
        'current_year': str(datetime.now().year),
        'api_endpoint': 'https://run.mocky.io/v3/faf2b832-e8bd-43f5-b10c-1a529a82f289',
        'database_uri': 'mongodb+srv://parasharvishist:yR7qtXETouPUcDpA@insuranceaicluster.k5phe.mongodb.net/insurance_db?retryWrites=true&w=majority&appName=insuranceAIcluster',
        'collection_name': 'insurance_claims',
        'similarity_cutoff': 0.6,
        'missing_threshold': 0.5,
        'next_agent_endpoint': 'http://localhost:8000/store_claims',  # Static endpoint
        'column_names': ['id', 'policy_number', 'claim_amount', 'status']
    }
    try:
        Insurerai().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Insurerai().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and return the results.
    """
    inputs = {
        'topic': 'Insurance Claims Data',
        'current_year': str(datetime.now().year),
        'api_endpoint': 'https://run.mocky.io/v3/faf2b832-e8bd-43f5-b10c-1a529a82f289',
        'database_uri': 'mongodb+srv://parasharvishist:yR7qtXETouPUcDpA@insuranceaicluster.k5phe.mongodb.net/insurance_db?retryWrites=true&w=majority&appName=insuranceAIcluster',
        'collection_name': 'insurance_claims',
        'similarity_cutoff': 0.6,
        'missing_threshold': 0.5,
        'next_agent_endpoint': 'http://localhost:8000/store_claims',  # Static endpoint
        'column_names': ['id', 'policy_number', 'claim_amount', 'status']
    }
    try:
        Insurerai().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == '__main__':
    run()