"""
client_schema_main.py - A script to execute some commands demonstrating MongoDB's client-side field-level encryption.

Note:
-----
Before running this script, first run "client_schema_create_key.py" to
configure a key in the database and to generate "key_bytes.bin"
and "json_schema.json".
"""

import os
from pathlib import Path

from pymongo import MongoClient
from pymongo.encryption_options import AutoEncryptionOpts
from pymongo.errors import EncryptionError
from bson import json_util


# Load the secret key from 'key_bytes.bin':
key_bin = Path("key_bytes.bin").read_bytes()

# Load the 'person' schema from "json_schema.json":
collection_schema = json_util.loads(Path("json_schema.json").read_text())

# Configure a single, local KMS provider, with the saved key:
kms_providers = {"local": {"key": key_bin}}

# Create a configuration for PyMongo, specifying the local key,
# the collection used for storing key data, and the json schema specifying
# field encryption:
fle_opts = AutoEncryptionOpts(
    kms_providers,
    "fle_demo.__keystore",
    schema_map={"fle_demo.people": collection_schema},
)

# Add a new document to the "people" collection, and then read it back out
# to demonstrate that the ssn field is automatically decrypted by PyMongo:
with MongoClient(os.environ["MDB_URL"], auto_encryption_opts=fle_opts) as client:
    client.fle_demo.people.delete_many({})
    client.fle_demo.people.insert_one(
        {
            "full_name": "Sophia Duleep Singh",
            "ssn": "123-12-1234",
        }
    )
    print("Decrypted find() results: ")
    print(client.fle_demo.people.find_one())

# Connect to MongoDB, but this time without FLE configuration.
# This will print the document with ssn *still encrypted*:
with MongoClient(os.environ["MDB_URL"]) as client:
    print("Encrypted find() results: ")
    print(client.fle_demo.people.find_one())

# The following demonstrates that if the ssn field is encrypted as
# "Random" it cannot be filtered:
try:
    with MongoClient(os.environ["MDB_URL"], auto_encryption_opts=fle_opts) as client:
        # This will fail if ssn is specified as "Random".
        # Change the algorithm to "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic"
        # in client_schema_create_key.py (and run it again) for this to succeed:
        print("Find by ssn: ")
        print(client.fle_demo.people.find_one({"ssn": "123-12-1234"}))
except EncryptionError as e:
    # This is expected if the field is "Random" but not if it's "Deterministic"
    print(e)

# Configure encryption options with the same key, but *without* a schema:
fle_opts_no_schema = AutoEncryptionOpts(
    kms_providers,
    "fle_demo.__keystore",
)
with MongoClient(
    os.environ["MDB_URL"], auto_encryption_opts=fle_opts_no_schema
) as client:
    print("Inserting Dora Thewlis, without configured schema.")
    # This will insert a document *without* encrypted ssn, because
    # no schema is specified in the client or server:
    client.fle_demo.people.insert_one(
        {
            "full_name": "Dora Thewlis",
            "ssn": "234-23-2345",
        }
    )

# Connect without FLE configuration to show that Sophia Duleep Singh is
# encrypted, but Dora Thewlis has her ssn saved as plaintext.
with MongoClient(os.environ["MDB_URL"]) as client:
    print("Encrypted find() results: ")
    for doc in client.fle_demo.people.find():
        print(" *", doc)
