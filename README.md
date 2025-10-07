# 🧠 Automated LinkedIn → Company → Finance → Contact Enrichment Pipeline

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![MongoDB](https://img.shields.io/badge/Database-MongoDB-green?logo=mongodb&logoColor=white)
![Apify](https://img.shields.io/badge/Scraper-Apify-orange?logo=apify&logoColor=white)
![Prospeo](https://img.shields.io/badge/API-Prospeo-yellow?logo=postman&logoColor=white)
![YahooFinance](https://img.shields.io/badge/Data-YahooFinance-purple?logo=yahoo&logoColor=white)

> 🧩 **End-to-end data enrichment system** that scrapes LinkedIn profiles, extracts company data, adds financial insights, and enriches contact info (email + mobile).  
> Built with **Apify**, **Prospeo**, **Yahoo Finance**, and **MongoDB** — fully automated with a single orchestrator.

---

## ⚙️ Project Overview

This pipeline automates B2B data enrichment by:
1. Scraping **LinkedIn CXO profiles**.
2. Collecting **company details** from LinkedIn pages.
3. Pulling **financial data** from Yahoo Finance & Alpha Vantage.
4. Enriching each profile with **verified emails and phone numbers** via Prospeo.
5. Storing all unified data into **MongoDB Atlas**.

---

## 🧩 Workflow Diagram

            ┌────────────────────────┐
            │ LinkedinScrapperApify  │
            │  (Profiles)            │
            └──────────┬─────────────┘
                       │
                       ▼
            ┌────────────────────────┐
            │ ApifyCompanyScrapper    │
            │  (Company info)         │
            └──────────┬─────────────┘
                       │
                       ▼
            ┌────────────────────────┐
            │ YahooFinanceScrapper   │
            │  (Financials)          │
            └──────────┬─────────────┘
                       │
                       ▼
            ┌────────────────────────┐
            │ Pmobile (Prospeo Email)│
            │  (Email enrichment)    │
            └──────────┬─────────────┘
                       │
                       ▼
            ┌────────────────────────┐
            │ Pscrapper (Prospeo Mob)│
            │  (Mobile enrichment)   │
            └────────────────────────┘


---

## 🧱 Tech Stack

| Component | Technology |
|------------|-------------|
| **Database** | MongoDB Atlas |
| **Scraping Framework** | Apify SDK |
| **Contact Enrichment** | Prospeo API |
| **Financial Data APIs** | Yahoo Finance (`yfinance`) + Alpha Vantage |
| **Language** | Python 3.13 |
| **Environment** | `python-dotenv` |
| **Logging** | Python `logging` |
| **Controller** | `main.py` orchestrator |

---

## 🧰 Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone <your-repo-url>
cd project-root

pip install -r requirements.txt

create a .env file and this 
APIFY_API_TOKEN=<your_apify_token>
APIFY_API_TOKEN2=<your_apify_company_token>
PROSPEO_API_KEY=<your_prospeo_api_key>
ALPHA_KEY=<your_alpha_vantage_key>


Stores LinkedIn profile data enriched later with emails & phones.

{
  "_id": "...",
  "firstName": "Anand",
  "lastName": "Awasthi",
  "linkedinUrl": "https://www.linkedin.com/in/avhananand",
  "currentPosition": [
    {
      "companyId": "151887",
      "companyLinkedinUrl": "https://www.linkedin.com/company/151887/",
      "companyName": "Avhan Technologies Pvt. Ltd."
    }
  ],
  "prospectEmailInfo": {...},
  "prospectMobileInfo": {...}
}


Stores company-level scraped data and financial enrichment.


{
  "_id": "...",
  "companyId": "151887",
  "companyLinkedinUrl": "https://www.linkedin.com/company/151887/",
  "results": [
    {
      "companyName": "Avhan Technologies Pvt Ltd",
      "websiteUrl": "https://www.avhan.com/"
    }
  ],
  "companyFinance": {
    "ticker": "TCS.NS",
    "sector": "Information Technology",
    "industry": "IT Services",
    "marketCap": 800000000000,
    "revenue": 230000000000,
    "status": "success"
  }
}




main script run command 

go to src and run main.py


