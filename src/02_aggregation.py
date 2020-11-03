import os
# Import the `pprint` function to print nested data:
from pprint import pprint

from dotenv import load_dotenv

import bson
import pymongo


def print_title(title, underline_char="="):
    """
    Utility function to print a title with an underline.
    """
    print()                             # Print a blank line
    print(title)
    print(underline_char * len(title)) # Print an underline made of `underline_char`


# ----------------------------------------------------------------------------
# The purpose of the next few lines is to load a MONGODB_URI environment
# variable and use it to configure a MongoClient, where it will then set up
# the global variable `movie_collection`, representing the `movies` collection
# in the `sample_mflix` database.

# Load config from a .env file:
load_dotenv(verbose=True)
MONGODB_URI = os.environ["MONGODB_URI"]

# Connect to your MongoDB cluster:
client = pymongo.MongoClient(MONGODB_URI)

# Get a reference to the "sample_mflix" database:
db = client["sample_mflix"]

# Get a reference to the "movies" collection:
movie_collection = db["movies"]


def a_sample_movie_document():
    """
    Obtain a single movie document, and pretty-print it.
    """
    print_title("A Sample Movie")

    pipeline = [
        {
            "$match": {
                "title": "A Star Is Born"
            }
        }, 
        { "$limit": 1 },
    ]
    results = movie_collection.aggregate(pipeline)
    for movie in results:
        pprint(movie)


def a_sample_comment_document():
    """
    Obtain a single comment document, and pretty-print it.
    """
    print_title("A Sample Comment")

    pipeline = [
        { "$limit": 1 },
    ]
    results = db["comments"].aggregate(pipeline)
    for movie in results:
        pprint(movie)


def a_star_is_born_all():
    """
    Print a summary of all documents for "A Star Is Born" in the collection.
    """
    print_title("A Star Is Born - All Documents")

    # A pipeline with the following stages:
    #  * Match title = "A Star Is Born"
    #  * Sort by year, ascending
    pipeline = [
        {
            "$match": {
                "title": "A Star Is Born"
            }
        }, 
        { "$sort": { "year": pymongo.ASCENDING } },
    ]
    results = movie_collection.aggregate(pipeline)
    for movie in results:
        print(" * {title}, {first_castmember}, {year}".format(
            title=movie["title"],
            first_castmember=movie["cast"][0],
            year=movie["year"],
        ))


def a_star_is_born_most_recent():
    """
    Print a summary for the most recent production of "A Star Is Born" in the collection.
    """
    print_title("A Star Is Born - Most Recent")

    # Match title = "A Star Is Born":
    stage_match_title = {
        "$match": {
            "title": "A Star Is Born"
        }
    }

    # Sort by year, descending:
    stage_sort_year_descending = {
        "$sort": { "year": pymongo.DESCENDING }
    }

    # Limit to 1 document:
    stage_limit_1 = { "$limit": 1 }

    pipeline = [
        stage_match_title, 
        stage_sort_year_descending,
        stage_limit_1,
    ]
    results = movie_collection.aggregate(pipeline)
    for movie in results:
        print(" * {title}, {first_castmember}, {year}".format(
            title=movie["title"],
            first_castmember=movie["cast"][0],
            year=movie["year"],
        ))


def movies_with_comments():
    """
    Print the first 5 comments for 10 movies in the collection.

    This query can be a little slow - see the comments for tips.
    """
    print_title("Movies With Comments")

    # Look up related documents in the 'comments' collection:
    stage_lookup_comments = {
        "$lookup": {
            "from": "comments", 
            "localField": "_id", 
            "foreignField": "movie_id", 
            "as": "related_comments"
        }
    }

    # Calculate the number of comments for each movie:
    stage_add_comment_count = {
        "$addFields": {
            "comment_count": {
                "$size": "$related_comments"
            }
        } 
    }

    # Match movie documents with more than 2 comments:
    stage_match_with_comments = {
        "$match": {
            "comment_count": {
                "$gt": 2
            }
        } 
    }
    # Limit to the first 10 documents:
    limit_10 = { "$limit": 10 }

    # Optional limit to 1000 documents.
    # Run at the start of the pipeline, to speed things up during development:
    limit_1000 = { "$limit": 1000 }

    pipeline = [
        # Uncomment the line below to run on 1000 documents instead of
        # the full collection, for speed:
        #
        # limit_1000,
        stage_lookup_comments,
        stage_add_comment_count,
        stage_match_with_comments,
        limit_10,
    ]
    results = movie_collection.aggregate(pipeline)
    for movie in results:
        print_title(movie["title"], "-")
        print("Comment count:", movie["comment_count"])

        # Loop through the first 5 comments and print the name and text:
        for comment in movie["related_comments"][:5]:
            print(" * {name}: {text}".format(
                name=comment["name"],
                text=comment["text"]))


def movies_each_year():
    """
    Print the number of movies produced in each year until 1920, along with the movie titles.
    """
    print_title("Movies Grouped By Year")

    # Group movies by year, producing 'year-summary' documents that look like:
    # {
    #     '_id': 1917,
    #     'movie_count': 3,
    #     'movie_titles': [
    #         'The Poor Little Rich Girl',
    #         'Wild and Woolly',
    #         'The Immigrant'
    #     ]
    # }
    stage_group_year = {
        "$group": {
            "_id": "$year",
            "movie_count": { "$sum": 1 },
            "movie_titles": { "$push": "$title" },
        }
    }

    # Match a year-summary document where the year  (stored as `_id`) is both:
    #  * numeric
    #  * less than 1920
    stage_match_years = {
        "$match": {
            "year": {
                "$type": "number",
                "$lt": 1920,
            }
        }
    }
    
    # Sort year-summary documents by '_id'
    # (which is the year the document summarizes):
    stage_sort_year_ascending = {
        "$sort": {"_id": pymongo.ASCENDING}
    }

    pipeline = [
        stage_match_years,
        stage_group_year,
        stage_sort_year_ascending,
    ]
    results = movie_collection.aggregate(pipeline)

    # Loop through the 'year-summary' documents:
    for year_summary in results:
        # Print an underlined heading for each year:
        title = "{year}: {count} movies".format(
            year=year_summary["_id"],
            count=year_summary["movie_count"])
        print_title(title, "-")
        # Loop through the document titles for each year and print them
        # as bullets:
        for title in year_summary["movie_titles"]:
            print(" *", title)


# The following lines are commented out, as the functions they call aren't
# described in the accompanying blog post.
# I left the function definitions here anyway, in case the reader might find
# them useful.
#
# a_sample_movie_document()
# a_sample_comment_document()

a_star_is_born_all()
a_star_is_born_most_recent()
movies_with_comments()
movies_each_year()