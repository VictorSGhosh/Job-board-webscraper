# Job Board Web Scraper

This project is a **web scraper** for job postings from multiple job boards using **Selenium** and **BeautifulSoup**. It extracts job details such as title, location, and URL, then saves them into a CSV file.

## Features
- Scrapes job listings from multiple job boards (e.g., **Monzo, Credit Karma, Block**).
- Uses **Selenium** to navigate and load job listings dynamically.
- Filters job listings based on **location** and **title** qualifiers.
- Saves extracted job data into a **CSV file**.

## Technologies Used
- **Python**
- **Selenium** (for browser automation)
- **BeautifulSoup** (for HTML parsing)
- **CSV** (for storing extracted job data)

## Installation

1. **Clone the repository**
   ```sh
   git clone https://github.com/VictorSGhosh/Job-board-webscraper.git
   cd job-board-scraper
   ```

2. **Create a virtual environment (optional but recommended)**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

## Configuration

This project uses a **JSON configuration file (`config.json`)** to specify job boards, locations, and title filters. Example:

```json
[
  {
    "name": "Monzo",
    "url": "https://monzo.com/careers/",
    "function": "monzo",
    "location_qualifiers": ["Remote", "London"],
    "job_qualifiers": ["Engineer", "Developer"]
  }
]
```

## Usage

1. **Run the scraper**
   ```sh
   python main.py
   ```
2. **Check the output CSV file**
   After completion, job listings will be saved in `job_listings.csv`.

## Adding a New Job Board
To add a new job board:
1. Implement a function in `scraper_functions.py` (following the format of `monzo()` or `credit_karma()`).
2. Add an entry in `config.json` with the job board details.

## Troubleshooting
- Ensure **Google Chrome** is installed for Selenium.
- If issues occur with **ChromeDriver**, update it using:
  ```sh
  pip install --upgrade webdriver-manager
  ```

## License
This project is open source.

## Contributing
Pull requests are welcome! Please follow best coding practices and provide clear commit messages.

## Author
**Victor Sankar Ghosh**

---
**Happy scraping!** 🚀

