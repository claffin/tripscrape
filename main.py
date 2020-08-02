import json
import os
import uuid
import argparse
import time
import re

import dateparser
import requests

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager

# Instantiate the parser
parser = argparse.ArgumentParser()
# Required URL positional argument
parser.add_argument('url', type=str,
                    help='The URL of the TripAdvisor page')
parser.add_argument('--proxy', type=str, help='Optional, use HTTP Proxy')

# Parse arguments
args = parser.parse_args()

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


# Function to checks xpath exists
def check_exists_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


# Set's url from arguments
url = args.url
# Creates JSON list for use later
data = {}


# Function to scrape hotel listing
def scrape_hotel_listing(page_url):
    # Get's page set in page_url and opens it in Chrome
    driver.get(page_url)
    data['listing'] = []
    data['reviews'] = []

    # Find the name of the listing and captures in name
    name = driver.find_element_by_xpath("//h1[@id='HEADING']").text

    # Find the total number of reviews and captures in number_of_reviews
    number_of_reviews = re.findall("\d+",
                                   driver.find_element_by_xpath("//span[@class='_33O9dg0j']").text.replace(',', ''))[0]

    # Find the average review score
    average_review = \
        re.findall("\d+", driver.find_element_by_xpath("//span[@class='_3cjYfwwQ']").text.replace('.', ''))[
            0]

    # Checks address is provided on listing
    if check_exists_by_xpath("//div[@class='_1sPw_t0w _3sCS_WGO']//span[@class='_3ErVArsu jke2_wbp']"):
        # Set's address as address on listing
        address = driver.find_element_by_xpath(
            "//div[@class='_1sPw_t0w _3sCS_WGO']//span[@class='_3ErVArsu jke2_wbp']").text
    else:
        # Set's address as None
        address = None
    # Checks telephone number provided on listing
    if check_exists_by_xpath("//span[@class='_1_CU9UZ6 _3ErVArsu jke2_wbp']"):
        # Set's telephone as telephone on listing
        telephone = driver.find_element_by_xpath("//span[@class='_1_CU9UZ6 _3ErVArsu jke2_wbp']").text
    else:
        # Set's telephone as None
        telephone = None
    # Checks website url provide on listing
    if check_exists_by_xpath("//span[contains(text(),'Visit hotel website')]"):
        # Set's website as website on listing
        redirect_url = driver.find_element_by_xpath(
            "//div[@class='_1sPw_t0w _3sCS_WGO']//a[@class='_2wKz--mA _2U17tZ2G _1YIGmrPj _2-kzHHGX']").get_attribute(
            "href")
        website = requests.get(redirect_url).url
    else:
        # Set's website as None
        website = None

    # Add's the listing details above as json object
    data['listing'].append({
        'name': name,
        'number_of_reviews': number_of_reviews,
        'average_review': average_review,
        'address': address,
        'telephone': telephone,
        'website': website,
    })

    # Scrapes total number of pages element
    total_pages = driver.find_element_by_xpath("//a[6]")
    # Extract's total page numbers from element

    total_pages_numbers = int(total_pages.text) - 1163

    # Loop by number of total pages
    for z in tqdm(range(total_pages_numbers)):
        # Scrapes review ids from page
        ids = driver.find_elements_by_xpath("//div[@class='oETBfkHU']")
        # Creates review ids json list
        review_ids = []
        # Loop appends each review id to list
        for i in ids:
            review_ids.append(i.get_attribute('data-reviewid'))
        # Loop for each review on listing by review id
        for x in review_ids:
            # Checks if review has user id, not all do, mainly old reviews
            if check_exists_by_xpath('//div[@data-reviewid="' + x + '"]/..//a[@class="ui_header_link _1r_My98y"]'):
                # Scrapes user id element
                userid_element = driver.find_element_by_xpath(
                    '//div[@data-reviewid="' + x + '"]/..//a[@class="ui_header_link _1r_My98y"]')
                # Extracts text from user id element
                userid = userid_element.text
            else:
                # Sets user id as none
                userid = None

            # Scrapes review date element
            review_date_element = driver.find_element_by_xpath(
                '//div[@data-reviewid="' + x + '"]/..//div[@class="_2fxQ4TOx"]')
            # Extract's review date from title attribute
            review_date_cleansed = review_date_element.text.rsplit('review ')[1]
            review_date = dateparser.parse(review_date_cleansed).strftime('%B %Y')

            # Scrapes date of stay element
            date_of_stay_element = driver.find_element_by_xpath(
                '//div[@data-reviewid="' + x + '"]//span[@class="_34Xs-BQm"]')
            # Check if date of stay has text
            if date_of_stay_element.text:
                # Extracts the date only from the text
                date_of_stay = date_of_stay_element.text.replace("Date of stay: ", "")

            else:
                # Sets date of visit as None
                date_of_visit = None

            # Scrapes title of review
            review_title_element = driver.find_element_by_xpath(
                '//div[@data-reviewid="' + x + '"]//a[@class="ocfR3SKN"]')
            # Extract title of review
            review_title = review_title_element.text

            # Checks if review needs to be expanded (More...)
            if check_exists_by_xpath('//div[@data-reviewid="' + x + '"]//div[@class="XUVJZtom"]'):
                time.sleep(1)
                # Review is expanded
                if driver.find_element_by_xpath(
                        '//div[@data-reviewid="' + x + '"]//div[@class="XUVJZtom"]').text == "Read more":
                    driver.find_element_by_xpath('//div[@data-reviewid="' + x + '"]//div[@class="XUVJZtom"]').click()
                # Provide time for review to expand
                time.sleep(1)

            # Scrapes review body element
            review_body_element = driver.find_element_by_xpath(
                '//div[@data-reviewid="' + x + '"]//q[@class="IRsGHoPm"]')
            # Extracts review body text
            review_body = review_body_element.text

            # Scrapes review rating element
            review_rating_element = driver.find_element_by_xpath(
                '//div[@data-reviewid="' + x + '"]//span[starts-with(@class, "ui_bubble_rating bubble_")]')
            # Extracts review rating from class, the end of the class name is the rating e.g. bubble_40
            review_rating = re.findall("\d+", review_rating_element.get_attribute("class"))[0]

            # Append the list with the data extracted
            data['reviews'].append({
                'userid': userid,
                'review_date': str(review_date),
                'date_of_stay': date_of_stay,
                'review_title': review_title,
                'review_body': review_body,
                'review_rating': review_rating
            })

        # Checks if there is a next page to scrape
        if total_pages_numbers > 1:
            # Finds Next button and clicks it
            driver.find_element_by_xpath("//a[contains(text(),'Next')]").click()
            # Minus page number after clicked, will stop scraping when no more pages available
            total_pages_numbers = total_pages_numbers - 1
            # Allow page to load
            time.sleep(1)
    return data


