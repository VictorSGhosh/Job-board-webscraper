from collections import defaultdict

from typing import List, Callable, Any, Optional

import requests
from selenium import webdriver
from selenium.common import NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, ParseResult, urlunparse, urljoin, quote, parse_qsl, urlencode

import time
import json
import re

from classes import Job

## WebDriver Functions
qualifiers = None

def function_init():
    function_map = {
        "beyondtrust": beyondtrust,     "cloudflare": cloudflare,   "enverus": enverus,             "fidelity": fidelity,           "adp":adp,              "atlassian": atlassian,
        "aristocrat": aristocrat,

        "fanduel": cmn_scraper1_1,      "sprout_social": cmn_scraper1_2,

        # iCiMS Career Pages
        "github": cmn_scraper11,        "sita": cmn_scraper11,      "osi_systems": cmn_scraper11,

        "magnite": cmn_scraper13_1,     "pjt": cmn_scraper13_1,     "motorola": cmn_scraper13_2,    "lego": cmn_scraper13_2,        "pernod_richard": cmn_scraper13_2, "thomson_reuters": cmn_scraper13_2,
        "epicor": cmn_scraper13_2,      "sony": cmn_scraper13_3,        "kion": cmn_scraper13_3,    "f5": cmn_scraper13_4,          "rbs": cmn_scraper13_4,         "accenture": cmn_scraper13_5,

        # Oracle Cloud Pages
        "oracle": cmn_scraper14,        "akamai": cmn_scraper14,    "honeywell": cmn_scraper14,

        "varonis": cmn_scraper15_1,     "pulsepoint": cmn_scraper15_1,

        "hme": cmn_scraper16,
    }
    # Dictionary to map function names to actual functions
    return function_map


def infer_scraper_from_url(url: str) -> Optional[Callable[[Any], List[Any]]]:
    hostname = urlparse(url.lower()).hostname or ""

    url_rules = [
        (r"\.greenhouse\.", cmn_scraper1), (r"\.lever\.co$", cmn_scraper2), (r"ashbyhq", cmn_scraper3), (r"workable", cmn_scraper4), (r"smartrecruiters", cmn_scraper5),
        (r"rippling", cmn_scraper6), (r"bamboohr", cmn_scraper7), (r"\.adp\.", cmn_scraper8), (r"\.gem\.", cmn_scraper9), (r"jobs\.dayforcehcm\.com$", cmn_scraper10), (r"^(?:https?://)?(?:www\.)?(?:careers|jobs)\.(?!jobvite\.com)", cmn_scraper11), # API Calls

        (r"\.icims\.", cmn_scraper12), (r"myworkday(?:jobs|site)", cmn_scraper13), (r"oraclecloud", cmn_scraper14), (r"jobvite", cmn_scraper15), (r"ultipro", cmn_scraper16), (r"\.paylocity\.", cmn_scraper17), (r"applytojob", cmn_scraper18), # Webscraper
    ]

    for pattern, scraper_func in url_rules:
        if re.search(pattern, hostname):
            return scraper_func

    return None


# Setup Selenium WebDriver (in headless mode)
def visited_data_load():
    # Load visited.json
    visited_filename = "visited.json"
    try:
        with open(visited_filename, "r", encoding="utf-8") as f:
            visited_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        visited_data = {}  # Fallback to an empty dictionary

    # Ensure visited_data is a defaultdict
    if not isinstance(visited_data, defaultdict):
        visited_data = defaultdict(list, visited_data)  # Initialize as empty dictionary if file not found or corrupt

    return visited_data


def webscraper_driver_init():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode

    # global driver  # Setup WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver


# Prepare URL
def webscraper_driver_get(driver, url):
    # global driver
    driver.get(url)
    time.sleep(1)


# Driver Clean up
def webscraper_driver_cleanup(driver):
    # global driver
    driver.quit()


## Qualifier Functions
def is_valid_location(location, location_qualifiers):
    return any(location_qualifier.lower() in location.lower() for location_qualifier in location_qualifiers) if location_qualifiers else True

def is_valid_title(job_title, title_qualifiers, title_disqualifiers):
    return ((any(title_qualifier.lower() in job_title.lower() for title_qualifier in title_qualifiers) if title_qualifiers else True) and
            (not any(title_disqualifier.lower() in job_title.lower() for title_disqualifier in title_disqualifiers) if title_disqualifiers else True))

def is_id_visited(job_id, visited_ids):
    return str(job_id) in visited_ids

def is_valid(job_id, job_location, job_title, board):
    location_qualifiers = board.location_qualifiers
    job_title_qualifiers = board.job_title_qualifiers
    job_title_disqualifiers = board.job_title_disqualifiers

    visited_ids = board.visited_ids

    loc_q = is_valid_location(job_location, location_qualifiers)
    title_q = is_valid_title(job_title, job_title_qualifiers, job_title_disqualifiers)
    visit_q = is_id_visited(str(job_id), visited_ids)
    return loc_q and title_q and not visit_q


### Helper Fns
def get_full_url_and_id(parsed_url: ParseResult):
    prefix = "https://boards.greenhouse.io" if not parsed_url.scheme and not parsed_url.netloc else ""
    url = (prefix + parsed_url.path) if prefix else f"{urlunparse(parsed_url)}"
    id = id if (id := parsed_url.path.split('/')[-1]).isdigit() else parsed_url.query.split('=')[-1]
    return url, id

def print_jobs(job_list: List[Job]) -> None:
    # Print jobs
    for job in job_list:
        print(job)


## Common WebScrapers
# GreenHouse Webscraper using API calls [Faster]
def cmn_scraper1(board=None):
    api_func = board.url.split("for=")[-1].split("&")[0] if "for=" in board.url else urlparse(board.url).path.lstrip("/")
    resp = requests.get(f"https://boards-api.greenhouse.io/v1/boards/{api_func}/jobs")
    resp.raise_for_status()  # throw error if request failed

    job_posts = resp.json().get("jobs", [])

    jobs_list = []
    company = board.company
    for job in job_posts:
        job_id = job.get("id")
        job_title = job.get("title")
        job_url = job.get("absolute_url")
        job_location = job.get("location").get("name") or "None"

        if is_valid(job_id, job_location, job_title, board):
            jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    return jobs_list

