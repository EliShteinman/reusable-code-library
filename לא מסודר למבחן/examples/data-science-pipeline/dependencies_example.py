# examples/data-science-pipeline/dependencies_example.py

import os

# from your_dal_module import YourDAL

# This pattern prioritizes a full connection URI from a secret,
# which is ideal for connecting to cloud services like MongoDB Atlas.

# 1. Try to get the full connection string first.
DB_URI_FROM_SECRET = os.getenv("DB_CONNECTION_URI")

if DB_URI_FROM_SECRET:
    # If the full URI is provided, use it directly.
    final_db_uri = DB_URI_FROM_SECRET
    db_name = os.getenv("DB_NAME", "default_db")  # Name might still be separate
else:
    # 2. Fallback to building the URI from individual parts (for local dev or other setups)
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "27017")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME", "default_db")

    if db_user and db_password:
        final_db_uri = f"mongodb://{db_user}:{db_password}@{db_host}:{db_port}/"
    else:
        final_db_uri = f"mongodb://{db_host}:{db_port}/"

# Now, instantiate your DAL with the determined URI and DB name
# data_layer_instance = YourDAL(mongo_uri=final_db_uri, db_name=db_name)