import os
import time
import logging
import importlib

# ------------------------
# Logging Setup
# ------------------------
LOG_DIR = os.path.join("src", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "main_pipeline.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ------------------------
# Utility function to run scrapers safely
# ------------------------
def run_script(module_path, func_name=None):
    """
    Dynamically import and run a Python script (or function inside it).
    module_path: e.g. 'scrappers.apifyscrapper.LinkedinScrapperApify'
    func_name:   optional — if script defines a main() or similar
    """
    try:
        logger.info(f"🚀 Starting: {module_path}")
        module = importlib.import_module(module_path)
        if func_name and hasattr(module, func_name):
            getattr(module, func_name)()
        logger.info(f"✅ Completed: {module_path}")
    except Exception as e:
        logger.error(f"❌ Error running {module_path}: {e}")
    finally:
        time.sleep(3)  # small cooldown between scrapers

# ------------------------
# Run all scrapers in sequence
# ------------------------
if __name__ == "__main__":
    logger.info("============================================")
    logger.info("⚙️  Starting Master Scraper Pipeline")
    logger.info("============================================")

    # 1️⃣ LinkedIn people scraper
    run_script("scrappers.apifyscrapper.LinkedinScrapperApify")

    # 2️⃣ Company scraper (Apify)
    run_script("scrappers.apifyscrapper.ApifyCompanyScrapper")

    # 3️⃣ Financial data scraper (Yahoo Finance + Alpha Vantage)
    run_script("scrappers.customscrapper.YahooFinanceScrapper")

    # 4️⃣ Prospeo email enrichment
    run_script("scrappers.ProspeoScrapper.Pmobile")

    # 5️⃣ Prospeo mobile enrichment
    run_script("scrappers.ProspeoScrapper.Pscrapper")

    logger.info("============================================")
    logger.info("🏁 All scrapers executed successfully!")
    logger.info("============================================")