def cmn_scraper1_1(board=None):
    job_list = cmn_scraper1(board)
    for job in job_list:
        job.url = f"https://boards.greenhouse.io/embed/job_app?for={board.func}&token={job.id}"
    return job_list

def cmn_scraper1_2(board=None):
    job_list = cmn_scraper1(board)

    def clean_url(url):
        parsed = urlparse(url)

        # Remove query and fragment
        clean_path = parsed.path.rstrip('/')  # remove trailing slash
        return urlunparse((parsed.scheme, parsed.netloc, clean_path, '', '', ''))  # remove params, query, fragment

    for job in job_list:
        job.url = clean_url(job.url)
    return job_list

# Using Lever API to scrape lever job postings
def cmn_scraper2(board):
    api_func = urlparse(board.url).path.lstrip("/")
    resp = requests.get(f"https://api.lever.co/v0/postings/{api_func}?mode=json")
    resp.raise_for_status()  # throw error if request failed

    job_posts = resp.json()

    jobs_list = []
    company = board.company
    for job in job_posts:
        job_id = job.get("id")
        job_title = job.get("text")
        job_url = job.get("hostedUrl")
        job_location = "; ".join(job.get("categories", {}).get("allLocations", []))

        if is_valid(job_id, job_location, job_title, board):
            jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    return jobs_list

def cmn_scraper3(board=None):
    api_func =  urlparse(board.url).path.lstrip("/")
    resp = requests.get(f"https://api.ashbyhq.com/posting-api/job-board/{api_func}")
    resp.raise_for_status()  # throw error if request failed

    job_posts = resp.json().get("jobs", [])

    jobs_list = []
    company = board.company
    for job in job_posts:
        job_id = job.get("id")
        job_title = job.get("title")
        job_url = job.get("jobUrl")
        job_location = job.get("location")

        if is_valid(job_id, job_location, job_title, board):
            jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    return jobs_list

def cmn_scraper4(board=None):
    jobs_list = []
    company = board.company

    api_func =  urlparse(board.url).path.strip("/")
    api_url = f"https://apply.workable.com/api/v3/accounts/{api_func}/jobs"

    response = requests.post(api_url)
    response.raise_for_status()
    data = response.json()

    jobs_posts = data.get("results", [])
    for job in jobs_posts:
        job_id, job_title = job.get("id"), job.get("title")
        locations = job.get("locations") or {}
        job_location = "; ".join([", ".join(filter(None, [location.get("city"), location.get("region"), location.get("country")])) for location in locations])
        shortcode = job.get("shortcode")
        job_url = f"https://apply.workable.com/{api_func}/j/{shortcode}/"

        if is_valid(job_id, job_location, job_title, board):
            jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    return jobs_list


def cmn_scraper5(board=None):
    offset = 0
    LIMIT = 100

    jobs_list = []
    company = board.company
    api_func = urlparse(board.url).path.lstrip("/")
    base_url = f"https://api.smartrecruiters.com/v1/companies/{api_func}/postings"

    while offset <= 1000:
        params = {
            "limit": LIMIT,
            "offset": offset
        }

        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        job_posts = data.get("content", [])
        if not job_posts:
            break

        for job in job_posts:
            job_id = job.get("id")
            job_title = job.get("name")
            job_url = job.get("ref")
            location = job.get("location", {})
            job_location = location.get("fullLocation").replace(", ,", ",") or ", ".join(
                filter(None, [
                    location.get("city"),
                    location.get("region"),
                    location.get("country")
                ])
            )

            if is_valid(job_id, job_location, job_title, board):
                jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

        offset += LIMIT
        if offset >= data.get("totalFound", 0):
            break

    for job in jobs_list:
        job_id = job.id
        detail_url = f"https://api.smartrecruiters.com/v1/companies/{api_func}/postings/{job_id}"
        detail_response = requests.get(detail_url, timeout=30)
        detail_response.raise_for_status()
        detail_data = detail_response.json()
        job.url =  detail_data.get("postingUrl")

    return jobs_list

# Rippling WebScraper Function using API calls [Faster]
def cmn_scraper6(board=None):
    jobs_list = []
    company = board.company

    company_key = urlparse(board.url).path.split("/")[-2]
    country = parse_qs(urlparse(board.url).query).get("country", [""])[0]

    url = f"https://api.rippling.com/platform/api/ats/v2/board/{company_key}/jobs?country={country}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        jobs = response.json().get("items", [])

        for job in jobs:
            job_id = job.get("id") or job.get("uuid")
            job_title = job.get("name", "").strip()
            job_url = job.get("url", "").strip()

            # Join all location names from the 'locations' list
            locations = job.get("locations", [])
            job_location = "; ".join(loc.get("name", "") for loc in locations)

            if is_valid(job_id, job_location, job_title, board):
                jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    except requests.exceptions.RequestException as e:
        print(f"Company {board.company} API request failed: {e}")
        return []

    return jobs_list


def cmn_scraper7(board=None):
    jobs_list = []
    company = board.company

    api_url = f"{board.url}/list"
    response = requests.get(api_url, timeout=30)
    response.raise_for_status()
    data = response.json()
    job_posts = data.get("result", [])

    # Convert a BambooHR location object into a readable string.
    def format_location(location: dict) -> str | None:
        if not location:
            return None

        parts = [
            location.get("city"),
            location.get("state"),
            location.get("province"),
            location.get("country"),
        ]

        # Remove None / empty values
        parts = [p for p in parts if p]
        return ", ".join(parts) if parts else None

    for job in job_posts:
        job_id = job.get("id")
        job_title = job.get("jobOpeningName")
        job_location = format_location(job.get("location")) or format_location(job.get("atsLocation")) or "Not Specified"
        job_url = f"{board.url}/{job_id}"

        if is_valid(job_id, job_location, job_title, board):
            jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    return jobs_list


def extract_adp_func(url: str) -> str:
    pattern = r"https://myjobs\.adp\.com/(?P<api_func>[^/]+)/cx/"
    match = re.search(pattern, url)
    if not match:
        raise ValueError("Could not extract ADP site id")
    return match.group("api_func")

