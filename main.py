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
    "cerebras": cerebras,
    "otterai": otterai,
    "credit_karma": cmn_scraper1,         "block": cmn_scraper1,          "coinbase": cmn_scraper1,
    "robinhood": cmn_scraper1,            "stripe": cmn_scraper1,         "ripple": cmn_scraper1,
    "sofi": cmn_scraper1,                 "drw": cmn_scraper1,            "hudson_river_trading": cmn_scraper1,
    "nerdwallet": cmn_scraper1,           "akuna_capital": cmn_scraper1,  "vatic_labs": cmn_scraper1,
    "pdt": cmn_scraper1,                  "aqr": cmn_scraper1,            "enfusion": cmn_scraper1,
    "recorded_future": cmn_scraper1,      "zscaler": cmn_scraper1,        "rubrik": cmn_scraper1,
    "paxos": cmn_scraper1,                "digicert": cmn_scraper1,       "wayfair": cmn_scraper1,
    "faire": cmn_scraper1,                "doordash": cmn_scraper1,       "pendo": cmn_scraper1,
    "pinterest": cmn_scraper1,            "roku": cmn_scraper1,           "airbnb": cmn_scraper1,
    "lyft": cmn_scraper1,                 "coupang": cmn_scraper1,        "worldquant": cmn_scraper1,
    "figma": cmn_scraper1,                "lendingtree": cmn_scraper1,    "squarespace": cmn_scraper1,
    "nextdoor": cmn_scraper1,             "duolingo": cmn_scraper1,       "handshake": cmn_scraper1,
    "purestorage": cmn_scraper1,          "digitalocean": cmn_scraper1,
    "point72": cmn_scraper2,              "spotter": cmn_scraper2,        "human_interest": cmn_scraper2,
    "carta": cmn_scraper2,                "propel": cmn_scraper2,         "arcesium": cmn_scraper2,
    "bolt": cmn_scraper2,                 "aquatic": cmn_scraper2,        "engineers_gate": cmn_scraper2,
    "sentilink": cmn_scraper2,            "semgrep": cmn_scraper2,        "okx": cmn_scraper2,
    "nightfall": cmn_scraper2,            "ping": cmn_scraper2,           "twitch": cmn_scraper2,
    "sumo_logic": cmn_scraper2,           "qualia": cmn_scraper2,         "ziprecruiter": cmn_scraper2,
    "box": cmn_scraper2,                  "yext": cmn_scraper2,           "upwork": cmn_scraper2,
    "discord": cmn_scraper2,              "duolingo": cmn_scraper2,       "airtable": cmn_scraper2,
    "render": cmn_scraper2,                "coreweave": cmn_scraper2,      "twilio": cmn_scraper2,
    "notion": cmn_scraper2
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
