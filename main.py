import csv
import os
from classes import *
from scraper_functions import *  # Importing functions dynamically

# Load the JSON config file
with open("config.json", "r") as f:
    job_sources = json.load(f)

# Dictionary to map function names to actual functions
function_map = {
    "monzo": monzo,
    "credit_karma": cmn_scraper1,
    "block": cmn_scraper1,
    "coinbase": cmn_scraper1,
    "robinhood": cmn_scraper1,
    "stripe": cmn_scraper1,
    "ripple": cmn_scraper1,
    "sofi": cmn_scraper1,
    "hudson_river_trading": cmn_scraper1,
    "drw": cmn_scraper1,
    "nerdwallet": cmn_scraper1,
    "akuna_capital": cmn_scraper1,
    "vatic_labs": cmn_scraper1,
    "pdt": cmn_scraper1,
    "aqr": cmn_scraper1,
    "point72": cmn_scraper2,
    "spotter": cmn_scraper2,
    "human_interest": cmn_scraper2,
    "carta": cmn_scraper2,
    "propel": cmn_scraper2,
    "arcesium": cmn_scraper2,
    "bolt": cmn_scraper2,
    "aquatic": cmn_scraper2
}

if __name__ == "__main__":
    webscraper_driver_init()

    # List to accumulate job data
    all_jobs = []

    # Iterate through each job source
    for source in job_sources:
        func_name = source["function"]
        webscraper_driver_get(source["url"])

        # Check if the function exists in the mapping
        if func_name in function_map:
            print(f"Scraping jobs from {source['name']}...")
            board = Board(company=source["name"], url=source["url"], location_qualifiers=source['location_qualifiers'], job_title_qualifiers=source['job_qualifiers'], job_title_disqualifiers=source['job_disqualifiers'])
            jobs = function_map[func_name](board)  # Call the function dynamically
            all_jobs.extend(jobs)
        else:
            print(f"Skipping {source['name']} - Function '{func_name}' not found.")


    # Save to CSV
    csv_filename = "job_listings.csv"

    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow(["Company", "Job ID", "Title", "Location", "URL", "Content", "Published At"])

        # Write job data
        for job in all_jobs:
            writer.writerow([
                job.company,   job.id,   job.title,   job.location,  job.url,
                job.content if hasattr(job, "content") else "N/A",
                job.published_at if hasattr(job, "published_at") else "N/A"
            ])

    print(f"Scraping complete. Data saved to {csv_filename}.")
    os.startfile(csv_filename)
    webscraper_driver_cleanup()