def encode_filter_expression(url: str):
    params = parse_qs(urlparse(url).query)
    raw_filter = " && ".join(
        f"{field} eq '{value}'"
        for field, values in params.items()
        for value in values
    )
    return quote(raw_filter, safe="")

def fetch_jobs_token(api_func: str) -> str:
    api_url = f"https://myjobs.adp.com/public/staffing/v1/career-site/{api_func}"
    response = requests.get(api_url)
    response.raise_for_status()
    return response.json().get("myJobsToken", None)

def fetch_adp_jobs(token, filter_expr):
    job_list_url = f"https://my.adp.com/myadp_prefix/mycareer/public/staffing/v1/job-requisitions/apply-custom-filters?$select=reqId,jobTitle,jobDescription,clientRequisitionID,requisitionLocations&$filter={filter_expr}&$top=100"
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Myjobstoken": token,
    }
    resp = requests.get(job_list_url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json().get("jobRequisitions", [])

def fetch_adp_job_details(job, api_func: str) -> tuple:
    job_id = job.get("clientRequisitionID")
    job_reqID = job.get("reqId")
    job_title = job.get("jobTitle")
    job_description = job.get("jobDescription")

    job_url = f"https://myjobs.adp.com/{api_func}/cx/job-details?reqId={job_reqID}"
    locations = []
    for loc in job.get("requisitionLocations", []):
        addr = loc.get("address", {})
        city = addr.get("cityName")
        country = addr.get("country", {}).get("longName")
        if city and country:
            locations.append(f"{city}, {country}")
        elif country:
            locations.append(country)
    job_location = "; ".join(locations) or "Unknown"
    return job_id, job_title, job_location, job_url, job_description

def cmn_scraper8(board=None):
    jobs_list = []

    api_func = extract_adp_func(board.url)
    encoded_filter = encode_filter_expression(board.url)
    my_jobs_token = fetch_jobs_token(api_func)

    job_posts = fetch_adp_jobs(my_jobs_token, encoded_filter)
    for job in job_posts:
        job_id, job_title, job_location, job_url, _ = fetch_adp_job_details(job, api_func)

        if is_valid(job_id, job_location, job_title, board):
            jobs_list.append(Job(board.company, job_id, job_title, job_location, job_url))

    return jobs_list


def cmn_scraper9(board=None):
    # API Endpoint
    jobs_list = []
    company = board.company
    board_id = urlparse(board.url).path.split("/")[-1]

    gem_url = "https://jobs.gem.com/api/public/graphql/batch"
    payload = [
        {
            "operationName": "JobBoardList",
            "variables": {"boardId": board_id},
            "query": """
                query JobBoardList($boardId: String!) {
                    oatsExternalJobPostings(boardId: $boardId) {
                        jobPostings {
                            id
                            extId
                            title
                            descriptionHtml
                            locations {
                                name
                                city
                                isoCountry
                                isRemote
                            }
                        }
                    }
                }
            """
        }
    ]

    # Headers
    headers = {
        "accept": "*/*",
        "content-type": "application/json"
    }

    # Send POST request
    response = requests.post(gem_url, headers=headers, data=json.dumps(payload))

    # Parse JSON response
    data = response.json()

    # Navigate to job postings
    jobs = data[0]['data']['oatsExternalJobPostings']['jobPostings']

    # Print each job title + location
    for job in jobs:
        job_id = job['id'][-8:].strip('=')  # Extract last 8 characters of ID
        job_title = job['title']
        locations = job['locations']
        ext_id = job['extId']
        job_url = f"{board.url}/{ext_id}"
        job_location = ", ".join([loc['name'] for loc in locations]) if locations else "N/A"

        if is_valid(job_id, job_location, job_title, board):
            jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    return jobs_list

def format_locations(posting_locations):
    locations = []

    for location in posting_locations:
        values = []
        for field in ("cityName", "stateCode", "formattedAddress"):
            (value:= location.get(field)) and value not in values and values.append(value)
        values and locations.append(", ".join(values))

    return "; ".join(locations) if locations else "Not specified"

def cmn_scraper10(board):
    jobs_list = []
    company = board.company
    parsed = urlparse(board.url)
    parts = parsed.path.strip("/").split("/")

    if len(parts) not in (2, 3):
        raise ValueError("Invalid Dayforce job board URL")

    client_namespace, job_board_code = parts[-2:]

    session = requests.Session()

    # Get CSRF token
    csrf_response = session.get("https://jobs.dayforcehcm.com/api/auth/csrf")
    csrf_response.raise_for_status()
    csrf_token = csrf_response.json()["csrfToken"]

    headers = {
        "Content-Type": "application/json",
        "x-csrf-token": csrf_token
    }
    search_url = (
        f"https://jobs.dayforcehcm.com/api/geo/"
        f"{client_namespace}/jobposting/search"
    )
    body = {
        "clientNamespace": client_namespace,
        "jobBoardCode": job_board_code,
        "cultureCode": "en-US",
        "distanceUnit": 0,
        "paginationStart": 0
    }

    jobs = []

    while True:
        response = session.post(search_url, headers=headers, json=body)
        response.raise_for_status()

        data = response.json()
        page_jobs = data.get("jobPostings", [])

        if not page_jobs:
            break

        jobs.extend(page_jobs)
        total_count = data.get("maxCount", len(page_jobs))

        if len(jobs) >= total_count:
            break

        body["paginationStart"] += 25


    for job in jobs:
        job_id = job.get("jobPostingId")
        job_title = job.get("jobTitle")
        job_location = format_locations(job.get("postingLocations") or [])
        job_url = (
            f"https://jobs.dayforcehcm.com/en-US/"
            f"{client_namespace}/"
            f"{job_board_code}/"
            f"jobs/{job_id}"
        )
        if is_valid(job_id, job_location, job_title, board):
            jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    return jobs_list

def slugify(title: str) -> str:
    # lowercase
    title = title.lower()

    # replace non-alphanumeric with hyphens
    title = re.sub(r"[^a-z0-9]+", "-", title)

    # remove leading/trailing hyphens
    return title.strip("-")

# iCiMS API Caller
def cmn_scraper11(board=None):
    jobs_list = []
    company = board.company
    job_board_url = board.url

    parsed = urlparse(job_board_url)

    # Preserve all existing query parameters
    params = dict(parse_qsl(parsed.query))

    # Required by the API
    params.setdefault("internal", "false")
    path = parsed.path

    api_path = "/api/jobs" if path == "/jobs" else re.sub(r"/[^/]+(?=/jobs$)", "/api", path)

    request_url = parsed._replace(
        path=api_path,
        query=urlencode(params),
    ).geturl()
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/138.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(request_url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    data = response.json()

    for item in data.get("jobs", []):
        job = item.get("data", {})
        job_id = job.get("req_id") or job.get("slug")
        job_title = job.get("title")
        job_location =  job.get("full_location") or job.get("location_name")
        job_url = job.get("meta_data", {}).get("canonical_url") or (lambda p: f"{p.scheme}://{p.netloc}/jobs/{job_id}/{slugify(job_title)}/job")(urlparse(job.get("apply_url")))

        if is_valid(job_id, job_location, job_title, board):
            jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    return jobs_list

# iCiMS Web-Crawler
def cmn_scraper12(board=None):
    jobs_list = []
    company = board.company
    base_url = board.url  # Base URL without pagination parameter
    headers = {"User-Agent": "Mozilla/5.0"}  # Prevent blocking by servers

    page_number = 0  # Start pagination from page 1

    while True:
        paginated_url = f"{base_url}&pr={page_number}"  # Append pagination parameter
        response = requests.get(paginated_url, headers=headers)

        if response.status_code != 200:
            break  # Stop if the request fails

        soup = BeautifulSoup(response.text, "html.parser")
        job_entries = soup.find_all("div", class_="row")  # Adjust based on actual structure

        if not job_entries:
            break  # Stop if no more jobs are found on the page

        for job in job_entries:
            job_title_element = job.find("h3")
            job_title = job_title_element.text.strip() if job_title_element else "N/A"

            job_link = job.find("a", class_="iCIMS_Anchor")
            job_url = job_link["href"] if job_link else "N/A"
            job_id = job_url.split("/")[-3] if job_url != "N/A" else "N/A"

            location_element = job.find("span", string=re.compile(r"^(Job Locations|Location|Location : Location)$"))
            job_location = location_element.parent.find_all("span")[-1].text.strip() if location_element else "N/A"

            if location_element is None or job_location in ["Job Locations", "Location"]:
                job_location = ", ".join(
                    [span.find("dd").text.strip() for span in reversed([div for div in job.find_all("div", class_="iCIMS_JobHeaderTag") if div.find("dt").find("span", class_="glyphicons glyphicons-map-marker") if div.find("dt")])])

            if is_valid(job_id, job_location, job_title, board):
                jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

        page_number += 1  # Move to the next page
    return jobs_list


def cmn_scraper13(board):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)
    time.sleep(3)
    wait = WebDriverWait(driver, 5)

    jobs_list = []
    company = board.company

    while True:
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Find all job listings
        job_posts = soup.find_all("li", class_="css-1q2dra3")

        for job in job_posts:
            job_title_elem = job.find("a", {"data-automation-id": "jobTitle"})
            job_location_elem = job.find("div", {"data-automation-id": "locations"})  # Location
            job_id_elem = job.find("li", class_="css-h2nt8k")  # Job ID

            # Extract job location from <dd> inside the location <div>
            job_location = "Not specified"
            if job_location_elem:
                location_dd = job_location_elem.find("dd", class_="css-129m7dg")
                if location_dd:
                    job_location = location_dd.text.strip()

            if job_title_elem:
                job_url = urljoin(board.url, job_title_elem["href"]).split('?', 1)[0]
                job_title = job_title_elem.text.strip()
                job_id = job_id_elem.text.strip() if job_id_elem else "N/A"

                if is_valid(job_id, job_location, job_title, board) and job_id not in [job.id for job in jobs_list]:
                    jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

        # Try to click the "Next" button if it exists
        try:
            # Locate the Next button using 'data-uxi-element-id'
            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-uxi-element-id='next']")))
            driver.execute_script("arguments[0].scrollIntoView();", next_button)  # Scroll to button
            driver.execute_script("arguments[0].click();", next_button)  # Click using JavaScript
            print("Navigating to next page...")
            time.sleep(1)
        except:
            print("No more pages to navigate.")
            break  # Exit loop if no "Next" button is found

    webscraper_driver_cleanup(driver)
    return jobs_list

