import urllib
from collections import defaultdict

from typing import List

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
from urllib.parse import urlparse, parse_qs, ParseResult, urlunparse, urljoin

import time
import json
import inspect
import re

from classes import Job

## WebDriver Functions
# driver = None
visited_data = None
qualifiers = None


# Setup Selenium WebDriver (in headless mode)
def init():
    global visited_data
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

    # global qualifiers
    # # Load visited.json
    # global_filename = "global.json"
    # try:
    #     with open(visited_filename, "r", encoding="utf-8") as f:
    #         qualifiers = json.load(f)
    # except (FileNotFoundError, json.JSONDecodeError):
    #     qualifiers = {}  # Fallback to an empty dictionary
    #
    # # Ensure visited_data is a defaultdict
    # if not isinstance(qualifiers, defaultdict):
    #     qualifiers = defaultdict(list, qualifiers)


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


def is_id_visited(job_id, company):
    return job_id in visited_data[company]


def is_valid(job_id, job_location, job_title, board):
    location_qualifiers = board.location_qualifiers
    job_title_qualifiers = board.job_title_qualifiers
    job_title_disqualifiers = board.job_title_disqualifiers
    company_func = board.func

    loc_q = is_valid_location(job_location, location_qualifiers)
    title_q = is_valid_title(job_title, job_title_qualifiers, job_title_disqualifiers)
    visit_q = is_id_visited(job_id, company_func)
    return loc_q and title_q and not visit_q


### Helper Fns
def get_full_url_and_id(parsed_url: ParseResult) -> (str, str):
    prefix = "https://boards.greenhouse.io" if not parsed_url.scheme and not parsed_url.netloc else ""
    url = (prefix + parsed_url.path) if prefix else f"{urlunparse(parsed_url)}"
    id = id if (id := parsed_url.path.split('/')[-1]).isdigit() else parsed_url.query.split('=')[-1]
    return url, id


def print_jobs(job_list: List[Job]):
    # Print jobs
    for job in job_list:
        print(job)


## Common WebScrapers
def cmn_scraper1(board=None):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)
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

            if is_valid(job_id, job_location, job_title, board):
                jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    caller = inspect.stack()[1]  # Get caller's frame
    caller_module = inspect.getmodule(caller[0])  # Get caller's module
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list


def cmn_scraper1_1(board=None):
    job_list = cmn_scraper1(board)
    for job in job_list:
        job.url = f"https://boards.greenhouse.io/embed/job_app?for={board.func}&token={job.id}"
    print_jobs(job_list)
    return job_list


def cmn_scraper2(board=None):
    driver = webscraper_driver_init()

    page_num = 1
    jobs_list = []
    company = board.company

    sep = "&" if urlparse(board.url).query else "?"
    while True:  # Pagination loop
        page_url = f"{board.url}{sep}page={page_num}"
        webscraper_driver_get(driver, page_url)  # Load the current page
        time.sleep(2)  # Allow time for elements to load

        job_posts = driver.find_elements(By.CLASS_NAME, "job-post")
        if not job_posts:
            break  # Stop if no more job listings are found

        for job in job_posts:
            outer_html = job.get_attribute("outerHTML")
            soup = BeautifulSoup(outer_html, "html.parser")

            job_link = soup.find("a")
            job_title_elem = soup.find("p", class_="body body--medium")

            # Extract the span text if it exists
            new_post_label = job_title_elem.find("span")
            new_label = new_post_label.get_text(strip=True) if new_post_label else ""

            job_location_elem = soup.find("p", class_="body body__secondary body--metadata")

            if job_link and job_title_elem:
                job_url = urljoin(board.url, job_link["href"])  # Convert relative URL to absolute
                parsed_url = urlparse(job_url)
                job_id = id if (id := parsed_url.path.split('/')[-1]).isdigit() else parsed_url.query.split('=')[-1]
                # Remove the span text manually (alternative method)
                for span in job_title_elem.find_all("span"):
                    span.extract()  # Removes all span elements
                job_title = job_title_elem.get_text(strip=True)

                job_location = job_location_elem.get_text(strip=True) if job_location_elem else "Not specified"

                if is_valid(job_id, job_location, job_title, board):
                    jobs_list.append(Job(company, job_id, job_title, job_location, job_url, published_at=new_label))

        page_num += 1  # Move to the next page
    caller = inspect.stack()[1]  # Get caller's frame
    caller_module = inspect.getmodule(caller[0])  # Get caller's module
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list


