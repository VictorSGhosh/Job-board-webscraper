from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

import time
import json

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
    return any(location_qualifier.lower() in location.lower() for location_qualifier in location_qualifiers)

def is_valid_title(job_title, title_qualifiers, title_disqualifiers):
    return ((any(title_qualifier.lower() in job_title.lower() for title_qualifier in title_qualifiers) if title_qualifiers else True) and
            (not any(title_disqualifier.lower() in job_title.lower() for title_disqualifier in title_disqualifiers) if title_disqualifiers else True))

def is_valid(job_location, job_title, board):
    location_qualifiers = board.location_qualifiers
    job_title_qualifiers = board.job_title_qualifiers
    job_title_disqualifiers = board.job_title_disqualifiers
    return is_valid_location(job_location, location_qualifiers) and is_valid_title(job_title, job_title_qualifiers, job_title_disqualifiers)

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


def credit_karma(board=None):
    job_posts = driver.find_elements(By.CLASS_NAME, "opening")
    jobs_list = []

    company = board.company
    for job in job_posts:
        outer_html = job.get_attribute("outerHTML")
        soup = BeautifulSoup(outer_html, "html.parser")

        job_link = soup.find("a")
        job_location = soup.find("span", class_="location")

        if job_link:
            job_id = job_link["href"].split("/")[-1]  # Extracting job ID from URL
            job_title = job_link.text.strip()
            job_url = f"https://boards.greenhouse.io{job_link['href']}"  # Creating full URL
            job_location = job_location.text.strip() if job_location else "Not specified"

            if is_valid(job_location, job_title, board):
                jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    # Step 5: Print job data
    for job in jobs_list:
        print(job)
    return jobs_list

def block(board=None):
    job_posts = driver.find_elements(By.CLASS_NAME, "opening")
    jobs_list = []

    company = board.company
    for job in job_posts:
        outer_html = job.get_attribute("outerHTML")
        soup = BeautifulSoup(outer_html, "html.parser")

        job_link = soup.find("a")
        job_location = soup.find("span", class_="location")

        if job_link:
            job_url = job_link["href"]
            parsed_url = urlparse(job_url)
            job_id = parse_qs(parsed_url.query).get("gh_jid", ["Unknown"])[0]  # Extract job_id correctly
            job_title = job_link.text.strip()
            job_url = f"{job_link['href']}"  # Creating full URL
            job_location = job_location.text.strip() if job_location else "Not specified"

            if is_valid(job_location, job_title, board):
                jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    # Step 5: Print job data
    for job in jobs_list:
        print(job)
    return jobs_list

def coinbase(board=None):
    job_posts = driver.find_elements(By.CLASS_NAME, "opening")
    jobs_list = []

    company = board.company
    for job in job_posts:
        outer_html = job.get_attribute("outerHTML")
        soup = BeautifulSoup(outer_html, "html.parser")

        job_link = soup.find("a")
        job_location = soup.find("span", class_="location")

        if job_link:
            job_url = job_link["href"]
            parsed_url = urlparse(job_url)
            job_id = parse_qs(parsed_url.query).get("gh_jid", ["Unknown"])[0]  # Extract job_id correctly
            job_title = job_link.text.strip()
            job_url = f"{job_link['href']}"  # Creating full URL
            job_location = job_location.text.strip() if job_location else "Not specified"

            if is_valid(job_location, job_title, board):
                jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    # Step 5: Print job data
    for job in jobs_list:
        print(job)
    return jobs_list