def cmn_scraper13_1(board=None):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)
    time.sleep(1)
    wait = WebDriverWait(driver, 5)

    jobs_list = []
    company = board.company

    while True:
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Find all job listings
        job_posts = soup.find_all("li", class_="css-1q2dra3")

        for job in job_posts:
            job_title_elem = job.find("a", {"data-automation-id": "jobTitle"})
            job_location_elem = job.find("div", {"data-automation-id": "locations"})  # Location
            job_id_elem = job.find("li", class_="css-h2nt8k")  # Job ID

            # Extract job location from <dd> inside the location <div>
            job_location = "Not specified"
            if job_location_elem:
                location_dd = job_location_elem.find("dd", class_="css-129m7dg")
                if location_dd:
                    job_location = location_dd.text.strip()

            if job_title_elem:
                job_url = urljoin(board.url, job_title_elem["href"]).split('?', 1)[0]
                job_title = job_title_elem.text.strip()
                job_id = job_id_elem.text.strip() if job_id_elem else "N/A"

                if is_valid(job_id, job_location, job_title, board):
                    # Visit the job URL to extract the job ID
                    try:
                        webscraper_driver_get(driver, job_url)
                        time.sleep(1)
                        job_soup = BeautifulSoup(driver.page_source, "html.parser")

                        # Try to locate the job ID element on the detail page
                        job_id_elem = job_soup.find("div", {"data-automation-id": "requisitionId"})
                        job_id = "N/A"
                        if job_id_elem:
                            job_id_dd = job_id_elem.find("dd", class_="css-129m7dg")
                            if job_id_dd:
                                job_id = job_id_dd.text.strip()
                    except Exception as e:
                        print(f"Error visiting job URL: {job_url} — {str(e)}")
                        job_id = "N/A"

                    # Return to the listings page before continuing
                    webscraper_driver_get(driver, board.url)
                    time.sleep(1)
                    if job_id != "N/A" and not is_id_visited(job_id, board.visited_ids):
                        jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

        # Try to click the "Next" button if it exists
        try:
            # Locate the Next button using 'data-uxi-element-id'
            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-uxi-element-id='next']")))
            driver.execute_script("arguments[0].scrollIntoView();", next_button)  # Scroll to button
            driver.execute_script("arguments[0].click();", next_button)  # Click using JavaScript
            print("Navigating to next page...")
            time.sleep(1)
        except:
            print("No more pages to navigate.")
            break  # Exit loop if no "Next" button is found

    webscraper_driver_cleanup(driver)
    return jobs_list