def cmn_scraper2_1(board=None):
    driver = webscraper_driver_init()

    page_num = 1
    jobs_list = []
    company = board.company

    while True:  # Pagination loop
        sep = "&" if urlparse(board.url).query else "?"
        page_url = f"{board.url}{sep}page={page_num}"
        webscraper_driver_get(driver, page_url)  # Load the current page
        time.sleep(2)  # Allow time for elements to load

        job_posts = driver.find_elements(By.CLASS_NAME, "job-post")
        if not job_posts:
            break  # Stop if no more job listings are found

        for job in job_posts:
            outer_html = job.get_attribute("outerHTML")
            soup = BeautifulSoup(outer_html, "html.parser")

            job_link = soup.find("a")
            job_title_elem = soup.find("p", class_="body body--medium")

            # Extract the span text if it exists
            new_post_label = job_title_elem.find("span")
            new_label = new_post_label.get_text(strip=True) if new_post_label else ""

            job_location_elem = soup.find("p", class_="body body__secondary body--metadata")

            if job_link and job_title_elem:
                job_url = urljoin(board.url, job_link["href"])  # Convert relative URL to absolute
                job_id = job_url.split("=")[-1]
                # job_title = job_title_elem.get_text(" ", strip=True)
                # Remove the span text manually (alternative method)
                for span in job_title_elem.find_all("span"):
                    span.extract()  # Removes all span elements
                job_title = job_title_elem.get_text(strip=True)

                job_location = job_location_elem.get_text(strip=True) if job_location_elem else "Not specified"

                if is_valid(job_id, job_location, job_title, board):
                    jobs_list.append(Job(company, job_id, job_title, job_location, job_url, published_at=new_label))

        page_num += 1  # Move to the next page
    caller = inspect.stack()[1]  # Get caller's frame
    caller_module = inspect.getmodule(caller[0])  # Get caller's module
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list

def cmn_scraper3(board=None):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)

    job_posts = driver.find_elements(By.CLASS_NAME, "_container_j2da7_1")
    jobs_list = []

    company = board.company
    for job in job_posts:
        outer_html = job.get_attribute("outerHTML")
        soup = BeautifulSoup(outer_html, "html.parser")

        job_link = soup.find("a")
        job_title_elem = soup.find("h3", class_="_title_12ylk_383")
        job_location_elem = soup.find("div", class_="_details_12ylk_389")

        if job_link and job_title_elem:
            job_url = urlparse(job_link["href"])
            job_id = job_url.path.split("/")[-1]
            job_url = f"https://jobs.ashbyhq.com{job_url.path}" if not job_url.scheme and not job_url.netloc else urlunparse(job_url)
            job_title = job_title_elem.get_text(strip=True)
            job_location = job_location_elem.get_text(strip=True).split("•")[1] if job_location_elem else "Not specified"

            if is_valid(job_id, job_location, job_title, board):
                jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    caller = inspect.stack()[1]  # Get caller's frame
    caller_module = inspect.getmodule(caller[0])  # Get caller's module
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list


def cmn_scraper4(board=None):
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

    caller = inspect.stack()[1]  # Get caller's frame
    caller_module = inspect.getmodule(caller[0])  # Get caller's module
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list

