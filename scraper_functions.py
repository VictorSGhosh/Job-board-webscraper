from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, ParseResult, urlunparse

import time
import json
import re

from classes import Job

## WebDriver Functions
driver = None
# Setup Selenium WebDriver (in headless mode)
def webscraper_driver_init():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode

    global driver  # Setup WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


# Prepare URL
def webscraper_driver_get(url):
    driver.get(url)
    time.sleep(1)


# Driver Clean up
def webscraper_driver_cleanup():
    global driver
    driver.quit()

## Qualifier Functions
def is_valid_location(location, location_qualifiers):
    return any(location_qualifier.lower() in location.lower() for location_qualifier in location_qualifiers) if location_qualifiers else True

def is_valid_title(job_title, title_qualifiers, title_disqualifiers):
    return ((any(title_qualifier.lower() in job_title.lower() for title_qualifier in title_qualifiers) if title_qualifiers else True) and
            (not any(title_disqualifier.lower() in job_title.lower() for title_disqualifier in title_disqualifiers) if title_disqualifiers else True))

def is_valid(job_location, job_title, board):
    location_qualifiers = board.location_qualifiers
    job_title_qualifiers = board.job_title_qualifiers
    job_title_disqualifiers = board.job_title_disqualifiers
    return is_valid_location(job_location, location_qualifiers) and is_valid_title(job_title, job_title_qualifiers, job_title_disqualifiers)

### Helper Fns
def get_full_url_and_id(parsed_url: ParseResult)-> (str, str):
    if not parsed_url.scheme and not parsed_url.netloc:
        url = f"https://boards.greenhouse.io{parsed_url.path}"
    else:
        url = f"{urlunparse(parsed_url)}"
    id = id if (id:=parsed_url.path.split('/')[-1]).isdigit() else parsed_url.query.split('=')[-1]
    return url, id

## Specific WebScrapers
def monzo(board):
    # Step 4: Execute JavaScript to access window.__remixContext
    remix_context = driver.execute_script("return window.__remixContext;")

    company = board.company
    job_list = []
    if remix_context:
        job_openings = remix_context['state']['loaderData']["routes/$url_token"]['jobPosts']['data']

        for job in job_openings:
            job_obj = Job(
                company=company,    job_id=job['id'],        title=job['title'],
                location=job['location'], url=job['absolute_url'],
                content=job.get('content', "No description available"),
                published_at=job.get('published_at', "Not specified")
            )
            job_list.append(job_obj)

    else:
        print("window.__remixContext not found in monzo")

    # Print jobs
    for job in job_list:
        print(job)
    return job_list

def cmn_scraper1(board):
    job_posts = driver.find_elements(By.CLASS_NAME, "opening")
    jobs_list = []

    company = board.company
    for job in job_posts:
        outer_html = job.get_attribute("outerHTML")
        soup = BeautifulSoup(outer_html, "html.parser")

        job_link = soup.find("a")
        job_location = soup.find("span", class_="location")

        if job_link:
            parsed_url = urlparse(job_link["href"])
            job_url, job_id = get_full_url_and_id(parsed_url)  # Creating full URL
            job_title = job_link.text.strip()
            job_location = job_location.text.strip() if job_location else "Not specified"

            if is_valid(job_location, job_title, board):
                jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    for job in jobs_list:
        print(job)
    return jobs_list

def cmn_scraper2(board=None):
    job_posts = driver.find_elements(By.CLASS_NAME, "job-post")
    jobs_list = []

    company = board.company
    for job in job_posts:
        outer_html = job.get_attribute("outerHTML")
        soup = BeautifulSoup(outer_html, "html.parser")

        job_link = soup.find("a")
        job_title_elem = soup.find("p", class_="body body--medium")
        job_location_elem = soup.find("p", class_="body body__secondary body--metadata")

        if job_link and job_title_elem:
            job_url = job_link["href"]
            parsed_url = urlparse(job_url)
            job_id = parsed_url.path.split("/")[-1]
            job_title = job_title_elem.get_text(strip=True)
            job_location = job_location_elem.get_text(strip=True) if job_location_elem else "Not specified"

            if is_valid(job_location, job_title, board):
                jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    for job in jobs_list:
        print(job)
    return jobs_list