def cmn_scraper13_2(board):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)
    time.sleep(1)
    wait = WebDriverWait(driver, 10)

    jobs_list = []
    company = board.company

    while True:
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Find all job listings
        job_posts = soup.find_all("li", class_="css-1q2dra3")

        for job in job_posts:
            job_title_elem = job.find("a", {"data-automation-id": "jobTitle"})
            job_id_elem_list = job.find_all("li", class_="css-h2nt8k")

            if job_title_elem:
                job_url = urljoin(board.url, job_title_elem["href"]).split('?', 1)[0]
                job_title = job_title_elem.text.strip()
                job_location, job_id  = [";".join([elem.text.strip() for elem in job_id_elem_list][:-1]), job_id_elem_list[-1].text.strip()] if job_id_elem_list else ["N/A", "N/A"]
                if is_valid(job_id, job_location, job_title, board) and job_id not in [job.id for job in jobs_list]:
                    jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

        # Try to click the "Next" button if it exists
        try:
            # Locate the Next button using 'data-uxi-element-id'
            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-uxi-element-id='next']")))
            driver.execute_script("arguments[0].scrollIntoView();", next_button)  # Scroll to button
            driver.execute_script("arguments[0].click();", next_button)  # Click using JavaScript
            print("Navigating to next page...")
            time.sleep(1)
        except:
            print("No more pages to navigate.")
            break  # Exit loop if no "Next" button is found

    webscraper_driver_cleanup(driver)
    return jobs_list

def cmn_scraper13_3(board):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)
    time.sleep(1)
    wait = WebDriverWait(driver, 5)

    jobs_list = []
    company = board.company

    while True:
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Find all job listings
        job_posts = soup.find_all("li", class_="css-1q2dra3")

        for job in job_posts:
            job_title_elem = job.find("a", {"data-automation-id": "jobTitle"})
            job_location_elem = job.find("dd", class_="css-129m7dg")  # Location
            job_id_list = job.find_all("li", class_="css-h2nt8k")

            if job_title_elem:
                job_url = urljoin(board.url, job_title_elem["href"]).split('?', 1)[0]
                job_title = job_title_elem.text.strip()
                job_location = job_location_elem.text.strip() if job_location_elem else "Not specified"
                job_id = job_id_list[0].text.strip() if job_id_list and len(job_id_list) > 1 else "N/A"

                if is_valid(job_id, job_location, job_title, board) and job_id not in [job.id for job in jobs_list]:
                    jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

        # Try to click the "Next" button if it exists
        try:
            # Locate the Next button using 'data-uxi-element-id'
            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-uxi-element-id='next']")))
            driver.execute_script("arguments[0].scrollIntoView();", next_button)  # Scroll to button
            driver.execute_script("arguments[0].click();", next_button)  # Click using JavaScript
            print("Navigating to next page...")
            time.sleep(1)
        except:
            print("No more pages to navigate.")
            break  # Exit loop if no "Next" button is found

    webscraper_driver_cleanup(driver)
    return jobs_list


def cmn_scraper13_4(board):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)
    wait = WebDriverWait(driver, 5)

    jobs_list = []
    company = board.company

    while True:
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Find all job listings
        job_posts = soup.find_all("li", class_="css-1q2dra3")

        for job in job_posts:
            job_title_elem = job.find("a", {"data-automation-id": "jobTitle"})
            job_location_elem = job.find("dd", class_="css-129m7dg")  # Location
            job_id_list = job.find_all("li", class_="css-h2nt8k")

            if job_title_elem:
                job_url = urljoin(board.url, job_title_elem["href"]).split('?', 1)[0]
                job_title = job_title_elem.text.strip()
                job_location = job_location_elem.text.strip() if job_location_elem else "Not specified"
                job_id = job_id_list[-1].text.strip() if job_id_list and len(job_id_list) > 1 else "N/A"

                if is_valid(job_id, job_location, job_title, board) and job_id not in [job.id for job in jobs_list]:
                    jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

        # Try to click the "Next" button if it exists
        try:
            # Locate the Next button using 'data-uxi-element-id'
            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-uxi-element-id='next']")))
            driver.execute_script("arguments[0].scrollIntoView();", next_button)  # Scroll to button
            driver.execute_script("arguments[0].click();", next_button)  # Click using JavaScript
            print("Navigating to next page...")
            time.sleep(1)
        except:
            print("No more pages to navigate.")
            break  # Exit loop if no "Next" button is found

    webscraper_driver_cleanup(driver)
    return jobs_list

def cmn_scraper13_5(board):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)
    time.sleep(1)
    wait = WebDriverWait(driver, 10)

    jobs_list = []
    company = board.company

    while True:
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Find all job listings
        job_posts = soup.find_all("li", class_="css-1q2dra3")

        for job in job_posts:
            job_title_elem = job.find("a", {"data-automation-id": "jobTitle"})
            job_id_elem_list = job.find_all("li", class_="css-h2nt8k")

            if job_title_elem:
                job_url = urljoin(board.url, job_title_elem["href"]).split('?', 1)[0]
                job_title = job_title_elem.text.strip()
                job_id, job_location   = [elem.text.strip() for elem in job_id_elem_list][:2] if job_id_elem_list else ["N/A", "N/A"]

                if is_valid(job_id, job_location, job_title, board) and not job_id.startswith("ATC"):
                    jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

        # Try to click the "Next" button if it exists
        try:
            # Locate the Next button using 'data-uxi-element-id'
            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-uxi-element-id='next']")))
            driver.execute_script("arguments[0].scrollIntoView();", next_button)  # Scroll to button
            driver.execute_script("arguments[0].click();", next_button)  # Click using JavaScript
            print("Navigating to next page...")
            time.sleep(1)
        except:
            print("No more pages to navigate.")
            break  # Exit loop if no "Next" button is found

    webscraper_driver_cleanup(driver)
    return jobs_list