def cmn_scraper4_1(board=None):
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
                job_id = job_url_elem["href"].split("/")[-1]  # Extract job ID
                job_title = job_title_elem.text.strip()  # Extract job title
                job_url = f"https://jobs.jobvite.com{job_url_elem['href']}"  # Construct full job URL
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

    caller = inspect.stack()[1]  # Get caller's frame
    caller_module = inspect.getmodule(caller[0])  # Get caller's module
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list

def cmn_scraper5(board):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)
    job_posts = driver.find_elements(By.CLASS_NAME, "posting-title")
    jobs_list = []

    company = board.company
    for job in job_posts:
        outer_html = job.get_attribute("outerHTML")
        soup = BeautifulSoup(outer_html, "html.parser")

        job_link_elem = soup.find("a", class_="posting-title")
        job_title_elem = soup.find("h5", {"data-qa": "posting-name"})
        job_location_elem = soup.find("span", class_="sort-by-location")

        if job_link_elem and job_title_elem:
            job_url = job_link_elem["href"]
            job_id = urlparse(job_url).path.split("/")[-1]  # Extract job ID from URL
            job_title = job_title_elem.text.strip()
            job_location = job_location_elem.text.strip() if job_location_elem else "Not specified"

            if is_valid(job_id, job_location, job_title, board):
                jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    caller = inspect.stack()[1]  # Get caller's frame
    caller_module = inspect.getmodule(caller[0])  # Get caller's module
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list


def cmn_scraper6(board):
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
                job_url = urljoin(board.url, job_title_elem["href"])
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

    caller = inspect.stack()[1]  # Get caller's frame
    caller_module = inspect.getmodule(caller[0])  # Get caller's module
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list


def cmn_scraper7(board):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)
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
                job_url = urljoin(board.url, job_title_elem["href"])
                job_title = job_title_elem.text.strip()
                job_id, job_location = [elem.text.strip() for elem in job_id_elem_list] if job_id_elem_list else ["N/A", "N/A"]

                if is_valid(job_id, job_location, job_title, board):
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

    caller = inspect.stack()[1]  # Get caller's frame
    caller_module = inspect.getmodule(caller[0])  # Get caller's module
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list


def cmn_scraper8(board):
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
                job_url = urljoin(board.url, job_title_elem["href"])
                job_title = job_title_elem.text.strip()
                job_location = job_location_elem.text.strip() if job_location_elem else "Not specified"
                job_id = job_id_list[1].text.strip() if job_id_list and len(job_id_list) > 1 else "N/A"

                if is_valid(job_id, job_location, job_title, board):
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

    caller = inspect.stack()[1]  # Get caller's frame
    caller_module = inspect.getmodule(caller[0])  # Get caller's module
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
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


def click_button_to_show_more_jobs(driver):
    wait = WebDriverWait(driver, 5)
    clicks = 20
    while clicks >= 0:
        # Get the page source after it's fully loaded
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Find all "Show more jobs" buttons using BeautifulSoup
        show_more_btns = soup.find_all("a", class_="js-more")

        if not show_more_btns:  # If no buttons are found, break out of the loop
            print("No more jobs to load.")
            break

        # Loop through all found buttons
        for show_more_btn in show_more_btns:
            try:
                # Find the button element using Selenium
                button = driver.find_element(By.CSS_SELECTOR, f"a.js-more[href='{show_more_btn['href']}']")

                # Wait for the button to be clickable
                wait.until(EC.element_to_be_clickable(button))
                driver.execute_script("arguments[0].scrollIntoView();", button)  # Scroll to button
                driver.execute_script("window.scrollBy(0, -300);")  # Scroll a bit further down
                time.sleep(1)  # Wait for the button to be fully in view
                print("Clicking on \"Show More Jobs\" Button...")
                button.click()  # Click the button
                clicks -= 1
                if clicks <= 0:
                    break

            except Exception as e:
                print(f"Error or button not clickable: {e}")
                break  # Exit loop if an error occurs or no buttons are found


