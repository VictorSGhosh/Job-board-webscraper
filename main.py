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
    "moloco": moloco,
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
    "purestorage": cmn_scraper1,          "digitalocean": cmn_scraper1,   "mongodb": cmn_scraper1,
    "hubspot": cmn_scraper1,              "elastic": cmn_scraper1,        "moveworks": cmn_scraper1,
    "voltron": cmn_scraper1,              "c3ai": cmn_scraper1,           "hashicorp": cmn_scraper1,
    "dfinity": cmn_scraper1,              "latentai": cmn_scraper1,       "salesloft": cmn_scraper1,
    "databricks": cmn_scraper1,           "asana": cmn_scraper1,          "datadog": cmn_scraper1,
    "redis": cmn_scraper1,                "cohesity": cmn_scraper1,       "dropbox": cmn_scraper1,
    "sentry": cmn_scraper1,               "braze": cmn_scraper1,          "collibra": cmn_scraper1,
    "optiver": cmn_scraper1,              "rapp": cmn_scraper1,           "applovin": cmn_scraper1,
    "signify_health": cmn_scraper1,       "myfitnesspal": cmn_scraper1,   "cedar": cmn_scraper1,
    "peloton": cmn_scraper1,              "kalderos": cmn_scraper1,       "picnichealth": cmn_scraper1,
    "rightway": cmn_scraper1,             "doximity": cmn_scraper1,       "thumbtack": cmn_scraper1,
    "videoamp": cmn_scraper1,             "buildops": cmn_scraper1,       "aurora": cmn_scraper1,
    "waymo": cmn_scraper1,                "recroom": cmn_scraper1,        "unity": cmn_scraper1,
    "roblox": cmn_scraper1,               "riot_games": cmn_scraper1,     "mastercontrol": cmn_scraper1,
    "equal_experts": cmn_scraper1,        "samsung_research": cmn_scraper1,"energyhub": cmn_scraper1,
    "axon": cmn_scraper1,                 "neuralink": cmn_scraper1,
    "point72": cmn_scraper2,              "spotter": cmn_scraper2,        "human_interest": cmn_scraper2,
    "carta": cmn_scraper2,                "propel": cmn_scraper2,         "arcesium": cmn_scraper2,
    "bolt": cmn_scraper2,                 "aquatic": cmn_scraper2,        "engineers_gate": cmn_scraper2,
    "sentilink": cmn_scraper2,            "semgrep": cmn_scraper2,        "okx": cmn_scraper2,
    "nightfall": cmn_scraper2,            "ping": cmn_scraper2,           "twitch": cmn_scraper2,
    "sumo_logic": cmn_scraper2,           "qualia": cmn_scraper2,         "ziprecruiter": cmn_scraper2,
    "box": cmn_scraper2,                  "yext": cmn_scraper2,           "upwork": cmn_scraper2,
    "discord": cmn_scraper2,              "airtable": cmn_scraper2,       "render": cmn_scraper2,
    "coreweave": cmn_scraper2,            "twilio": cmn_scraper2,         "notion": cmn_scraper2,
    "perplexity": cmn_scraper2,           "temporal": cmn_scraper2,       "dialpad": cmn_scraper2,
    "smartsheet": cmn_scraper2,           "stackline": cmn_scraper2,      "admarketplace": cmn_scraper2,
    "pmg": cmn_scraper2,                  "edo": cmn_scraper2,            "doubleverify": cmn_scraper2,
    "trade_desk": cmn_scraper2,           "omada_health": cmn_scraper2,   "heartflow": cmn_scraper2,
    "headway": cmn_scraper2,              "schrodinger": cmn_scraper2,    "launchdarkly": cmn_scraper2,
    "strava": cmn_scraper2,               "heygen": cmn_scraper2,         "latitude": cmn_scraper2,
    "sony_music": cmn_scraper2,           "npr": cmn_scraper2,            "rockstar_games": cmn_scraper2,
    "zynga": cmn_scraper2,                "otter": cmn_scraper2,          "varda_space": cmn_scraper2,
    "samsung_semiconductor": cmn_scraper2,"city_storage": cmn_scraper2,   "twist_bioscience": cmn_scraper2
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
