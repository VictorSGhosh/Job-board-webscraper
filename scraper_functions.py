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
qualifiers = None

def function_init():
    # Setup function_map here
    # Dictionary to map function names to actual functions
    function_map = {
        "otterai": otterai,             "moloco": moloco,           "nationwide": nationwide,       "gm": gm,                       "arista": arista,          "vectra": vectra,
        "enverus": enverus,             "magnite": magnite,         "trmlabs": trmlabs,             "coalition": coalition,

        # Greenhouse Embed Career Pages
        "credit_karma": cmn_scraper1,   "block": cmn_scraper1,      "coinbase": cmn_scraper1,       "robinhood": cmn_scraper1,      "stripe": cmn_scraper1,     "ripple": cmn_scraper1,
        "sofi": cmn_scraper1,           "drw": cmn_scraper1,        "nerdwallet": cmn_scraper1,     "akuna_capital": cmn_scraper1,  "vatic_labs": cmn_scraper1, "hudson_river_trading": cmn_scraper1,
        "pdt": cmn_scraper1,            "aqr": cmn_scraper1,        "enfusion": cmn_scraper1,       "zscaler": cmn_scraper1,        "rubrik": cmn_scraper1,     "recorded_future": cmn_scraper1,
        "paxos": cmn_scraper1,          "digicert": cmn_scraper1,   "wayfair": cmn_scraper1,        "faire": cmn_scraper1,          "doordash": cmn_scraper1,   "pendo": cmn_scraper1,
        "pinterest": cmn_scraper1,      "roku": cmn_scraper1,       "airbnb": cmn_scraper1,         "lyft": cmn_scraper1,           "coupang": cmn_scraper1,    "worldquant": cmn_scraper1,
        "lendingtree": cmn_scraper1,    "figma": cmn_scraper1,      "squarespace": cmn_scraper1,    "nextdoor": cmn_scraper1,       "duolingo": cmn_scraper1,   "handshake": cmn_scraper1,
        "digitalocean": cmn_scraper1,   "mongodb": cmn_scraper1,    "purestorage": cmn_scraper1,    "hubspot": cmn_scraper1,        "elastic": cmn_scraper1,    "moveworks": cmn_scraper1,
        "voltron": cmn_scraper1,        "c3ai": cmn_scraper1,       "hashicorp": cmn_scraper1,      "dfinity": cmn_scraper1,        "latentai": cmn_scraper1,   "salesloft": cmn_scraper1,
        "databricks": cmn_scraper1,     "asana": cmn_scraper1,      "datadog": cmn_scraper1,        "redis": cmn_scraper1,          "cohesity": cmn_scraper1,   "dropbox": cmn_scraper1,
        "sentry": cmn_scraper1,         "braze": cmn_scraper1,      "collibra": cmn_scraper1,       "optiver": cmn_scraper1,        "rapp": cmn_scraper1,       "applovin": cmn_scraper1,
        "cedar": cmn_scraper1,          "peloton": cmn_scraper1,    "kalderos": cmn_scraper1,       "picnichealth": cmn_scraper1,   "aurora": cmn_scraper1,     "myfitnesspal": cmn_scraper1,
        "rightway": cmn_scraper1,       "doximity": cmn_scraper1,   "thumbtack": cmn_scraper1,      "videoamp": cmn_scraper1,       "buildops": cmn_scraper1,   "applied_intuition": cmn_scraper1,
        "waymo": cmn_scraper1,          "recroom": cmn_scraper1,    "unity": cmn_scraper1,          "roblox": cmn_scraper1,         "riot_games": cmn_scraper1, "mastercontrol": cmn_scraper1,
        "equal_experts": cmn_scraper1,  "energyhub": cmn_scraper1,  "axon": cmn_scraper1,           "neuralink": cmn_scraper1,      "nuro": cmn_scraper1,       "samsung_research": cmn_scraper1,
        "cloudflare": cmn_scraper1,     "bitgo": cmn_scraper1,      "okta": cmn_scraper1,           "anthropic": cmn_scraper1,      "brex": cmn_scraper1,       "upstart": cmn_scraper1,
        "ixl": cmn_scraper1,            "zuora": cmn_scraper1,      "tempus": cmn_scraper1,         "inovalon": cmn_scraper1,       "godaddy": cmn_scraper1,    "magicleap": cmn_scraper1,
        "tower_research": cmn_scraper1, "flagship": cmn_scraper1,   "definitive": cmn_scraper1,     "coinbase2": cmn_scraper1,      "nasuni": cmn_scraper1,     "beyondtrust": cmn_scraper1,
        "next": cmn_scraper1,           "foursquare": cmn_scraper1, "altruist": cmn_scraper1,       "current": cmn_scraper1,        "wing": cmn_scraper1,       "flexport": cmn_scraper1,
        "zeta_global": cmn_scraper1,    "seatgeek": cmn_scraper1,   "chewy": cmn_scraper1,          "taskrabbit": cmn_scraper1,     "6sense": cmn_scraper1,     "sentinelone": cmn_scraper1,
        "navan": cmn_scraper1,          "blend": cmn_scraper1,      "nexxen": cmn_scraper1,         "berkadia": cmn_scraper1,       "flock": cmn_scraper1,      "cerebras": cmn_scraper1,
        "impact.com": cmn_scraper1,     "glean": cmn_scraper1,      "updater": cmn_scraper1,        "orion": cmn_scraper1,          "skydio": cmn_scraper1,     "hunter_douglas": cmn_scraper1,
        "equipmentshare": cmn_scraper1, "exiger": cmn_scraper1,     "skillz": cmn_scraper1,         "modmed": cmn_scraper1,         "toast": cmn_scraper1,      "honor": cmn_scraper1,
        "plume": cmn_scraper1,          "ionq": cmn_scraper1,       "impact": cmn_scraper1,         "material_bank": cmn_scraper1,  "guild": cmn_scraper1,      "aura_frames": cmn_scraper1,
        "aura": cmn_scraper1,           "dremio": cmn_scraper1,     "inizio_evoke": cmn_scraper1,   "cockroach": cmn_scraper1,      "revolution": cmn_scraper1, "circleci": cmn_scraper1,
        "sonic": cmn_scraper1,          "gemini": cmn_scraper1,     "relavity_space": cmn_scraper1, "esri": cmn_scraper1,           "capvision": cmn_scraper1,  "conviva": cmn_scraper1,
        "foxglove": cmn_scraper1,       "abnormal": cmn_scraper1,   "coveo": cmn_scraper1,          "realtor.com": cmn_scraper1,

        "billtrust": cmn_scraper1_1,    "fanduel": cmn_scraper1_1,

        # Greenhouse Career Pages
        "point72": cmn_scraper2,        "spotter": cmn_scraper2,    "human_interest": cmn_scraper2, "carta": cmn_scraper2,          "propel": cmn_scraper2,     "arcesium": cmn_scraper2,
        "bolt": cmn_scraper2,           "aquatic": cmn_scraper2,    "engineers_gate": cmn_scraper2, "sentilink": cmn_scraper2,      "semgrep": cmn_scraper2,    "okx": cmn_scraper2,
        "nightfall": cmn_scraper2,      "ping": cmn_scraper2,       "twitch": cmn_scraper2,         "sumo_logic": cmn_scraper2,     "qualia": cmn_scraper2,     "ziprecruiter": cmn_scraper2,
        "box": cmn_scraper2,            "yext": cmn_scraper2,       "upwork": cmn_scraper2,         "discord": cmn_scraper2,        "airtable": cmn_scraper2,   "render": cmn_scraper2,
        "coreweave": cmn_scraper2,      "twilio": cmn_scraper2,     "notion": cmn_scraper2,         "perplexity": cmn_scraper2,     "temporal": cmn_scraper2,   "twist_bioscience": cmn_scraper2,
        "smartsheet": cmn_scraper2,     "stackline": cmn_scraper2,  "admarketplace": cmn_scraper2,  "pmg": cmn_scraper2,            "edo": cmn_scraper2,        "doubleverify": cmn_scraper2,
        "trade_desk": cmn_scraper2,     "heartflow": cmn_scraper2,  "omada_health": cmn_scraper2,   "launchdarkly": cmn_scraper2,   "headway": cmn_scraper2,    "schrodinger": cmn_scraper2,
        "strava": cmn_scraper2,         "heygen": cmn_scraper2,     "latitude": cmn_scraper2,       "sony_music": cmn_scraper2,     "npr": cmn_scraper2,        "rockstar_games": cmn_scraper2,
        "zynga": cmn_scraper2,          "otter": cmn_scraper2,      "varda_space": cmn_scraper2,    "city_storage": cmn_scraper2,   "dialpad": cmn_scraper2,    "samsung_semiconductor": cmn_scraper2,
        "tripadvisor": cmn_scraper2,    "monzo": cmn_scraper2,      "postman": cmn_scraper2,        "oportun": cmn_scraper2,        "adyen": cmn_scraper2,      "stubhub": cmn_scraper2,
        "reddit": cmn_scraper2,         "affirm": cmn_scraper2,     "scaleai": cmn_scraper2,        "lucid_motors": cmn_scraper2,   "ipg": cmn_scraper2,        "playstation": cmn_scraper2,
        "cloudkitchen": cmn_scraper2,   "niantic": cmn_scraper2,    "natera": cmn_scraper2,         "bridgewater": cmn_scraper2,    "airbyte": cmn_scraper2,    "appian": cmn_scraper2,
        "flex": cmn_scraper2,           "bilt": cmn_scraper2,       "vercel": cmn_scraper2,         "interactive": cmn_scraper2,    "labelbox": cmn_scraper2,   "farmers_dog": cmn_scraper2,
        "maven": cmn_scraper2,          "canonical": cmn_scraper2,  "noyo": cmn_scraper2,           "ethos": cmn_scraper2,          "pitchbook": cmn_scraper2,  "prove": cmn_scraper2,
        "connectwise": cmn_scraper2,    "podium": cmn_scraper2,     "accuweather": cmn_scraper2,    "signify_health": cmn_scraper2, "guideline": cmn_scraper2,  "id.me": cmn_scraper2,
        "grammarly": cmn_scraper2,      "bill": cmn_scraper2,       "thousandeyes": cmn_scraper2,   "eliseai": cmn_scraper2,        "amount": cmn_scraper2,     "lightspeed": cmn_scraper2,
        "eventbrite": cmn_scraper2,     "verkada": cmn_scraper2,    "vivid_seats": cmn_scraper2,    "mozilla": cmn_scraper2,        "luminar": cmn_scraper2,    "avidxchange": cmn_scraper2,
        "asm": cmn_scraper2,            "gusto": cmn_scraper2,      "truveta": cmn_scraper2,        "fetch": cmn_scraper2,          "angi": cmn_scraper2,       "chatham_financial": cmn_scraper2,
        "dbt": cmn_scraper2,            "groupon": cmn_scraper2,    "oppfi": cmn_scraper2,          "whatnot": cmn_scraper2,        "via": cmn_scraper2,        "headspace": cmn_scraper2,
        "2k": cmn_scraper2,             "pubmatic": cmn_scraper2,   "instabase": cmn_scraper2,      "simplisafe": cmn_scraper2,     "recharge": cmn_scraper2,   "addepar": cmn_scraper2,
        "vimeo": cmn_scraper2,          "galileo": cmn_scraper2,    "alten": cmn_scraper2,          "offerup": cmn_scraper2,        "motive": cmn_scraper2,     "warby_parker": cmn_scraper2,
        "tenable": cmn_scraper2,        "prime_ai": cmn_scraper2,   "flow_traders": cmn_scraper2,   "counterpart": cmn_scraper2,    "trumid": cmn_scraper2,     "uber_freight": cmn_scraper2,
        "boomi": cmn_scraper2,          "everquote": cmn_scraper2,  "zoro": cmn_scraper2,           "west_monroe": cmn_scraper2,    "cargurus": cmn_scraper2,   "alphasense": cmn_scraper2,
        "bandwidth": cmn_scraper2,      "bamboohr": cmn_scraper2,   "kkr": cmn_scraper2,            "capco": cmn_scraper2,          "hitachi": cmn_scraper2,    "amplitude": cmn_scraper2,
        "benchling": cmn_scraper2,      "moneylion": cmn_scraper2,  "weather": cmn_scraper2,        "globality": cmn_scraper2,      "seekwell": cmn_scraper2,   "blink": cmn_scraper2,
        "tanium": cmn_scraper2,         "unite_us": cmn_scraper2,   "acrisure": cmn_scraper2,       "harrys": cmn_scraper2,         "workhelix": cmn_scraper2,  "nymbus": cmn_scraper2,
        "devrev": cmn_scraper2,         "checkr": cmn_scraper2,     "intercom": cmn_scraper2,       "dataiku": cmn_scraper2,        "lattice": cmn_scraper2,    "sigma_computing": cmn_scraper2,
        "onetrust": cmn_scraper2,       "xai": cmn_scraper2,        "komodo": cmn_scraper2,         "axle": cmn_scraper2,           "newsbreak": cmn_scraper2,  "taketwo": cmn_scraper2,
        "tebra": cmn_scraper2,          "five9": cmn_scraper2,      "virtu": cmn_scraper2,          "personalis": cmn_scraper2,     "shift4": cmn_scraper2,     "officehours": cmn_scraper2,
        "enigma": cmn_scraper2,         "plotly": cmn_scraper2,     "nih-ncbi": cmn_scraper2,       "cribl": cmn_scraper2,          "onx": cmn_scraper2,        "branch": cmn_scraper2,
        "ascertain": cmn_scraper2,      "peregrine": cmn_scraper2,  "delfina": cmn_scraper2,        "cohere": cmn_scraper2,

        # Ashby HQ Career Pages
        "snowflake": cmn_scraper3,      "quora": cmn_scraper3,      "mapbox": cmn_scraper3,         "openai": cmn_scraper3,         "n8n": cmn_scraper3,        "harvey": cmn_scraper3,
        "academia": cmn_scraper3,       "nash": cmn_scraper3,       "phil": cmn_scraper3,           "commure": cmn_scraper3,        "vouch": cmn_scraper3,      "acorns": cmn_scraper3,
        "dave": cmn_scraper3,           "crusoe": cmn_scraper3,     "sift": cmn_scraper3,           "lambda": cmn_scraper3,         "suzy": cmn_scraper3,       "par": cmn_scraper3,
        "zip": cmn_scraper3,            "kin": cmn_scraper3,        "writer": cmn_scraper3,         "virta": cmn_scraper3,          "uipath": cmn_scraper3,     "permitflow": cmn_scraper3,
        "distyl": cmn_scraper3,         "arcade": cmn_scraper3,     "comity": cmn_scraper3,         "livekit": cmn_scraper3,        "squint.ai": cmn_scraper3,  "stainless": cmn_scraper3,
        "airwallex": cmn_scraper3,      "lightdash": cmn_scraper3,  "railway": cmn_scraper3,        "chroma": cmn_scraper3,         "count": cmn_scraper3,      "pear": cmn_scraper3,
        "zefr": cmn_scraper3,           "spara": cmn_scraper3,      "sobek-ai": cmn_scraper3,       "vanta": cmn_scraper3,

        # Jobvite Career Pages
        "confluent": cmn_scraper4,      "splunk": cmn_scraper4,     "barracuda": cmn_scraper4,      "qlik": cmn_scraper4,           "nutanix": cmn_scraper4,    "asus": cmn_scraper4,
        "gei": cmn_scraper4,            "funko": cmn_scraper4,      "amerisave": cmn_scraper4,      "edelman": cmn_scraper4,        "cupertino": cmn_scraper4,  "webmd": cmn_scraper4,
        "ziff_davis": cmn_scraper4,     "tylertech": cmn_scraper4,

        "payscale": cmn_scraper4_1,     "total_wine": cmn_scraper4_1,

        # Job Lever Career Pages
        "plaid": cmn_scraper5,          "wolverine": cmn_scraper5,  "point": cmn_scraper5,          "lendbuzz": cmn_scraper5,       "protective": cmn_scraper5, "prosper": cmn_scraper5,
        "wealthfront": cmn_scraper5,    "spotify": cmn_scraper5,    "quizlet": cmn_scraper5,        "houzz": cmn_scraper5,          "pipedrive": cmn_scraper5,  "dun&bradstreet": cmn_scraper5,
        "outreach": cmn_scraper5,       "opengov": cmn_scraper5,    "palantir": cmn_scraper5,       "sysdig": cmn_scraper5,         "lamini": cmn_scraper5,     "digital_turbine": cmn_scraper5,
        "savinynt": cmn_scraper5,       "bounteous": cmn_scraper5,  "veeva": cmn_scraper5,          "sonar": cmn_scraper5,          "aledade": cmn_scraper5,    "included_health": cmn_scraper5,
        "mercedes": cmn_scraper5,       "zoox": cmn_scraper5,       "egen": cmn_scraper5,           "kodiak": cmn_scraper5,         "match": cmn_scraper5,      "bitwise": cmn_scraper5,
        "regrello": cmn_scraper5,       "penumbra": cmn_scraper5,   "coupa": cmn_scraper5,          "clear_capital": cmn_scraper5,  "cellares": cmn_scraper5,   "meridianlink": cmn_scraper5,
        "plusai": cmn_scraper5,         "lightcast": cmn_scraper5,  "kandji": cmn_scraper5,         "activecampaign": cmn_scraper5, "greenlight": cmn_scraper5, "spreetail": cmn_scraper5,
        "attentive": cmn_scraper5,      "viant": cmn_scraper5,      "pointclickcare": cmn_scraper5, "thrive": cmn_scraper5,         "lyra": cmn_scraper5,       "ci&t": cmn_scraper5,
        "varo": cmn_scraper5,           "granicus": cmn_scraper5,   "dronedeploy": cmn_scraper5,    "brillio": cmn_scraper5,        "gopuff": cmn_scraper5,     "system1": cmn_scraper5,
        "scribd": cmn_scraper5,         "nium": cmn_scraper5,       "whoop": cmn_scraper5,          "porter": cmn_scraper5,         "cyngn": cmn_scraper5,      "aircall": cmn_scraper5,
        "xero": cmn_scraper5,           "clari": cmn_scraper5,      "shippo": cmn_scraper5,         "watchguard": cmn_scraper5,     "kyruus": cmn_scraper5,     "woven-by-toyota": cmn_scraper5,
        "basis": cmn_scraper5,          "better": cmn_scraper5,     "insightm": cmn_scraper5,       "adora": cmn_scraper5,

        # Workday Career Pages
        "bank_of_america": cmn_scraper6,"citi": cmn_scraper6,       "wells_fargo": cmn_scraper6,    "us_bank": cmn_scraper6,        "truist": cmn_scraper6,     "pnc": cmn_scraper6,
        "discover": cmn_scraper6,       "m&t": cmn_scraper6,        "state_street": cmn_scraper6,   "53rd": cmn_scraper6,           "barclays": cmn_scraper6,   "nt": cmn_scraper6,
        "huntington": cmn_scraper6,     "regions": cmn_scraper6,    "td": cmn_scraper6,             "mufg": cmn_scraper6,           "deutsche": cmn_scraper6,   "federal_reserve": cmn_scraper6,
        "rbc": cmn_scraper6,            "mastercard": cmn_scraper6, "paypal": cmn_scraper6,         "equifax": cmn_scraper6,        "avant": cmn_scraper6,      "transunion": cmn_scraper6,
        "fiserve": cmn_scraper6,        "remitly": cmn_scraper6,    "fractal": cmn_scraper6,        "q2": cmn_scraper6,             "verily": cmn_scraper6,     "s&p": cmn_scraper6,
        "rocket": cmn_scraper6,         "blackrock": cmn_scraper6,  "arrowstreet": cmn_scraper6,    "vanguard": cmn_scraper6,       "lpl": cmn_scraper6,        "blackstone": cmn_scraper6,
        "target": cmn_scraper6,         "bjs": cmn_scraper6,        "home_depot": cmn_scraper6,     "dicks": cmn_scraper6,          "meijer": cmn_scraper6,     "qurate": cmn_scraper6,
        "puma": cmn_scraper6,           "nordstrom": cmn_scraper6,  "kohls": cmn_scraper6,          "walmart": cmn_scraper6,        "expedia": cmn_scraper6,    "ebay": cmn_scraper6,
        "twitter": cmn_scraper6,        "cloudera": cmn_scraper6,   "yahoo": cmn_scraper6,          "grubhub": cmn_scraper6,        "snapchat": cmn_scraper6,   "zillow": cmn_scraper6,
        "pluralsight": cmn_scraper6,    "chegg": cmn_scraper6,      "hp": cmn_scraper6,             "hp_enterprise": cmn_scraper6,  "nvidia": cmn_scraper6,     "dell": cmn_scraper6,
        "asml": cmn_scraper6,           "intel": cmn_scraper6,      "allstate": cmn_scraper6,       "guidewire": cmn_scraper6,      "massmutual": cmn_scraper6, "usaa": cmn_scraper6,
        "guardian": cmn_scraper6,       "unum": cmn_scraper6,       "fidelity": cmn_scraper6,       "prudential": cmn_scraper6,     "onemain": cmn_scraper6,    "northwestern_mutual": cmn_scraper6,
        "frost": cmn_scraper6,          "starr": cmn_scraper6,      "radian": cmn_scraper6,         "salesforce": cmn_scraper6,     "adobe": cmn_scraper6,      "alliancebernstein": cmn_scraper6,
        "autodesk": cmn_scraper6,       "slack": cmn_scraper6,      "quantiphi": cmn_scraper6,      "commvault": cmn_scraper6,      "blueyonder": cmn_scraper6, "alteryx": cmn_scraper6,
        "cadence": cmn_scraper6,        "trimble": cmn_scraper6,    "workiva": cmn_scraper6,        "zendesk": cmn_scraper6,        "comcast": cmn_scraper6,    "verizon": cmn_scraper6,
        "tmobile": cmn_scraper6,        "syniverse": cmn_scraper6,  "dentsu": cmn_scraper6,         "davita": cmn_scraper6,         "centene": cmn_scraper6,    "cardinal": cmn_scraper6,
        "medtronic": cmn_scraper6,      "sanofi": cmn_scraper6,     "bms": cmn_scraper6,            "dexcom": cmn_scraper6,         "amgen": cmn_scraper6,      "gsk": cmn_scraper6,
        "hermann": cmn_scraper6,        "bcbsa": cmn_scraper6,      "bd": cmn_scraper6,             "vertex": cmn_scraper6,         "merck": cmn_scraper6,      "chg": cmn_scraper6,
        "cvs": cmn_scraper6,            "oreilly": cmn_scraper6,    "borgwarner": cmn_scraper6,     "sony_pictures": cmn_scraper6,  "draftkings": cmn_scraper6, "thomson_reuters": cmn_scraper6,
        "pixar": cmn_scraper6,          "pbs": cmn_scraper6,        "wolters_kluwer": cmn_scraper6, "pernod_richard": cmn_scraper6, "ncr": cmn_scraper6,        "synechron": cmn_scraper6,
        "ntt": cmn_scraper6,            "sonos": cmn_scraper6,      "philips": cmn_scraper6,        "broadcom": cmn_scraper6,       "occ": cmn_scraper6,        "peter_millar": cmn_scraper6,
        "nxp": cmn_scraper6,            "sysco": cmn_scraper6,      "pennstate": cmn_scraper6,      "utaustin": cmn_scraper6,       "kla": cmn_scraper6,        "thermofisher": cmn_scraper6,
        "ancestry": cmn_scraper6,       "circlek": cmn_scraper6,    "relx": cmn_scraper6,           "resmed": cmn_scraper6,         "broadridge": cmn_scraper6, "motorola": cmn_scraper6,
        "warner_bros": cmn_scraper6,    "disney": cmn_scraper6,     "lilly": cmn_scraper6,          "elevance": cmn_scraper6,       "3m": cmn_scraper6,         "morgan_stanley": cmn_scraper6,
        "crowdstrike": cmn_scraper6,    "marvell": cmn_scraper6,    "blizzard": cmn_scraper6,       "athena": cmn_scraper6,         "lowes": cmn_scraper6,      "applied_materials": cmn_scraper6,
        "magellan": cmn_scraper6,       "saif": cmn_scraper6,       "uline": cmn_scraper6,          "wex": cmn_scraper6,            "epiq": cmn_scraper6,       "neuberger_berman": cmn_scraper6,
        "zoom": cmn_scraper6,           "us_foods": cmn_scraper6,   "pacbio": cmn_scraper6,         "concentrix": cmn_scraper6,     "ups": cmn_scraper6,        "ss&c": cmn_scraper6,
        "univ_chicago": cmn_scraper6,   "genesys": cmn_scraper6,    "deluxe": cmn_scraper6,         "geico": cmn_scraper6,          "bcbsnc": cmn_scraper6,     "cox": cmn_scraper6,
        "lexisnexis": cmn_scraper6,     "pros": cmn_scraper6,       "evolent": cmn_scraper6,        "johnson": cmn_scraper6,        "redwood": cmn_scraper6,    "wolverine_worldwide": cmn_scraper6,
        "western_union": cmn_scraper6,  "shipt": cmn_scraper6,      "nike": cmn_scraper6,           "cat": cmn_scraper6,            "revvity": cmn_scraper6,    "jbhunt": cmn_scraper6,
        "proofpoint": cmn_scraper6,     "redfin": cmn_scraper6,     "stryker": cmn_scraper6,        "ehealth": cmn_scraper6,        "arch": cmn_scraper6,       "first_national": cmn_scraper6,
        "ascensus": cmn_scraper6,       "poshmark": cmn_scraper6,   "clearwater": cmn_scraper6,     "etsy": cmn_scraper6,           "sailpoint": cmn_scraper6,  "washington_post": cmn_scraper6,
        "gordon": cmn_scraper6,         "insulet": cmn_scraper6,    "gap": cmn_scraper6,            "reliaquest": cmn_scraper6,     "cleveland": cmn_scraper6,  "globus_medical": cmn_scraper6,
        "brookhaven": cmn_scraper6,     "carrier": cmn_scraper6,    "wgu": cmn_scraper6,            "transperfect": cmn_scraper6,   "pra": cmn_scraper6,        "world_kinect": cmn_scraper6,
        "samsung": cmn_scraper6,        "redhat": cmn_scraper6,     "travellers": cmn_scraper6,     "workday": cmn_scraper6,        "at&t": cmn_scraper6,       "cincinnati_childrens": cmn_scraper6,
        "rakuten": cmn_scraper6,        "polaris": cmn_scraper6,    "factset": cmn_scraper6,        "bmo": cmn_scraper6,            "gartner": cmn_scraper6,    "credit_acceptance": cmn_scraper6,
        "kyndryl": cmn_scraper6,        "toyota": cmn_scraper6,     "goosehead": cmn_scraper6,      "priceline": cmn_scraper6,      "ercot": cmn_scraper6,      "siemens_healthineers": cmn_scraper6,
        "jll": cmn_scraper6,            "aig": cmn_scraper6,        "morningstar": cmn_scraper6,    "vetsource": cmn_scraper6,      "dimensional": cmn_scraper6,"veterans_united": cmn_scraper6,
        "itron": cmn_scraper6,          "j&j": cmn_scraper6,        "labcorp": cmn_scraper6,        "ameriprise": cmn_scraper6,     "safelite": cmn_scraper6,   "chamberlain": cmn_scraper6,
        "lseg": cmn_scraper6,           "entrust": cmn_scraper6,    "scholastic": cmn_scraper6,     "schweitzer": cmn_scraper6,     "elsevier": cmn_scraper6,   "cloud_software": cmn_scraper6,
        "stride": cmn_scraper6,         "keybank": cmn_scraper6,    "anheuser-busch": cmn_scraper6, "capital_group": cmn_scraper6,  "newrez": cmn_scraper6,     "openlane": cmn_scraper6,
        "edwards": cmn_scraper6,        "videojet": cmn_scraper6,   "pimco": cmn_scraper6,          "hhmi": cmn_scraper6,           "cme_group": cmn_scraper6,  "kyriba": cmn_scraper6,
        "exeter": cmn_scraper6,         "pjt": cmn_scraper6,        "donaldson": cmn_scraper6,      "uniphore": cmn_scraper6,       "dataminr": cmn_scraper6,   "clarivate": cmn_scraper6,
        "assetmark": cmn_scraper6,      "strategic": cmn_scraper6,  "mcafee": cmn_scraper6,         "kbr": cmn_scraper6,            "manulife": cmn_scraper6,   "socure": cmn_scraper6,
        "iron_mountain": cmn_scraper6,  "neurocrine": cmn_scraper6, "amfam": cmn_scraper6,          "fti": cmn_scraper6,            "e*": cmn_scraper6,         "medline": cmn_scraper6,
        "dxc": cmn_scraper6,            "sunrun": cmn_scraper6,     "reputation": cmn_scraper6,     "boeing": cmn_scraper6,         "gen": cmn_scraper6,        "alsac": cmn_scraper6,
        "voya": cmn_scraper6,           "zelle": cmn_scraper6,      "avnet": cmn_scraper6,

        "7-11": cmn_scraper7,           "corewell": cmn_scraper7,   "raymond_james": cmn_scraper7,

        "f5": cmn_scraper8,             "sony": cmn_scraper8,       "waystar": cmn_scraper8,        "kion": cmn_scraper8,           "carmax": cmn_scraper8,

        # Smart Recruiters Career Pages
        "walmart2": cmn_scraper9,       "servicenow": cmn_scraper9, "visa": cmn_scraper9,           "experian": cmn_scraper9,       "intuitive": cmn_scraper9,  "western_digital": cmn_scraper9,
        "nbc": cmn_scraper9,            "balsam": cmn_scraper9,     "linkedin": cmn_scraper9,       "nagarro": cmn_scraper9,        "canva": cmn_scraper9,      "wise": cmn_scraper9,
        "nielseniq": cmn_scraper9,      "freshworks": cmn_scraper9, "guardianhealth": cmn_scraper9, "fortune": cmn_scraper9,        "sandisk": cmn_scraper9,

        "abbvie": cmn_scraper10,        "pa": cmn_scraper10,        "mcdonalds": cmn_scraper10,     "procore": cmn_scraper10,       "wellmark": cmn_scraper10,

        "palo_alto": cmn_scraper9_5,    "talan": cmn_scraper9_5,

        # Oracle Cloud Career Pages
        "jpmc": cmn_scraper11,          "bny": cmn_scraper11,       "fortinet": cmn_scraper11,      "oracle": cmn_scraper11,        "citizen": cmn_scraper11,   "macys": cmn_scraper11,
        "pearson": cmn_scraper11,       "nokia": cmn_scraper11,     "ford": cmn_scraper11,          "mount_sinai": cmn_scraper11,   "fanatics": cmn_scraper11,  "goldman_sachs": cmn_scraper11,
        "hackett": cmn_scraper11,       "cummins": cmn_scraper11,   "jefferies": cmn_scraper11,     "perficient": cmn_scraper11,    "kroger": cmn_scraper11,    "unitedlex": cmn_scraper11,
        "s&c": cmn_scraper11,           "verint": cmn_scraper11,    "hexaware": cmn_scraper11,      "staples": cmn_scraper11,       "envision": cmn_scraper11,  "reiter": cmn_scraper11,
        "dtcc": cmn_scraper11,          "nov": cmn_scraper11,       "computershare": cmn_scraper11, "delta_dental": cmn_scraper11,  "intelsat": cmn_scraper11,  "american_eagle": cmn_scraper11,
        "myriad": cmn_scraper11,        "adt": cmn_scraper11,       "navy_federal": cmn_scraper11,  "newmark": cmn_scraper11,       "verisk": cmn_scraper11,    "gm_financial": cmn_scraper11,

        # Workable Career Pages
        "tplink": cmn_scraper12,        "mindex": cmn_scraper12,    "therapynotes": cmn_scraper12,  "prepass": cmn_scraper12,       "datavisor": cmn_scraper12, "tiger_analytics": cmn_scraper12,
        "corcentric": cmn_scraper12,    "rokt": cmn_scraper12,      "proarch": cmn_scraper12,       "ag_consulting": cmn_scraper12, "byrider": cmn_scraper12,   "resource_innovation": cmn_scraper12,

        # iCiMS Career Pages
        "github": cmn_scraper13,        "statefarm": cmn_scraper13, "constellation": cmn_scraper13, "gallagher": cmn_scraper13,     "sirius": cmn_scraper13,    "dollar_general": cmn_scraper13,
        "principal": cmn_scraper13,     "rivian": cmn_scraper13,    "amd": cmn_scraper13,           "pds_health": cmn_scraper13,    "booking": cmn_scraper13,   "first_citizens": cmn_scraper13,
        "dish": cmn_scraper13,          "sheetz": cmn_scraper13,    "city_national": cmn_scraper13, "hinge_health": cmn_scraper13,  "ice": cmn_scraper13,       "republic_finance": cmn_scraper13,
        "selective": cmn_scraper13,     "incyte": cmn_scraper13,    "paychex": cmn_scraper13,       "medallia": cmn_scraper13,      "garmin": cmn_scraper13,    "konica_minolta": cmn_scraper13,
        "ulta": cmn_scraper13,          "novant": cmn_scraper13,    "osi_systems": cmn_scraper13,   "mcgraw_hill": cmn_scraper13,   "docusign": cmn_scraper13,  "publicis_groupe": cmn_scraper13,
        "jcpenny": cmn_scraper13,       "tufts": cmn_scraper13,     "blackline": cmn_scraper13,

        # iCiMS iFrame Career Pages
        "healthequity": cmn_scraper14,  "pepsico": cmn_scraper14,   "cotiviti": cmn_scraper14,      "lord_abbett": cmn_scraper14,   "sas": cmn_scraper14,       "liberty_mutual": cmn_scraper14,
        "blackhawk": cmn_scraper14,     "msci": cmn_scraper14,      "ddn": cmn_scraper14,           "healthedge": cmn_scraper14,    "biorad": cmn_scraper14,    "charles_schwab": cmn_scraper14,
        "fujifilm": cmn_scraper14,      "riverbed": cmn_scraper14,  "lynker": cmn_scraper14,        "vista_equity": cmn_scraper14,  "quest": cmn_scraper14,     "quest_diagnostics": cmn_scraper14,
        "lennox": cmn_scraper14,        "tds": cmn_scraper14,       "carecentrix": cmn_scraper14,   "mercury": cmn_scraper14,       "seismic": cmn_scraper14,   "east-west-bank": cmn_scraper14,
        "rs&h": cmn_scraper14,          "corgan": cmn_scraper14,    "fisher": cmn_scraper14,        "joby_aviation": cmn_scraper14, "woolpert": cmn_scraper14,  "constructconnect": cmn_scraper14,
        "cacu": cmn_scraper14,

        # Ultipro Career Pages
        "redsail": cmn_scraper15,       "vertex2": cmn_scraper15,   "convergint": cmn_scraper15,    "access": cmn_scraper15,        "ovative": cmn_scraper15,   "hensel_phelps": cmn_scraper15,
        "frontier": cmn_scraper15,      "tandem": cmn_scraper15,    "realpage": cmn_scraper15,      "discovery": cmn_scraper15,     "milliman": cmn_scraper15,  "odw": cmn_scraper15,
        "aventiv": cmn_scraper15,       "usp": cmn_scraper15,       "crown_castle": cmn_scraper15,  "ambry": cmn_scraper15,         "microport": cmn_scraper15, "hme": cmn_scraper15,
        "grocery": cmn_scraper15,

        # Rippling Career Pages
        "bamboo": cmn_scraper16,        "sheerid": cmn_scraper16,   "transcend": cmn_scraper16,     "rightcrowd": cmn_scraper16,    "cozey": cmn_scraper16,     "socket_telecom": cmn_scraper16,
        "thrive_global": cmn_scraper16, "galileo2": cmn_scraper16,  "schoolai": cmn_scraper16,      "partner.co": cmn_scraper16,    "serviceup": cmn_scraper16, "forterra": cmn_scraper16,
        "webull": cmn_scraper16,        "tixr": cmn_scraper16,      "odyssey": cmn_scraper16,       "infinitus": cmn_scraper16,     "cbts": cmn_scraper16,      "create_music": cmn_scraper16,
        "intelliguard": cmn_scraper16,  "primerx": cmn_scraper16,   "closinglock": cmn_scraper16,   "piedmont": cmn_scraper16,      "alertwest": cmn_scraper16, "adelaide": cmn_scraper16,
        "bizzycar": cmn_scraper16,      "charlie": cmn_scraper16,   "fountane": cmn_scraper16,      "owlet": cmn_scraper16,         "rentspree": cmn_scraper16,

        # Gem Career Pages
        "portal_ai": cmn_scraper17,     "linktree": cmn_scraper17,  "apartment-list": cmn_scraper17,"signoz": cmn_scraper17,        "roe_ai": cmn_scraper17,    "heavy-construction-systems": cmn_scraper17,
        "letter-ai": cmn_scraper17,     "converge": cmn_scraper17,  "boring-company": cmn_scraper17,"bluesky": cmn_scraper17,       "dragonfly": cmn_scraper17, "stack-auth-com": cmn_scraper17,
        "cloudraft": cmn_scraper17,     "gem": cmn_scraper17,       "silkline": cmn_scraper17,
    }
    return function_map



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
    return job_id in visited_ids


