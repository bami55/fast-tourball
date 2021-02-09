import os
from dotenv import load_dotenv
from os.path import join, dirname

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# toornament
API_KEY = os.environ['API_KEY']
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

# ballchasing
BCS_API_KEY = os.environ['BCS_API_KEY']

REQUEST_METHOD = {
    'get': 'GET',
    'post': 'POST',
    'delete': 'DELETE'
}
