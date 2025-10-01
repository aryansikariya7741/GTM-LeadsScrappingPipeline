import os
from apify_client import ApifyClient
from pymongo import MongoClient
import time
from dotenv import load_dotenv

# -----------------------------
# MongoDB Setup
# -----------------------------
mongo_client = MongoClient(
    "mongodb+srv://Cluster25172:pass123@cluster25172.bj5nf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster25172"
)
db = mongo_client["companyDB"]
collection = db["linkedin_companies"]
company_info_collection = db["company_info"]  # new collection for storing results

# -----------------------------
# Apify Setup
# -----------------------------
API_TOKEN = os.getenv("APIFY_API_TOKEN")

client = ApifyClient(API_TOKEN)

# -----------------------------
# Process companies
# -----------------------------
for doc in collection.find({}, {"currentPosition": 1, "_id": 0}):
    if "currentPosition" in doc and isinstance(doc["currentPosition"], list):
        for pos in doc["currentPosition"]:
            company_id = pos.get("companyId")
            url = pos.get("companyLinkedinUrl")

            if not company_id or not url:
                continue

            # Check if company already processed
            exists = company_info_collection.find_one({"companyId": company_id})
            if exists:
                print(f"⏩ Skipping companyId {company_id}, already exists in company_info.")
                continue

            print(f"\n🔄 Processing companyId: {company_id}, URL: {url}")

            # Run Apify actor
            run_input = {"profileUrls": [url]}
            run = client.actor("AjfNXEI9qTA2IdaAX").call(run_input=run_input)

            dataset_id = run["defaultDatasetId"]

            # Collect results
            results = list(client.dataset(dataset_id).iterate_items())

            if results:
                for item in results:
                    print("📌 Output:", item)

                # Save results with companyId
                company_info_collection.insert_one({
                    "companyId": company_id,
                    "companyLinkedinUrl": url,
                    "results": results,
                    "apifyRunId": run["id"],  # trace run
                    "status": "succeeded"
                })
                print(f"✅ Saved results for companyId {company_id} into company_info.")
            else:
                print(f"⚠️ No results returned for companyId {company_id}")

            # Delay between cycles
            time.sleep(5)




