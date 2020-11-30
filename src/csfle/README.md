# Client-Side Field-Level Encryption

This directory contains sample code to accompany a [CSFLE post](https://developer.mongodb.com/quickstart/python-quickstart-fle).
It contains 4 scripts, in pairs:

## The Sample Code

| File | Description |
|---|---|
|[client_schema_create_key.py](client_schema_create_key.py)| A script demonstrating how to create a key for local storage, and a data key within MongoDB. It outputs two files: The random bytes used to encrypt the data key, and a JSON schema file containing a schema to be used to configure MongoClient |
|[client_schema_main.py](client_schema_main.py)| A Python script which executes various commands against a MongoDB cluster to demonstrate various aspects of Client-Side Field Level Encryption in MongoDB. It's designed to be run after `client_schema_create_key.py`, which creates some files this script depends on. |
|[server_schema_create_key.py](server_schema_create_key.py)|  A script demonstrating how to create a key for local storage, and a data key within MongoDB. It outputs one file containing the random bytes used to encrypt the data key. The JSON schema is set directly on the `people` collection as a validator  |
|[server_schema_main.py](server_schema_main.py)| A Python script which executes various commands against a MongoDB cluster to demonstrate various aspects of Client-Side Field Level Encryption in MongoDB (with a CSFLE schema applied to a collection). It's designed to be run after `server_schema_create_key.py`, which creates some files this script depends on. |

## Executing The Sample Code

The best way to understand and run the code is to follow the [blog post](https://developer.mongodb.com/quickstart/python-quickstart-fle) it was written for, but the summary is:

* You need Python 3.6+
* Pip install the dependencies with `python3 -m pip install pymongo[svr,encryption] ~= 3.11`
* Set the ``MDB_URL`` environment variable to your Atlas cluster's URL.
* Run each script to see what it does! (The code is heavily commented.)