def cmn_scraper9(board=None):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)

    jobs_list = []
    company = board.company

    # Keep clicking "Show more jobs" and scrolling until all jobs are loaded
    scroll_to_load_jobs(driver)
    click_button_to_show_more_jobs(driver)

    # Parse the page after all jobs are loaded
    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_posts = soup.find_all("li", class_="opening-job")

    for job in job_posts:
        job_link_elem = job.find("a", class_="link--block details")
        job_title_elem = job_link_elem.find("h4", class_="details-title job-title link--block-target") if job_link_elem else None
        job_location_elem = job.find_previous("h3", class_="opening-title")

        if job_link_elem and job_title_elem:
            job_url = job_link_elem["href"]
            job_title = job_title_elem.text.strip()
            job_location = job_location_elem.text.strip() if job_location_elem else "Not specified"
            job_id = (job_url.split("/")[-1]).split("-")[0]

            if is_valid(job_id, job_location, job_title, board):
                jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    caller = inspect.stack()[1]
    caller_module = inspect.getmodule(caller[0])
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list

def cmn_scraper9_5(board=None):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)

    jobs_list = []
    company = board.company

    # Keep clicking "Show more jobs" and scrolling until all jobs are loaded
    scroll_to_load_jobs(driver)
    click_button_to_show_more_jobs(driver)

    # Parse the page after all jobs are loaded
    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_posts = soup.find_all("li", class_="opening-job")

    for job in job_posts:
        job_link_elem = job.find("a", class_="link--block details")
        job_title_elem = job_link_elem.find("h4", class_="details-title job-title link--block-target") if job_link_elem else None
        job_location_elem = job.find("p", class_="job-desc")

        if job_link_elem and job_title_elem:
            job_url = job_link_elem["href"]
            job_title = job_title_elem.text.strip()
            job_location = job_location_elem.text.strip() if job_location_elem else "Not specified"
            job_id = (job_url.split("/")[-1]).split("-")[0]

            if is_valid(job_id, job_location, job_title, board):
                jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    caller = inspect.stack()[1]
    caller_module = inspect.getmodule(caller[0])
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list


def cmn_scraper10(board=None):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)

    jobs_list = []
    company = board.company

    # Keep clicking "Show more jobs" and scrolling until all jobs are loaded
    scroll_to_load_jobs(driver)

    # Parse the page after all jobs are loaded
    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_posts = soup.find_all("li", class_="opening-job")

    for job in job_posts:
        job_link_elem = job.find("a", class_="link--block details")
        job_title_elem = job_link_elem.find("h4", class_="details-title job-title link--block-target") if job_link_elem else None
        job_location_elem = job.find("li", class_="job-desc")

        if job_link_elem and job_title_elem:
            job_url = job_link_elem["href"]
            job_title = job_title_elem.text.strip()
            job_location = job_location_elem.text.strip() if job_location_elem else "Not specified"
            job_id = (job_url.split("/")[-1]).split("-")[0]

            if is_valid(job_id, job_location, job_title, board):
                jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    caller = inspect.stack()[1]
    caller_module = inspect.getmodule(caller[0])
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list


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
    job_posts = soup.find_all("div", class_="job-tile job-grid-item search-results job-grid-item--all-actions-visible")

    for job_tile in job_posts:
        job_id = job_tile.find("div", class_="job-grid-item__link")["id"] if job_tile.find("div", class_="job-grid-item__link") else None
        job_title = job_tile.find("span", class_="job-tile__title").text.strip() if job_tile.find("span", class_="job-tile__title") else None
        job_url = job_tile.find("a", class_="job-grid-item__link")["href"] if job_tile.find("a", class_="job-grid-item__link") else None
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
            job_url = job.find_element(By.CLASS_NAME, "job-list-item__link").get_attribute("href")  # Extract job URL
            job_id = re.search(r'/job/(\d+)/', job_url).group(1)
            job_location = job.find_element(By.CLASS_NAME, "job-list-item__job-info-value").text  # Extract location

            if is_valid(job_id, job_location, job_title, board):
                jobs_list.append(Job(company, job_id, job_title, job_location, job_url))
        except Exception:
            continue  # Skip if any field is missing
    return jobs_list


