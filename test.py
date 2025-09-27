"""
scraper_alpha.py

Company name -> Alpha Vantage SYMBOL_SEARCH -> ticker -> yfinance financials
"""

import requests
import yfinance as yf
import pandas as pd
import time

ALPHA_KEY = "4ZLQ7RFHAM127FGG"  # <-- replace with your key

# --- Step 1: Resolve company name -> ticker using Alpha Vantage ---
def search_ticker_alpha(company_name):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "SYMBOL_SEARCH",
        "keywords": company_name,
        "apikey": ALPHA_KEY
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    matches = data.get("bestMatches", [])
    if not matches:
        return None
    # Best match symbol
    return matches[0].get("1. symbol")

# --- Step 2: Fetch financial data from yfinance ---
def fetch_yfinance_data(ticker):
    t = yf.Ticker(ticker)
    info = t.info or {}
    try:
        fin = t.financials
        bal = t.balance_sheet
    except Exception:
        fin = bal = None

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
        "marketCap": info.get("marketCap"),
        "revenue": df_get_latest(fin, ["Total Revenue", "Revenue"]),
        "netIncome": df_get_latest(fin, ["Net Income", "Net income"]),
        "totalAssets": df_get_latest(bal, ["Total Assets", "Assets"]),
        "totalLiabilities": df_get_latest(bal, ["Total Liab", "Liabilities"]),
        "cashAndEquivalents": df_get_latest(bal, ["Cash and cash equivalents", "Cash"])
    }

# --- Step 3: Main runner ---
def main(company_names, out_csv="company_financials.csv", sleep_between=1.0):
    rows = []
    for name in company_names:
        print(f"\n🔎 Resolving: {name}")
        try:
            ticker = search_ticker_alpha(name)
        except Exception as e:
            print(f"❌ Search failed for {name}: {e}")
            rows.append({"company": name, "ticker": None, "error": str(e)})
            continue

        if not ticker:
            print(f"⚠️ Could not find ticker for {name}")
            rows.append({"company": name, "ticker": None})
            continue

        print(f"✅ Found ticker: {ticker} | Fetching financials...")
        try:
            data = fetch_yfinance_data(ticker)
            data["company"] = name
            rows.append(data)
        except Exception as e:
            print(f"⚠️ Failed to fetch financials for {ticker}: {e}")
            rows.append({"company": name, "ticker": ticker, "error": str(e)})

        time.sleep(sleep_between)  # polite delay

    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)
    print(f"\n📁 Done. Saved to {out_csv}")
    return df

if __name__ == "__main__":
    companies = [
    # US Big Tech
    "Apple Inc",
    "Microsoft Corporation",
    "Amazon.com Inc",
    "Alphabet Inc",
    "Meta Platforms Inc",
    "NVIDIA Corporation",
    "Tesla Inc",
    "Netflix Inc",

    # Indian IT & Conglomerates
    "Reliance Industries",
    "Tata Consultancy Services",
    "Infosys",
    "HCL Technologies",
    "Wipro",
    "Adani Enterprises",
    "HDFC Bank",
    "ICICI Bank",
    "State Bank of India",

    # Global Blue-Chips
    "Samsung Electronics",
    "Toyota Motor Corporation",
    "Sony Group Corporation",
    "IBM",
    "Intel Corporation",
    "Oracle Corporation",
    "Siemens AG",
    "Unilever",
    "Procter & Gamble",
    "Johnson & Johnson",
    "Coca-Cola",
    "PepsiCo",
    "Walmart Inc",
    "Exxon Mobil Corporation",
    "Shell PLC",
    "BP PLC" ]


    df = main(companies)
    print(df.head())
