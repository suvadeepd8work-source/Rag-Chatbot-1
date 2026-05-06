import subprocess
import os
import logging
import json
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("Phase_6_Automated_Scheduler/scheduler.log"),
        logging.StreamHandler()
    ]
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_pipeline():
    logging.info("--- Starting Automated Knowledge Update Pipeline ---")
    
    try:
        # Step 1: Phase 1 - Scrape Data
        logging.info("Step 1: Running Phase 1 Scraper...")
        # Use python -m or absolute paths for reliability in CI
        subprocess.run(["python", "Phase_1_Data_Acquisition/scraper.py"], cwd=PROJECT_ROOT, check=True)
        logging.info("Step 1 Complete: Data scraped.")
        
        # Step 2: Phase 2 - Prepare Data (Aggregate and Chunk)
        logging.info("Step 2: Running Phase 2 Data Preparation...")
        subprocess.run(["python", "Phase_2_Vector_Database/prepare_data.py"], cwd=PROJECT_ROOT, check=True)
        logging.info("Step 2 Complete: Data aggregated and chunked.")
        
        # Step 3: Phase 2 - Update Vector Database (Lightweight Mode)
        logging.info("Step 3: Updating Knowledge Base (Lightweight Search)...")
        # In our current setup, Phase 2 ingestion is just generating chunks
        logging.info("Step 3 Complete: Knowledge Base updated.")
        
        # Step 4: Save Last Updated Date
        update_info = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "success"
        }
        with open(os.path.join(PROJECT_ROOT, "metadata.json"), "w") as f:
            json.dump(update_info, f)
        logging.info(f"Step 4 Complete: Last updated date saved: {update_info['last_updated']}")
        
        logging.info("--- Pipeline Successfully Completed ---")
        
    except subprocess.CalledProcessError as e:
        logging.error(f"Pipeline failed during step: {e}")
        exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    # Execute the pipeline once and exit
    # This is optimized for GitHub Actions / Cron jobs
    run_pipeline()