def cmn_scraper11(board=None):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)
    time.sleep(2)

    # Keep clicking "Show more jobs" and scrolling until all jobs are loaded
    scroll_to_load_jobs(driver)
    click_show_more(driver)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_posts = soup.find_all("div", class_="job-tile job-grid-item search-results job-grid-item--all-actions-visible")
    jobs_list = grid_style_job_posts(driver, board) if job_posts else list_style_job_posts(driver, board)

    caller = inspect.stack()[1]
    caller_module = inspect.getmodule(caller[0])
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list


def handle_cookie_popup(driver):
    wait = WebDriverWait(driver, 5)
    # Handle cookie popup if present
    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Decline') or contains(text(), 'Disagree')]")))
        cookie_button.click()
        print("Declined cookies.")
        time.sleep(1)  # Wait a bit for changes to apply
    except Exception:
        print("No cookie popup found or already declined.")


def cmn_scraper12(board=None):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)

    jobs_list = []
    company = board.company

    # Keep clicking "Show more jobs" and scrolling until all jobs are loaded
    handle_cookie_popup(driver)
    click_show_more(driver)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Find all job elements
    job_posts = soup.find_all("li", {"role": "listitem"})
    for job in job_posts:
        # Extract job ID from the <a> tag's href attribute
        if not (job_link := job.find("a")):
            continue

        job_href = job_link["href"]
        job_id = job_href.split("/")[-2]  # Extract job ID from URL

        # Extract job title
        job_title_element = job.find("h3", attrs={"data-id": "job-item"}) or job.find("h3", attrs={"data-ui": "job-title"})
        job_title = job_title_element.text.strip() if job_title_element else "N/A"

        # Extract job URL
        job_url = urljoin(board.url, job_href)

        # Extract job location(s)
        location_elements = job.find_all("div", {"data-ui": "job-location-tooltip"})
        locations = [" ".join([span.text.strip() for span in loc.find_all("span", attrs={"class": "styles--2TdGW"})]) for loc in location_elements]
        job_location = "; ".join(locations)

        if is_valid(job_id, job_location, job_title, board):
            jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    caller = inspect.stack()[1]
    caller_module = inspect.getmodule(caller[0])
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list


def cmn_scraper13(board=None):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)
    time.sleep(1)

    jobs_list = []
    company = board.company

    # Parse the page after all jobs are loaded
    soup = BeautifulSoup(driver.page_source, "html.parser")
    # Extract job details
    job_posts = soup.find_all("mat-expansion-panel", class_="search-result-item")

    for job in job_posts:
        # Job Title
        title_tag = job.find("span", itemprop="title")
        job_title = title_tag.text.strip() if title_tag else "N/A"

        # Job ID (Extracted from the URL)
        job_link = job.find("a", class_="job-title-link")
        job_url = urljoin(board.url, job_link["href"]) if job_link else "N/A"
        job_id = job_link["href"].split("/")[-1].split("?")[0] if job_link else "N/A"

        # Job Location
        location_tag = job.find("span", class_="label-value location")
        job_location = location_tag.text.strip() if location_tag else "N/A"
        job_location = job_location.replace("\n", ", ")
        if is_valid(job_id, job_location, job_title, board):
            jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    caller = inspect.stack()[1]
    caller_module = inspect.getmodule(caller[0])
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list


def cmn_scraper14(board=None):
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

            location_element = job.find("span", string=re.compile(r"^(Job Locations|Location)$"))
            job_location = location_element.parent.find_all("span")[-1].text.strip() if location_element else "N/A"

            if location_element is None or job_location in ["Job Locations", "Location"]:
                job_location = ", ".join(
                    [span.find("dd").text.strip() for span in reversed([div for div in job.find_all("div", class_="iCIMS_JobHeaderTag") if div.find("dt").find("span", class_="glyphicons glyphicons-map-marker") if div.find("dt")])])

            if is_valid(job_id, job_location, job_title, board):
                jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

        page_number += 1  # Move to the next page

    # Print jobs if function is not called within the same module
    caller = inspect.stack()[1]
    caller_module = inspect.getmodule(caller[0])
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)

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


