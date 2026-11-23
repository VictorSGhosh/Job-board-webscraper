import csv
import webbrowser
import time

# Path to your CSV file
csv_file = "job_listings.csv"

# Column index where URLs are stored (0-based index)
url_column_index = 4
frnt_skip = 436
bck_skip = 571
# Define browser paths (Adjust based on your system)
browsers = {
    "midori": "C:/Program Files/Midori Browser/midori.exe",
    "firefox": "C:/Program Files/Mozilla Firefox/firefox.exe",
    "chrome": "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "edge": "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "opera": "C:/Users/HP/AppData/Local/Programs/Opera/opera.exe"
}

# Register browsers
for name, path in browsers.items():
    webbrowser.register(name, None, webbrowser.BackgroundBrowser(path))

chrome_websites = ["workday", "icims"]
edge_websites = ["greenhouse", "jobvite", "oraclecloud", "ultipro"]
opera_websites = ["ashbyhq", ".lever", "workable", "smartrecruiters", "rippling", ".gem.", "bamboohr", "paylocity", "applytojob", ".adp.", "dayforcehcm"]

# Function to determine which browser to use based on URL content
def get_browser(url):
    """Selects browser based on keywords in the URL."""

    # return webbrowser.get("chrome")

    if any(website in url.lower() for website in chrome_websites):
        time.sleep(1)
        return webbrowser.get("chrome")  # Open jobs in Chrome
    elif any(website in url.lower() for website in edge_websites):
        return webbrowser.get("edge")  # Open jobs in Edge
    elif any(website in url.lower() for website in opera_websites):
        return webbrowser.get("opera")  # Open jobs in Opera
    else:
        return webbrowser.get("edge")
        return webbrowser.get("firefox")  # The default browser is Firefox/Midori


# Read CSV and open URLs
with open(csv_file, newline='', encoding='utf-8') as file:
    reader = csv.reader(file)

    for idx, row in enumerate(reader):
        if row and frnt_skip <= idx <= bck_skip:  # Ensure row is not empty
            url = row[url_column_index].strip()  # Get URL from the specified column
            if url.startswith("http"):  # Ensure it's a valid URL
                browser = get_browser(url)
                browser and browser.open(url)  # Open in the selected browser
                time.sleep(1)  # Optional delay to prevent opening too many tabs at once