def is_valid(job_id, job_location, job_title, board):
    location_qualifiers = board.location_qualifiers
    job_title_qualifiers = board.job_title_qualifiers
    job_title_disqualifiers = board.job_title_disqualifiers
    # company_func = board.func
    visited_ids = board.visited_ids

    loc_q = is_valid_location(job_location, location_qualifiers)
    title_q = is_valid_title(job_title, job_title_qualifiers, job_title_disqualifiers)
    visit_q = is_id_visited(job_id, visited_ids)
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
                job_url = urljoin(board.url, job_title_elem["href"])
                job_title = job_title_elem.text.strip()
                job_id, job_location = [elem.text.strip() for elem in job_id_elem_list][:2] if job_id_elem_list else ["N/A", "N/A"]

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
    job_posts = soup.find_all("div", class_="job-tile job-grid-item search-results job-grid-item--all-actions-visible") or soup.find_all("div", class_="job-tile job-grid-item search-results job-grid-item--layout1 job-grid-item--all-actions-visible")

    for job_tile in job_posts:
        # Job URL and ID from <a> tag
        a_tag = job_tile.find('a', class_='job-grid-item__link')
        if a_tag and 'href' in a_tag.attrs:
            job_url = a_tag['href']
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
    job_posts = soup.find_all("div", class_="job-tile job-grid-item search-results job-grid-item--all-actions-visible") or soup.find_all("div", class_="job-tile job-grid-item search-results job-grid-item--layout1 job-grid-item--all-actions-visible")
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

            location_element = job.find("span", string=re.compile(r"^(Job Locations|Location|Location : Location)$"))
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
        job_posts = soup.find_all("div", class_="css-aapqz6")
        if not job_posts:
            flag = False
        for job in job_posts:
            # Extract job title and relative URL
            title_tag = job.find("a", class_="css-1f5v3ib-Anchor")
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

def cmn_scraper17(board=None):
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
        job_id = job['id'][-8:]
        job_title = job['title']
        locations = job['locations']
        ext_id = job['extId']
        job_url = f"{board.url}/{ext_id}"
        job_location = ", ".join([loc['name'] for loc in locations]) if locations else "N/A"
        # print(f"Job ID: {id}")
        # print(f"Job URL: {job_url}")
        # print(f"Job Title: {title}")
        # print(f"Locations: {location_names}")
        # print("-" * 40)

        if is_valid(job_id, job_location, job_title, board):
            jobs_list.append(Job(company, job_id, job_title, job_location, job_url))

    caller = inspect.stack()[1]
    caller_module = inspect.getmodule(caller[0])
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
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

    caller = inspect.stack()[1]  # Get caller's frame
    caller_module = inspect.getmodule(caller[0])  # Get caller's module
    if caller_module is None or caller_module.__name__ != __name__:
        print_jobs(jobs_list)
    webscraper_driver_cleanup(driver)