def cmn_scraper15(board=None):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)

    jobs_list = []
    company = board.company

    load_more_jobs_on_ultipro(driver)
    # load_all_locations(driver)
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

    caller = inspect.stack()[1]
    caller_module = inspect.getmodule(caller[0])
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list


def cmn_scraper16(board=None):
    driver = webscraper_driver_init()

    jobs_list = []
    company = board.company
    page = 0

    flag = True
    while flag:
        # Smart pagination URL construction
        page_url = f"{board.url}{'&' if '?' in board.url else '?'}page={page}"
        webscraper_driver_get(driver, page_url)
        # Parse the page
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Extract job postings
        job_posts = soup.find_all("div", class_="css-cq05mv")
        if not job_posts:
            flag = False
        for job in job_posts:
            # Extract job title and relative URL
            title_tag = job.find("a", class_="css-zepamx-Anchor")
            if not title_tag:
                continue
            job_title = title_tag.text.strip()
            job_relative_url = title_tag['href']
            job_url = urljoin(board.url, job_relative_url)

            # Extract job ID from URL (UUID format)
            job_id = job_relative_url.rstrip("/").split("/")[-1]

            # Multiple Locations: Find all <span data-icon="LOCATION_OUTLINE"> and next <p>
            locations = []
            for loc_icon in job.find_all("span", {"data-icon": "LOCATION_OUTLINE"}):
                p_tag = loc_icon.find_next("p")
                if p_tag:
                    locations.append(p_tag.text.strip())
            job_location = "; ".join(locations) if locations else "Not specified"

            if is_valid(job_id, job_location, job_title, board):
                jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

        page += 1

    caller = inspect.stack()[1]
    caller_module = inspect.getmodule(caller[0])
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list

# Specific Webscraper Functions
def otterai(board=None):
    job_list = cmn_scraper1(board)
    for job in job_list:
        job.url = job.url.replace("careers", "job-detail")
    print_jobs(job_list)
    return job_list


def moloco(board=None):
    job_list = cmn_scraper1(board)
    for job in job_list:
        job.url = "https://job-boards.greenhouse.io/moloco/jobs/" + job.id
    print_jobs(job_list)
    return job_list

def trmlabs(board=None):
    job_list = cmn_scraper2(board)
    for job in job_list:
        job.url = f"https://job-boards.greenhouse.io/embed/job_app?for={board.func}&token={job.id}"
    print_jobs(job_list)
    return job_list

def coalition(board=None):
    job_list = cmn_scraper2(board)
    for job in job_list:
        job.url = job.url.replace("gh_j", "")
    print_jobs(job_list)
    return job_list

def vectra(board=None):
    driver = webscraper_driver_init()

    jobs_list = []
    company = board.company

    page_num = 1
    while True:  # Pagination loop
        sep = "&" if urlparse(board.url).query else "?"
        page_url = f"{board.url}{sep}page={page_num}"
        page_num += 1
        webscraper_driver_get(driver, page_url)  # Load the current page
        time.sleep(2)  # Allow time for elements to load

        job_posts = driver.find_elements(By.CLASS_NAME, "job-post")
        if not job_posts:
            break  # Stop if no more job listings are found

        for job in job_posts:
            outer_html = job.get_attribute("outerHTML")
            soup = BeautifulSoup(outer_html, "html.parser")

            job_link = soup.find("a")
            job_title_elem = soup.find("p", class_="body body--medium")

            # Extract the span text if it exists
            new_post_label = job_title_elem.find("span")
            new_label = new_post_label.get_text(strip=True) if new_post_label else ""

            job_location_elem = soup.find("p", class_="body body__secondary body--metadata")

            if job_link and job_title_elem:
                job_url = urljoin(board.url, job_link["href"])  # Convert relative URL to absolute
                job_id = urlparse(job_url).query.split("=")[-1]
                # Remove the span text manually (alternative method)
                for span in job_title_elem.find_all("span"):
                    span.extract()  # Removes all span elements
                job_title = job_title_elem.get_text(strip=True)

                job_location = job_location_elem.get_text(strip=True) if job_location_elem else "Not specified"

                if is_valid(job_id, job_location, job_title, board):
                    jobs_list.append(Job(company, job_id, job_title, job_location, job_url, published_at=new_label))

    caller = inspect.stack()[1]  # Get caller's frame
    caller_module = inspect.getmodule(caller[0])  # Get caller's module
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list


