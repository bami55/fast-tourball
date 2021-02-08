import os
from dotenv import load_dotenv
from os.path import join, dirname

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

API_KEY = os.environ['API_KEY']
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

REQUEST_METHOD = {
    'get': 'GET',
    'post': 'POST',
    'delete': 'DELETE'
}
