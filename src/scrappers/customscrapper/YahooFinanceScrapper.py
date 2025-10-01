import requests
import yfinance as yf
import pandas as pd
import time
import logging
import certifi
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# ------------------ CONFIG ------------------
ALPHA_KEY = "4ZLQ7RFHAM127FGG"   # Replace with your Alpha Vantage key
MONGO_URI = "mongodb+srv://Cluster25172:pass123@cluster25172.bj5nf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster25172"

DB_NAME = "companyDB"
COLLECTION_NAME = "linkedin_companies"
OUT_CSV = "company_financials.csv"
# ---------------------------------------------

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ------------------ MONGO FETCH ------------------
def fetch_companies():
    """Fetch company names + LinkedIn industries from MongoDB"""
    try:
        client = MongoClient(MONGO_URI, server_api=ServerApi('1'), tlsCAFile=certifi.where())
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        companies = []
        for doc in collection.find({}, {"currentPosition.companyName": 1, "industry": 1}):
            current_positions = doc.get("currentPosition", [])
            if current_positions and isinstance(current_positions, list):
                company_name = current_positions[0].get("companyName")
                linkedin_industry = doc.get("industry")  # LinkedIn's industry field
                if company_name:
                    companies.append({
                        "name": company_name,
                        "linkedinIndustry": linkedin_industry
                    })

        logger.info(f"Fetched {len(companies)} companies from MongoDB [{DB_NAME}.{COLLECTION_NAME}]")
        return companies
    except Exception as e:
        logger.error(f"MongoDB fetch failed: {e}")
        return []

# ------------------ STEP 1: SYMBOL SEARCH ------------------
def search_ticker_alpha(company_name):
    """Resolve company name -> ticker using Alpha Vantage"""
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "SYMBOL_SEARCH",
        "keywords": company_name,
        "apikey": ALPHA_KEY
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        matches = data.get("bestMatches", [])
        if not matches:
            logger.warning(f"No ticker found for {company_name}")
            return None
        symbol = matches[0].get("1. symbol")
        logger.info(f"Resolved {company_name} -> {symbol}")
        return symbol
    except Exception as e:
        logger.error(f"Alpha Vantage search failed for {company_name}: {e}")
        return None

# ------------------ STEP 2: YFINANCE ------------------
def fetch_yfinance_data(ticker):
    """Fetch financial + sector data from yfinance"""
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        fin = getattr(t, "financials", None)
        bal = getattr(t, "balance_sheet", None)
    except Exception as e:
        logger.error(f"yfinance failed for {ticker}: {e}")
        return None

    def df_get_latest(df, field_candidates):
        if df is None or df.empty:
            return None
        for cand in field_candidates:
            for row in df.index:
                if cand.lower() in str(row).lower():
                    try:
                        return int(df.loc[row].dropna().values[0])
                    except:
                        try:
                            return float(df.loc[row].dropna().values[0])
                        except:
                            return None
        return None

    return {
        "ticker": ticker,
        "shortName": info.get("shortName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "marketCap": info.get("marketCap"),
        "revenue": df_get_latest(fin, ["Total Revenue", "Revenue"]),
        "netIncome": df_get_latest(fin, ["Net Income"]),
        "totalAssets": df_get_latest(bal, ["Total Assets", "Assets"]),
        "totalLiabilities": df_get_latest(bal, ["Total Liab", "Liabilities"]),
        "cashAndEquivalents": df_get_latest(bal, ["Cash and cash equivalents", "Cash"])
    }

# ------------------ STEP 3: MAIN RUNNER ------------------
def main(companies, out_csv=OUT_CSV, sleep_between=1.0):
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'), tlsCAFile=certifi.where())
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    rows = []
    for comp in companies:
        name = comp["name"]
        linkedin_industry = comp.get("linkedinIndustry")

        logger.info(f"🔎 Processing company: {name}")

        ticker = search_ticker_alpha(name)
        if not ticker:
            rows.append({"company": name, "ticker": None, "error": "No ticker found", "linkedinIndustry": linkedin_industry})
            continue

        data = fetch_yfinance_data(ticker)
        if not data:
            rows.append({"company": name, "ticker": ticker, "error": "yfinance fetch failed", "linkedinIndustry": linkedin_industry})
            continue

        data["company"] = name
        data["linkedinIndustry"] = linkedin_industry  # merge LinkedIn industry fallback
        rows.append(data)

        # update MongoDB with financials
        collection.update_one(
            {"currentPosition.companyName": name},
            {"$set": {"financials": data}}
        )

        logger.info(f"✅ Completed {name} ({ticker})")
        time.sleep(sleep_between)  # polite delay

    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)
    logger.info(f"📁 Saved results to {out_csv}")
    return df

# ------------------ ENTRY POINT ------------------
if __name__ == "__main__":
    companies = fetch_companies()
    if not companies:
        logger.warning("No companies to process. Exiting.")
    else:
        df = main(companies)
        logger.info(f"Run completed. Preview:\n{df.head()}")