def nationwide(board):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)
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
                job_url = urljoin(board.url, job_title_elem["href"])
                job_title = job_title_elem.text.strip()
                _, job_id, job_location = [elem.text.strip() for elem in job_id_elem_list] if job_id_elem_list else ["", "N/A", "N/A"]

                if is_valid(job_id, job_location, job_title, board):
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

    caller = inspect.stack()[1]  # Get caller's frame
    caller_module = inspect.getmodule(caller[0])  # Get caller's module
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list


def gm(board=None):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)
    wait = WebDriverWait(driver, 10)

    jobs_list = []
    company = board.company
    pages = 5

    while pages > 0:
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Find all job listings
        job_posts = soup.find_all("li", class_="css-1q2dra3")

        for job in job_posts:
            job_title_elem = job.find("a", {"data-automation-id": "jobTitle"})
            job_location_elem = job.find_all("dd", class_="css-129m7dg")  # Location
            job_id_list = job.find_all("li", class_="css-h2nt8k")

            if job_title_elem:
                job_url = urljoin(board.url, job_title_elem["href"])
                job_title = job_title_elem.text.strip()
                job_id = job_id_list[1].text.strip() if job_id_list and len(job_id_list) > 1 else "N/A"
                job_location = job_location_elem[1].text.strip() if job_location_elem and len(job_location_elem) > 1 else "Not specified"

                if is_valid(job_id, job_location, job_title, board):
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
        pages -= 1

    caller = inspect.stack()[1]  # Get caller's frame
    caller_module = inspect.getmodule(caller[0])  # Get caller's module
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list


def arista(board=None):
    driver = webscraper_driver_init()
    webscraper_driver_get(driver, board.url)

    jobs_list = []
    company = board.company

    # Keep clicking "Show more jobs" and scrolling until all jobs are loaded
    scroll_to_load_jobs(driver)

    # Parse the page after all jobs are loaded
    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_posts = soup.find_all("li", class_="opening-job")

    for job in job_posts:
        job_link_elem = job.find("a", class_="link--block details")
        job_title_elem = job_link_elem.find("h4", class_="details-title job-title link--block-target") if job_link_elem else None
        job_location_elem_list = job.find_all("li", class_="job-desc")

        if job_link_elem and job_title_elem:
            job_url = job_link_elem["href"]
            job_title = job_title_elem.text.strip()
            job_location = job_location_elem_list[1].text.strip() if job_location_elem_list and len(job_location_elem_list) > 1 else "Not specified"
            job_id = (job_url.split("/")[-1]).split("-")[0]

            if is_valid(job_id, job_location, job_title, board):
                jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    caller = inspect.stack()[1]
    caller_module = inspect.getmodule(caller[0])
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
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

    caller = inspect.stack()[1]  # Get caller's frame
    caller_module = inspect.getmodule(caller[0])  # Get caller's module
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list


def magnite(board=None):
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
                job_url = urljoin(board.url, job_title_elem["href"])
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
                    if job_id != "N/A" and not is_id_visited(job_id, board.func):
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

    caller = inspect.stack()[1]  # Get caller's frame
    caller_module = inspect.getmodule(caller[0])  # Get caller's module
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
    return jobs_list