def scroll_to_load_jobs(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)  # Allow time for jobs to load

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:  # If the height doesn't change, stop scrolling
            print("Reached the end of the page.")
            break
        last_height = new_height  # No button available, continue scrolling


def click_show_more(driver):
    """Finds and clicks the 'Show More Results' button until it's no longer available."""
    wait = WebDriverWait(driver, 10)
    while True:
        try:
            # Find the button
            show_more_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[contains(text(), 'Show More Results')]] | //button[contains(text(), 'Show more')]")))
            show_more_button.click()
            print("Clicked 'Show More Results' button.")
            time.sleep(1)

        except Exception:
            print("No more 'Show More Results' button found.")
            break

def grid_style_job_posts(driver, board=None):
    jobs_list = []
    company = board.company
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_posts = soup.find_all("div", class_="job-tile job-grid-item search-results job-grid-item--all-actions-visible") or soup.find_all("div", class_="job-tile job-grid-item search-results job-grid-item--layout1 job-grid-item--all-actions-visible")

    for job_tile in job_posts:
        # Job URL and ID from <a> tag
        a_tag = job_tile.find('a', class_='job-grid-item__link')
        job_id, job_url = None, None
        if a_tag and 'href' in a_tag.attrs:
            job_url = a_tag['href'].split("?")[0]
            job_id = job_url.split('/job/')[-1].split('/')[0]

        job_title = job_tile.find("span", class_="job-tile__title").text.strip() if job_tile.find("span", class_="job-tile__title") else None
        job_location = job_tile.find("span", attrs={"data-bind": "html: primaryLocation"}).text.strip() if job_tile.find("span", attrs={"data-bind": "html: primaryLocation"}) else None

        if is_valid(job_id, job_location, job_title, board):
            jobs_list.append(Job(company, job_id, job_title, job_location, job_url))
    return jobs_list


def list_style_job_posts(driver, board=None):
    jobs_list = []
    company = board.company

    job_posts = driver.find_elements(By.CLASS_NAME, "search-results.job-tile.job-list-item")
    for job in job_posts:
        try:
            job_title = job.find_element(By.CLASS_NAME, "job-tile__title").text  # Extract job title
            job_url = job.find_element(By.CLASS_NAME, "job-list-item__link").get_attribute("href").split("?")[0]  # Extract job URL
            job_id = re.search(r'/job/([a-zA-Z0-9]+)/', job_url).group(1)
            job_location = job.find_element(By.CLASS_NAME, "job-list-item__job-info-value").text  # Extract location
            job_location = job_location.replace('\n', ' ')
            if is_valid(job_id, job_location, job_title, board):
                jobs_list.append(Job(company, job_id, job_title, job_location, job_url))
        except Exception:
            continue  # Skip if any field is missing
    return jobs_list

# Oracle Cloud WebPages
def cmn_scraper14(board=None):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)
    time.sleep(2)

    # Keep clicking "Show more jobs" and scrolling until all jobs are loaded
    scroll_to_load_jobs(driver)
    click_show_more(driver)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_posts = soup.find_all("div", class_="job-tile job-grid-item search-results job-grid-item--all-actions-visible") or soup.find_all("div", class_="job-tile job-grid-item search-results job-grid-item--layout1 job-grid-item--all-actions-visible")
    jobs_list = grid_style_job_posts(driver, board) if job_posts else list_style_job_posts(driver, board)

    webscraper_driver_cleanup(driver)
    return jobs_list

# JobVite Web-Crawler
def cmn_scraper15(board=None):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)
    jobs_list = []
    company = board.company

    while True:  # Pagination loop
        time.sleep(2)  # Allow time for elements to load
        job_posts = driver.find_elements(By.XPATH, "//tr[td[@class='jv-job-list-name']]")

        for job in job_posts:
            outer_html = job.get_attribute("outerHTML")
            soup = BeautifulSoup(outer_html, "html.parser")

            job_title_elem = soup.find("td", class_="jv-job-list-name").find("a")
            job_location_elem = soup.find("td", class_="jv-job-list-location")

            if job_location_elem and job_title_elem:
                job_id = job_title_elem["href"].split("/")[-1]  # Extract job ID
                job_title = job_title_elem.text.strip()  # Extract job title
                job_url = f"https://jobs.jobvite.com{job_title_elem['href']}"  # Construct full job URL
                job_location = "".join(job_location_elem.text.replace("\n", "").split("  "))  # Clean location text

                if is_valid(job_id, job_location, job_title, board):
                    jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

        # Check if "Next" button exists
        try:
            next_button = driver.find_element(By.XPATH, "//a[contains(@class, 'jv-pagination-next')]")
            if "disabled" in next_button.get_attribute("class"):  # Check if the button is disabled
                break  # Stop pagination if no more pages
            next_button.click()  # Click to load next page
            time.sleep(2)  # Wait for the next page to load
        except (NoSuchElementException, ElementClickInterceptedException):
            break  # Stop pagination if button is missing

    webscraper_driver_cleanup(driver)
    return jobs_list

