"""
client_schema_create_key.py - A Python script to create a random key.

This script:
 * Generates a random 96-byte key, and writes it to "key_bytes.bin"
 * Connects to the MongoDB server at "MDB_URL" and adds a key to "fle_demo.__keystore", with the alt name of "example".
 * Creates a "people" collection, with a JSON schema provided as validator.
"""

import os
from pathlib import Path
from secrets import token_bytes

from bson.binary import STANDARD
from bson.codec_options import CodecOptions
from pymongo import MongoClient
from pymongo.encryption import ClientEncryption
from pymongo.encryption_options import AutoEncryptionOpts


# Generate a secure 96-byte secret key:
key_bytes = token_bytes(96)

# Configure a single, local KMS provider, with the saved key:
kms_providers = {"local": {"key": key_bytes}}
fle_opts = AutoEncryptionOpts(
    kms_providers=kms_providers, key_vault_namespace="fle_demo.__keystore"
)

# Connect to MongoDB with the key information generated above:
with MongoClient(os.environ["MDB_URL"], auto_encryption_opts=fle_opts) as client:
    print("Resetting demo database & keystore...")
    client.drop_database("fle_demo")

    # Create a ClientEncryption object to create the data key below:
    client_encryption = ClientEncryption(
        kms_providers,
        "fle_demo.__keystore",
        client,
        CodecOptions(uuid_representation=STANDARD),
    )

    print("Creating key in MongoDB ...")
    key_id = client_encryption.create_data_key("local", key_alt_names=["example"])

    # This is the schema which will be saved out to "json_schema.json":
    schema = {
        "bsonType": "object",
        "properties": {
            "ssn": {
                "encrypt": {
                    "bsonType": "string",
                    # Change to "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic" in order to filter by ssn value:
                    "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Random",
                    "keyId": [key_id],
                }
            },
        },
    }

    print("Creating 'people' collection in 'fle_demo' database (with schema) ...")
    client.fle_demo.create_collection(
        "people",
        codec_options=CodecOptions(uuid_representation=STANDARD),
        validator={"$jsonSchema": schema},
    )

    print("Writing secret key to 'key_bytes.bin' ...")
    Path("key_bytes.bin").write_bytes(key_bytes)

    print("Done.")