import os
import requests
from dotenv import load_dotenv
from pymongo import MongoClient

# ------------------------
# Load environment variables
# ------------------------
load_dotenv()
PROSPEO_API_KEY = os.getenv("PROSPEO_API_KEY")

if not PROSPEO_API_KEY:
    raise ValueError("Missing PROSPEO_API_KEY in .env file")

# ------------------------
# MongoDB connection
# ------------------------
mongo_client = MongoClient(
    "mongodb+srv://Cluster25172:pass123@cluster25172.bj5nf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster25172"
)
db = mongo_client["companyDB"]
linkedin_collection = db["linkedin_companies"]

# ------------------------
# Prospeo API setup
# ------------------------
url = "https://api.prospeo.io/mobile-finder"
headers = {
    "Content-Type": "application/json",
    "X-KEY": PROSPEO_API_KEY
}

# ------------------------
# Set N for testing (modify this number)
# ------------------------
n = 5  # change this number for testing

# ------------------------
# Process limited LinkedIn records
# ------------------------
print(f"📱 Starting mobile enrichment for first {n} LinkedIn profiles...\n")

for i, record in enumerate(linkedin_collection.find().limit(n), start=1):
    print(f"\n{'='*60}")
    print(f"🔍 Processing record #{i}")

    linkedin_url = record.get("linkedinUrl")
    first_name = record.get("firstName")
    last_name = record.get("lastName")

    # ✅ Skip if already has phone info
    if "prospectMobileInfo" in record and record["prospectMobileInfo"]:
        print(f"⏩ Skipping {first_name} {last_name} — already has prospectMobileInfo.")
        continue

    if not linkedin_url:
        print(f"⚠️ Skipping {first_name} {last_name} — no LinkedIn URL found.")
        continue

    # ------------------------
    # Call Prospeo Mobile Finder API
    # ------------------------
    payload = {"url": linkedin_url}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()

        # Save the API response in DB
        linkedin_collection.update_one(
            {"_id": record["_id"]},
            {"$set": {"prospectMobileInfo": response_data}}
        )

        print(f"✅ [{i}] Saved mobile data for {first_name} {last_name}")
        print("Response summary:", response_data)

    except Exception as e:
        print(f"❌ Error processing {first_name} {last_name}: {e}")

print(f"\n🎯 Completed mobile number enrichment for {n} records.")
