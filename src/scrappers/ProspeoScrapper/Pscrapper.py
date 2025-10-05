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
company_info_collection = db["company_info"]

# ------------------------
# Prospeo API setup
# ------------------------
url = "https://api.prospeo.io/email-finder"
headers = {
    "Content-Type": "application/json",
    "X-KEY": PROSPEO_API_KEY
}

# ------------------------
# Set N for testing (modify this number)
# ------------------------
n = 3  # change this to how many records you want to test

# ------------------------
# Process limited LinkedIn records
# ------------------------
print(f"Testing with first {n} records...\n")

for i, record in enumerate(linkedin_collection.find().limit(n), start=1):
    print(f"loop start\n{'-'*40}")
    first_name = record.get("firstName")
    last_name = record.get("lastName")

    # Extract companyId
    company_data = record.get("currentPosition", [])
    if not company_data or not company_data[0].get("companyId"):
        print(f"[{i}] Skipping {first_name} {last_name} — no companyId found.")
        continue

    company_id = company_data[0]["companyId"]

    # Find the matching company info
    company_info = company_info_collection.find_one({"companyId": company_id})
    if not company_info:
        print(f"[{i}] Skipping {first_name} {last_name} — no company info for ID {company_id}.")
        continue

    website_url = company_info.get("results", [{}])[0].get("websiteUrl")
    if not website_url:
        print(f"[{i}] Skipping {first_name} {last_name} — no website URL found.")
        continue

    # ------------------------
    # Call Prospeo API
    # ------------------------
    data = {
        "first_name": first_name,
        "last_name": last_name,
        "company": website_url
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response_data = response.json()

        print(f"\n[{i}] {first_name} {last_name} → {website_url}")
        print("Prospeo API Response:", response_data)

    except Exception as e:
        print(f"[{i}] Error processing {first_name} {last_name}: {e}")

    print(f"{'-'*40}\n loop end\n{'-'*40}")

print(f"\nCompleted testing {n} records.")
