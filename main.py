import json
import os
import uuid
import argparse

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager

# Instantiate the parser
from google import scrape_google_reviews
from tripadvisor import scrape_restaurant_listing, scrape_hotel_listing
from yelp import scrape_yelp_reviews

parser = argparse.ArgumentParser()
# Required URL positional argument
parser.add_argument('url', type=str,
                    help='The URL of the TripAdvisor page')
parser.add_argument('--proxy', type=str, help='Optional, use HTTP Proxy')

# Parse arguments
args = parser.parse_args()


def chrome_setup():
    # Set Chrome options
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    if args.proxy:
        options.add_argument('--proxy-server=%s' % args.proxy)

    # Downloads latest ChromeDriver and sets it as the driver for Selenium
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    return driver

# Set's url from arguments
url = args.url

# Executes function according to the listing type
if '/Restaurant_' in url:
    driver = chrome_setup()
    data = scrape_restaurant_listing(url, driver)
elif '/Hotel_' in url:
    driver = chrome_setup()
    data = scrape_hotel_listing(url, driver)
elif '/Attraction_Review' in url:
    print("Attractions not yet supported")
elif '/VacationRentalReview-' in url:
    print("Vacation rentals not yet supported")
elif '/biz' in url:
    data = scrape_yelp_reviews(url)
elif '/search?' in url:
    driver = chrome_setup()
    data = scrape_google_reviews(url, driver)

# Create tmp directory, if it doesn't exist
if not os.path.exists('tmp'):
    os.makedirs('tmp')

# Writes data output to JSON file, named using a UUID
with open('./tmp/' + str(uuid.uuid1()) + '.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)
