import csv
import os
import time

from classes import *
from scraper_functions import *  # Importing functions dynamically
from multiprocessing import Pool, cpu_count

from typing import Callable, Dict, List, Tuple, Any

# Load the JSON config file
with open("config.json", "r") as f:
    job_sources = json.load(f)


def scrape_source(source: Dict[str, Any], func: Callable[[Any], List[Any]], visited_ids: List[str]) -> Tuple[str, List[Any]]:
    try:
        print(f"Scraping jobs from {source['name']}...")
        board = Board(
            company=source["name"],  func=source["function"],  url=source["url"],
            location_qualifiers=source['location_qualifiers'],
            job_title_qualifiers=source['job_qualifiers'],
            job_title_disqualifiers=source['job_disqualifiers'],
            visited_ids = visited_ids
        )
        jobs = func(board)
        return source["function"], jobs
    except Exception as e:
        print(f"Exception while scraping jobs from {source['name']}: {e}")
        return source["function"], []


if __name__ == "__main__":
    start_time = time.time()  # Record start time

    # Load visited.json if it exists
    visited_filename = "visited.json"
    try:
        with open(visited_filename, "r", encoding="utf-8") as f:
            visited_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        visited_data = {}  # Initialize as empty dictionary if file not found or corrupt

    # Load filed.json if it exists
    filed_filename = "filed.json"
    try:
        with open(filed_filename, "r", encoding="utf-8") as f:
            filed_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        filed_data = {}  # Initialize as empty dictionary if file not found or corrupt

    # Merge filed.json into visited.json
    for company, job_ids in filed_data.items():
        if company in visited_data:
            # Merge job IDs, avoiding duplicates
            visited_data[company] = list(set(visited_data[company]) | set(job_ids))
        else:
            visited_data[company] = job_ids  # Directly add new company data

    # Save the updated visited.json
    with open(visited_filename, "w", encoding="utf-8") as f:
        json.dump(visited_data, f, indent=4)

    with open(filed_filename, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=4)

    print(f"Merged job IDs into {visited_filename}.")

    # List to accumulate job data
    all_jobs = []
    filed_data = defaultdict(list)  # Dictionary to store company-wise job IDs

    # 🧠 Multiprocessing Part
    function_map = function_init()  # Load or generate the function_map
    visited_data = visited_data_load()  # Load visited ids

    tasks = []
    for source in job_sources:
        func_name = source["function"]
        func = function_map.get(func_name)
        visited_ids = visited_data.get(func_name, [])
        if func is not None:
            tasks.append((source, func, visited_ids))
        else:
            print(f"Function {func_name} not found in function_map. Skipping {source['name']}.")

    efficiency = 50   # For peak performance, do not use all cpus
    cpu_cores = int(cpu_count() * (efficiency/100))
    with Pool(processes=min(cpu_cores, len(tasks))) as pool:
        results = pool.starmap(scrape_source, tasks)

    for source_name, jobs in results:
        if jobs:
            all_jobs.extend(jobs)
            filed_data[source_name].extend([job.id for job in jobs])

    # Save to CSV
    csv_filename = "job_listings.csv"

    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow(["Company", "Job ID", "Title", "Location", "URL", "Content", "Published At"])

        # Write job data
        for job in all_jobs:
            writer.writerow([
                job.company, job.id, job.title, job.location, job.url,
                job.content if hasattr(job, "content") else "N/A",
                job.published_at if hasattr(job, "published_at") else "N/A"
            ])

    print(f"Scraping complete. Data saved to {csv_filename}.")
    os.startfile(csv_filename)

    with open(filed_filename, "w", encoding="utf-8") as f:
        json.dump(filed_data, f, indent=4)
    print(f"Job IDs saved to {filed_filename}.")

    end_time = time.time()
    elapsed_seconds = end_time - start_time
    minutes = int(elapsed_seconds // 60)
    seconds = int(elapsed_seconds % 60)

    print(f"Time taken: {minutes} minutes and {seconds} seconds")