def cmn_scraper15_1(board=None):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)
    jobs_list = []
    company = board.company

    while True:  # Pagination loop
        time.sleep(2)  # Allow time for elements to load
        job_posts = driver.find_elements(By.XPATH, "//li[@class='row']")

        for job in job_posts:
            outer_html = job.get_attribute("outerHTML")
            soup = BeautifulSoup(outer_html, "html.parser")

            job_title_elem = soup.find("div", class_="jv-job-list-name")
            job_url_elem = soup.find("a")
            job_location_elem = soup.find("div", class_="jv-job-list-location")

            if job_location_elem and job_title_elem:
                job_id = urlparse(job_url_elem["href"]).path.split("/")[-1]  # Extract job ID
                job_title = job_title_elem.text.strip()  # Extract job title
                job_url = f"https://jobs.jobvite.com{job_url_elem['href']}"  # Construct full job URL
                job_location = " ".join(job_location_elem.text.replace("\n", "").strip().split())  # Clean location text

                if is_valid(job_id, job_location, job_title, board):
                    jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

        # Check if "Next" button exists
        try:
            next_button = driver.find_element(By.XPATH, "//a[contains(@class, 'jv-pagination-next')]")
            if "disabled" in next_button.get_attribute("class"):  # Check if the button is disabled
                break  # Stop pagination if no more pages
            next_button.click()  # Click to load next page
            time.sleep(2)  # Wait for the next page to load
        except (NoSuchElementException, ElementClickInterceptedException):
            break  # Stop pagination if button is missing

    webscraper_driver_cleanup(driver)
    return jobs_list





def load_more_jobs_on_ultipro(driver):
    while True:
        # Wait for the "View More Opportunities" link to be visible
        try:
            load_more_link = driver.find_element(By.ID, "LoadMoreJobs")
            if not load_more_link.is_displayed():
                break
        except:
            break  # Exit if the link is not found or not visible

        # Click the "View More Opportunities" link
        load_more_link.click()
        print("Clicked on \'View More Opportunities\'")

        # Wait for new jobs to load (you can adjust the sleep time or use WebDriverWait)
        time.sleep(1)  # Sleep to wait for the page to load new job posts


def cmn_scraper16(board=None):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)

    jobs_list = []
    company = board.company

    load_more_jobs_on_ultipro(driver)
    # Parse the page
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Extract job postings
    job_posts = soup.find_all("div", {"data-automation": "opportunity"})

    for job in job_posts:
        # Job Title & URL
        title_tag = job.find("a", {"data-automation": "job-title"})
        job_title = title_tag.text.strip() if title_tag else "N/A"
        job_url = urljoin(board.url, title_tag["href"]) if title_tag else "N/A"

        # Extract Job ID from URL
        job_id = job_url.split("opportunityId=")[-1] if "opportunityId=" in job_url else "N/A"

        # Job Location
        location_tag = job.find("span", {"data-automation": "location-description"})
        city_tag = job.find("span", {"data-automation": "name-and-location-id-label"})
        country_tag = job.find("span", {"data-automation": "city-state-zip-country-label"})

        job_location = ", ".join(filter(None, [
            city_tag.text.strip() if city_tag else None,
            location_tag.text.strip() if location_tag else None,
            country_tag.text.strip() if country_tag else None
        ]))
        if is_valid(job_id, job_location, job_title, board):
            jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    webscraper_driver_cleanup(driver)
    return jobs_list

# Paylocity WebCrawler
def cmn_scraper17(board=None):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)

    jobs_list = []
    company = board.company

    # Parse the page
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Extract job postings
    job_posts = soup.find_all("div", class_="row job-listing-job-item")

    for job in job_posts:
        title_tag = job.find("a", class_="no-underline custom-link-color")
        job_title = title_tag.get_text(strip=True)
        job_date = job.find_all("span")[1].get_text(strip=True)  # This is the third <span>, containing the date
        job_location = ", ".join(location.get_text(strip=True) for location in job.find("div", class_="location-column").find_all("span"))

        relative_url = title_tag["href"]
        job_url = urljoin(board.url, relative_url)

        job_id = relative_url.split("/")[-1]

        if is_valid(job_id, job_location, job_title, board):
            jobs_list.append(Job(company, job_id, job_title, job_location, job_url, published_at=job_date))

    webscraper_driver_cleanup(driver)
    return jobs_list

# JazzHR Web-Crawler
def cmn_scraper18(board=None):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)

    jobs_list = []
    company = board.company

    # Parse the page
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Extract job postings
    job_elements = soup.find_all('li', class_='list-group-item')
    for job_elem in job_elements:
        # Extract job name
        title_tag = job_elem.find('a')
        job_title = title_tag.get_text(strip=True) if title_tag else None

        # Extract job URL
        job_url = title_tag['href'] if title_tag and title_tag.has_attr('href') else None

        # Extract job ID from URL (e.g., "IpitwCMaP6" in the example)
        job_id = job_url.split('/')[-2] if job_url else None

        # Extract job location
        location_tag = job_elem.find('ul').find('li')
        job_location = location_tag.get_text(strip=True) if location_tag else None

        if is_valid(job_id, job_location, job_title, board):
            jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    webscraper_driver_cleanup(driver)
    return jobs_list


# Specific Webscraper Functions
def beyondtrust(board=None):
    job_list = cmn_scraper1(board)
    for job in job_list:
        job.url = f"https://www.beyondtrust.com/company/careers/{job.id}"
    return job_list

def cloudflare(board=None):
    resp = requests.get(f"https://boards-api.greenhouse.io/v1/boards/{board.func}/jobs")
    resp.raise_for_status()  # throw error if request failed

    data = resp.json()
    job_posts = data.get("jobs", [])

    def get_posting_location(job):
        # Greenhouse stores the real city/country info inside metadata under the key 'Job Posting Location'.
        v = next((m["value"] for m in job.get("metadata", []) if m.get("name") == "Job Posting Location"), "N/A")
        return "; ".join(v) if isinstance(v, list) else v

    jobs_list = []

    company = board.company
    for job in job_posts:
        job_id = job.get("id")
        job_title = job.get("title")
        job_url = job.get("absolute_url")
        job_location = get_posting_location(job)

        if is_valid(job_id, job_location, job_title, board):
            jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    return jobs_list

