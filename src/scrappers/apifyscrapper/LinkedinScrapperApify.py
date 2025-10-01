from apify_client import ApifyClient
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# ------------------------
# MongoDB connection
# ------------------------
mongo_client = MongoClient("mongodb+srv://Cluster25172:pass123@cluster25172.bj5nf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster25172")
db = mongo_client["companyDB"]              # your database
collection = db["linkedin_companies"]       # your collection

API_TOKEN = os.getenv("APIFY_API_TOKEN")
# ------------------------
# Apify connection
# ------------------------
apify_client = ApifyClient(API_TOKEN)

# Prepare the Actor input
run_input = {
    "currentJobTitles": ["CEO", "CTO", "CFO"],
    "industryIds": ["4"],
    "locations": ["United States"],
    "maxItems": 20,
    "profileScraperMode": "Full",
    "searchQuery": "Banking",
    "seniorityLevelIds": ["310"],
    "startPage": 1
}

# Run the Actor and wait for it to finish
run = apify_client.actor("M2FMdjRVeF1HPGFcc").call(run_input=run_input)

# Fetch results and insert into MongoDB
for item in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
    collection.insert_one(item)  # insert each record into MongoDB
    print(f"Inserted {item.get('companyName', 'Unknown')} into MongoDB")
