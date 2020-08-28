from datetime import datetime
import os
# Import the `pprint` function to print nested data:
from pprint import pprint

from dotenv import load_dotenv

import bson
from pymongo import MongoClient


def print_title(title):
    """
    Utility function to print a title with an underline.
    """
    print()                 # Print a blank line
    print(title)
    print('=' * len(title)) # Print an underline made of '='


# Load config from a .env file:
load_dotenv(verbose=True)
MONGODB_URI = os.environ['MONGODB_URI']

# Connect to your MongoDB cluster:
client = MongoClient(MONGODB_URI)

# Get a reference to the 'sample_mflix' database:
db = client['sample_mflix']

# Get a reference to the 'movies' collection:
movies = db['movies']

results = movies.aggregate([
    {
        '$group': {
            '_id': '$imdb.rating', 
            'titles': {
                '$push': '$title'
            }, 
            'count': {
                '$sum': 1
            }
        }
    }, {
        '$sort': {
            '_id': 1
        }
    }, {
        '$limit': 1
    }
])

print("The 3 worst movies on IMDB:")
worst_rating_document = next(results)
for title in worst_rating_document['titles']:
    print(f" * {title}")