# Function to scrape restaurant listing
def scrape_restaurant_listing(page_url):
    # Get's page set in page_url and opens it in Chrome
    driver.get(page_url)

    data['listing'] = []
    data['reviews'] = []

    # Find the name of the listing and captures in name
    name = driver.find_element_by_xpath("//h1[contains(@class,'_3a1XQ88S')]").text

    # Find the total number of reviews and captures in number_of_reviews
    number_of_reviews = re.findall("\d+",
                                   driver.find_element_by_xpath("//span[@class='_3Wub8auF']").text.replace(',', ''))[0]

    # Find the average review score
    average_review = re.findall("\d+", driver.find_element_by_xpath("//span[@class='r2Cf69qf']").text.replace('.', ''))[
        0]

    # Checks address is provided on listing
    if check_exists_by_xpath("//a[@href='#MAPVIEW']"):
        # Set's address as address on listing
        address = driver.find_element_by_xpath("//a[@href='#MAPVIEW']").text
    else:
        # Set's address as None
        address = None
    # Checks telephone number provided on listing
    if check_exists_by_xpath("//span[@class='_15QfMZ2L']"):
        # Set's telephone as telephone on listing
        telephone = driver.find_element_by_xpath("//span[@class='_15QfMZ2L']").text
    else:
        # Set's telephone as None
        telephone = None
    # Checks website url provide on listing
    if check_exists_by_xpath("//a[contains(text(),'Website')]"):
        # Set's website as website on listing
        website = driver.find_element_by_xpath("//a[contains(text(),'Website')]").get_attribute("href")
    else:
        # Set's website as None
        website = None

    # Add's the listing details above as json object
    data['listing'].append({
        'name': name,
        'number_of_reviews': number_of_reviews,
        'average_review': average_review,
        'address': address,
        'telephone': telephone,
        'website': website,
    })

    # Scrapes total number of pages element
    total_pages = driver.find_element_by_xpath("//*[starts-with(@class,'pageNum last')]")
    # Extract's total page numbers from element
    total_pages_numbers = int(total_pages.text)

    # Loop by number of total pages
    for z in tqdm(range(total_pages_numbers)):
        # Scrapes review ids from page
        ids = driver.find_elements_by_xpath("//*[starts-with(@id,'review_')]")
        # Creates review ids json list
        review_ids = []
        # Loop appends each review id to list
        for i in ids:
            review_ids.append(i.get_attribute('id'))
        # Loop for each review on listing by review id
        for x in review_ids:
            # Checks if review has user id, not all do, mainly old reviews
            if check_exists_by_xpath('//*[@id="' + x + '"]//div[@class="info_text pointer_cursor"]/div[1]'):
                # Scrapes user id element
                userid_element = driver.find_element_by_xpath(
                    '//*[@id="' + x + '"]//div[@class="info_text pointer_cursor"]/div[1]')
                # Extracts text from user id element
                userid = userid_element.text
            else:
                # Sets user id as none
                userid = None

            # Scrapes review date element
            review_date_element = driver.find_element_by_xpath('//*[@id="' + x + '"]//span[@class="ratingDate"]')
            # Extract's review date from title attribute
            review_date = review_date_element.get_attribute("title")

            # Checks if the date of visit is available for the review
            if check_exists_by_xpath('//*[@id="' + x + '"]//div[@class="prw_rup prw_reviews_stay_date_hsx"]'):
                # Scrapes date of visit element
                date_of_visit_element = driver.find_element_by_xpath(
                    '//*[@id="' + x + '"]//div[@class="prw_rup prw_reviews_stay_date_hsx"]')
                # Check if date of visit has text
                if date_of_visit_element.text:
                    # Extracts the date only from the text
                    date_of_visit = date_of_visit_element.text.replace("Date of visit: ", "")
                else:
                    # Sets date of visit as None
                    date_of_visit = None

            # Checks if review title is available
            if check_exists_by_xpath('//*[@id="' + x + '"]//div[@class="quote"]'):
                # Scrapes title of review
                review_title_element = driver.find_element_by_xpath('//*[@id="' + x + '"]//div[@class="quote"]')
            # Checks if review title is available, newest review has isNew in class name
            if check_exists_by_xpath('//*[@id="' + x + '"]//div[@class="quote isNew"]'):
                # Scrapes title of review
                review_title_element = driver.find_element_by_xpath('//*[@id="' + x + '"]//div[@class="quote isNew"]')
            # Extract title of review
            review_title = review_title_element.text

            # Checks if review needs to be expanded (More...)
            if check_exists_by_xpath('//*[@id="' + x + '"]/div/div[2]/div[2]/div/p/span'):
                # Review is expanded
                driver.find_element_by_xpath('//*[@id="' + x + '"]/div/div[2]/div[2]/div/p/span').click()
                # Provide time for review to expand
                time.sleep(1)

            # Scrapes review body element
            review_body_element = driver.find_element_by_xpath(
                '//*[@id="' + x + '"]//div[@class="prw_rup prw_reviews_text_summary_hsx"]/div/p')
            # Extracts review body text
            review_body = review_body_element.text

            # Scrapes review rating element
            review_rating_element = driver.find_element_by_xpath(
                '//*[@id="' + x + '"]//span[starts-with(@class, "ui_bubble_rating bubble_")]')
            # Extracts review rating from class, the end of the class name is the rating e.g. bubble_40
            review_rating = re.findall("\d+", review_rating_element.get_attribute("class"))[0]

            # Append the list with the data extracted
            data['reviews'].append({
                'userid': userid,
                'review_date': review_date,
                'date_of_visit': date_of_visit,
                'review_title': review_title,
                'review_body': review_body,
                'review_rating': review_rating
            })

        # Checks if there is a next page to scrape
        if total_pages_numbers > 1:
            # Finds Next button and clicks it
            driver.find_element_by_xpath("//a[contains(text(),'Next')]").click()
            # Minus page number after clicked, will stop scraping when no more pages available
            total_pages_numbers = total_pages_numbers - 1
            # Allow page to load
            time.sleep(1)
    return data


# Executes function according to the listing type
if '/Restaurant_' in url:
    scrape_restaurant_listing(url)
elif '/Hotel_' in url:
    scrape_hotel_listing(url)
elif '/Attraction_Review' in url:
    print("Attractions not yet supported")
elif '/VacationRentalReview-' in url:
    print("Vacation rentals not yet supported")

# Create tmp directory, if it doesn't exist
if not os.path.exists('tmp'):
    os.makedirs('tmp')

# Writes data output to JSON file, named using a UUID
with open('./tmp/' + str(uuid.uuid1()) + '.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)

# Closes the browser and session
driver.quit()
