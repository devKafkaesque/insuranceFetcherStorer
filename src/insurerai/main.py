#!/usr/bin/env python
import sys
import warnings
from datetime import datetime
from insurerai.crew import Insurerai

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Main control file for your insurance claims data crew.
# This script provides inputs for fetching claims from your dummy insurance API 
# and storing them in MongoDB.

def run():
    """
    Run the crew to fetch and store insurance claims data.
    """
    inputs = {
        'topic': 'Insurance Claims Data',
        'current_year': str(datetime.now().year),
        'api_endpoint': 'https://run.mocky.io/v3/66b2b9b1-5e5c-4a73-aee4-4e5a7b8f0c3c',
        'mongodb_uri': 'mongodb+srv://parasharvishist:yR7qtXETouPUcDpA@insuranceaicluster.k5phe.mongodb.net/?retryWrites=true&w=majority&appName=insuranceAIcluster',
        'collection_name': 'claims'
    }
    
    try:
        Insurerai().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'topic': 'Insurance Claims Data',
        'api_endpoint': 'https://run.mocky.io/v3/66b2b9b1-5e5c-4a73-aee4-4e5a7b8f0c3c',
        'mongodb_uri': 'mongodb+srv://parasharvishist:yR7qtXETouPUcDpA@insuranceaicluster.k5phe.mongodb.net/?retryWrites=true&w=majority&appName=insuranceAIcluster',
        'collection_name': 'claims'
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
        'api_endpoint': 'https://run.mocky.io/v3/66b2b9b1-5e5c-4a73-aee4-4e5a7b8f0c3c',
        'mongodb_uri': 'mongodb+srv://parasharvishist:yR7qtXETouPUcDpA@insuranceaicluster.k5phe.mongodb.net/?retryWrites=true&w=majority&appName=insuranceAIcluster',
        'collection_name': 'claims'
    }
    try:
        Insurerai().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == '__main__':
    # Run the crew by default when executing this script.
    run()