def enverus(board=None):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)
    jobs_list = []
    company = board.company

    while True:  # Pagination loop
        time.sleep(2)  # Allow time for elements to load
        job_posts = driver.find_elements(By.XPATH, "//div[div[@class='jv-job-list-name']]")

        for job in job_posts:
            outer_html = job.get_attribute("outerHTML")
            soup = BeautifulSoup(outer_html, "html.parser")

            job_title_elem = soup.find("div", class_="jv-job-list-name").find("a")
            job_location_elem = soup.find("div", class_="jv-job-list-location")

            if job_location_elem and job_title_elem:
                job_id = urlparse(job_title_elem["href"]).path.split("/")[-1]  # Extract job ID
                job_title = job_title_elem.text.strip()  # Extract job title
                job_url = f"https://jobs.jobvite.com{job_title_elem['href']}"  # Construct full job URL
                job_location = "".join(job_location_elem.text.replace("\n", "").split("  "))  # Clean location text

                if is_valid(job_id, job_location, job_title, board):
                    jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

        # Check if "Next" button exists
        try:
            next_button = driver.find_element(By.XPATH, "//a[contains(@class, 'jv-pagination-next')]")
            if "disabled" in next_button.get_attribute("class"):  # Check if the button is disabled
                break  # Stop pagination if no more pages
            next_button.click()  # Click to load next page
            time.sleep(2)  # Wait for the next page to load
        except (NoSuchElementException, ElementClickInterceptedException):
            break  # Stop pagination if button is missing

    webscraper_driver_cleanup(driver)
    return jobs_list


def atlassian(board=None):
    jobs_list = []
    company = board.company

    request_url = "https://www.atlassian.com/endpoint/careers/listings"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/138.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(request_url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    data = response.json()

    for item in data:
        job_id = item.get("id")
        job_title = item.get("title")
        job_location = ", ".join(item.get("locations", []))
        job_url = item.get("portalJobPost", {}).get("portalUrl")

        if is_valid(job_id, job_location, job_title, board):
            jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    return jobs_list

def fidelity(board=None):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)
    time.sleep(1)
    wait = WebDriverWait(driver, 5)

    jobs_list = []
    company = board.company

    while True:
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Find all job listings
        job_posts = soup.find_all("li", class_="css-1q2dra3")

        for job in job_posts:
            # Extract title and url
            title_tag = job.find("a", {"data-automation-id": "jobTitle"})
            job_title = title_tag.text.strip()
            job_url =  urljoin(board.url, title_tag["href"]).split('?', 1)[0]

            # Extract subtitle list items
            subtitles = job.find("ul", {"data-automation-id": "subtitle"}).find_all("li")
            job_location = subtitles[0].text.strip()

            # Job ID is inside the second <li>, before the first space
            job_id = subtitles[1].text.strip().split()[0]  # "J62034"

            # Posting Date appears as "Posting Date: DD/MM/YYYY"
            posting_date = subtitles[2].text.replace("Posting Date:", "").strip()

            if is_valid(job_id, job_location, job_title, board) and job_id not in [job.id for job in jobs_list]:
                jobs_list.append(Job(company, job_id, job_title, job_location, job_url, published_at=posting_date))

        # Try to click the "Next" button if it exists
        try:
            # Locate the Next button using 'data-uxi-element-id'
            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-uxi-element-id='next']")))
            driver.execute_script("arguments[0].scrollIntoView();", next_button)  # Scroll to button
            driver.execute_script("arguments[0].click();", next_button)  # Click using JavaScript
            print("Navigating to next page...")
            time.sleep(1)
        except:
            print("No more pages to navigate.")
            break  # Exit loop if no "Next" button is found

    webscraper_driver_cleanup(driver)
    return jobs_list

def aristocrat(board=None):
        driver = webscraper_driver_init()
        webscraper_driver_get(driver, board.url)
        time.sleep(1)
        wait = WebDriverWait(driver, 5)

        jobs_list = []
        company = board.company

        while True:
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # Find all job listings
            job_posts = soup.find_all("li", class_="css-1q2dra3")

            for job in job_posts:
                job_title_elem = job.find("a", {"data-automation-id": "jobTitle"})
                job_location_elem = job.find("dd", class_="css-129m7dg")  # Location
                job_id_list = job.find_all("li", class_="css-h2nt8k")

                if job_title_elem:
                    job_url = urljoin(board.url, job_title_elem["href"]).split('?', 1)[0]
                    job_title = job_title_elem.text.strip()
                    job_location = "; ". join([x.text.strip() for x in job_id_list[1:-3]])
                    job_id = job_id_list[-2].text.strip() if job_id_list and len(job_id_list) > 1 else "N/A"

                    if is_valid(job_id, job_location, job_title, board) and job_id not in [job.id for job in jobs_list]:
                        jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

            # Try to click the "Next" button if it exists
            try:
                # Locate the Next button using 'data-uxi-element-id'
                next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-uxi-element-id='next']")))
                driver.execute_script("arguments[0].scrollIntoView();", next_button)  # Scroll to button
                driver.execute_script("arguments[0].click();", next_button)  # Click using JavaScript
                print("Navigating to next page...")
                time.sleep(1)
            except:
                print("No more pages to navigate.")
                break  # Exit loop if no "Next" button is found

        webscraper_driver_cleanup(driver)
        return jobs_list

def adp(board=None):
    jobs_list = []

    def is_title_qualified(job_title, title_qualifiers):
        return any(title_qualifier.lower() in job_title.lower() for title_qualifier in title_qualifiers) if title_qualifiers else True

    def is_title_disqualified(job_title, title_disqualifiers):
        return not any(title_disqualifier.lower() in job_title.lower() for title_disqualifier in title_disqualifiers) if title_disqualifiers else True

    def is_valid_description(job_description, job_title_qualifiers):
        job_description_lower = job_description.lower() if job_description else ""
        return any(qualifier.lower() in job_description_lower for qualifier in job_title_qualifiers)

    api_func = extract_adp_func(board.url)
    encoded_filter = encode_filter_expression(board.url)
    my_jobs_token = fetch_jobs_token(api_func)

    job_posts = fetch_adp_jobs(my_jobs_token, encoded_filter)
    for job in job_posts:
        job_id, job_title, job_location, job_url, job_description = fetch_adp_job_details(job, api_func)

        if ((not is_id_visited(str(job_id), board.visited_ids)) and is_valid_location(job_location, board.location_qualifiers) and
                (is_title_qualified(job_title, board.job_title_qualifiers) or is_valid_description(job_description, board.job_title_qualifiers)) and is_title_disqualified(job_title, board.job_title_disqualifiers)):
            jobs_list.append(Job(board.company, job_id, job_title, job_location, job_url))

    return jobs_list
