import re
import time

import dateparser
import requests
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm


def scroll(driver, timeout, element):
    scroll_pause_time = timeout

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(scroll_pause_time)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If heights are the same it will exit the function
            break
        last_height = new_height


def scrape_google_reviews(page_url, driver):
    # Get's page set in page_url and opens it
    driver.get(page_url)

    def check_exists_by_xpath(xpath):
        try:
            driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True

    data = {}
    data['listing'] = []
    data['reviews'] = []

    # Find the name of the listing and captures in name
    name = driver.find_element_by_xpath("//h2[starts-with(@class, 'qrShPb kno-ecr-pt PZPZlf mfMhoc')]//span").text

    # Find the total number of reviews and captures in number_of_reviews
    number_of_reviews = re.findall("\d+",
                                   driver.find_element_by_xpath("//span[@class='hqzQac']//span//a//span").text.replace(
                                       ',', ''))[0]

    # Find the average review score
    average_review = \
        re.findall("\d+", driver.find_element_by_xpath("//span[@class='Aq14fc']").text.replace('.', ''))[
            0]

    # Checks address is provided on listing
    if check_exists_by_xpath("//span[@class='LrzXr']"):
        # Set's address as address on listing
        address = driver.find_element_by_xpath(
            "//span[@class='LrzXr']").text
    else:
        # Set's address as None
        address = None
    # Checks telephone number provided on listing
    if check_exists_by_xpath("//span[@class='LrzXr zdqRlf kno-fv']"):
        # Set's telephone as telephone on listing
        telephone = driver.find_element_by_xpath("//span[@class='LrzXr zdqRlf kno-fv']").text
    else:
        # Set's telephone as None
        telephone = None
    # Checks website url provide on listing
    if check_exists_by_xpath("//a[text()='Website']"):
        # Set's website as website on listing
        redirect_url = driver.find_element_by_xpath(
            "//a[text()='Website']").get_attribute(
            "href")
        website = redirect_url
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

    driver.find_element_by_xpath("//span[contains(text(), 'Google reviews')]").click()
    time.sleep(5)
    driver.find_element_by_xpath("//span[contains(text(),'Most relevant')]").click()
    time.sleep(5)
    driver.find_element_by_xpath("//div[contains(text(),'Newest')]").click()
    element_inside_popup = driver.find_element_by_xpath("//div[@class='review-dialog-list']")
    time.sleep(2)
    while True:  # scroll 5 times
        last_top = driver.execute_script('return arguments[0].scrollTop;', element_inside_popup)
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + 1000;', element_inside_popup)
        time.sleep(2)
        new_top = driver.execute_script('return arguments[0].scrollTop;', element_inside_popup)
        if new_top == last_top:
            # If heights are the same it will exit the function
            break

    reviews = driver.find_elements_by_xpath("//div[@jscontroller='e6Mltc']")
    for y in reviews:
        # Checks if review has user id, not all do, mainly old reviews
        try:
            # Scrapes user id element
            userid_element = y.find_element_by_xpath(
                './/div[@class="TSUbDb"]')
            # Extracts text from user id element
            userid = userid_element.text
        except NoSuchElementException:
            # Sets user id as none
            userid = None

        # Scrapes review date element
        review_date_element = y.find_element_by_xpath('.//span[@class="dehysf"]')
        # Extract's review date from title attribute
        review_date = review_date_element.text

        try:
            review_body_element = y.find_element_by_xpath(
                './/span[@class="review-full-text"]')
            review_body = review_body_element.text
        except NoSuchElementException:
            try:
                # Scrapes review body element
                review_body_element = y.find_element_by_xpath(
                    './/div[@class="Jtu6Td"]')
                # Extracts review body text
                review_body = review_body_element.text
            except NoSuchElementException:
                pass

        # Scrapes review rating element
        review_rating_element = y.find_element_by_xpath(
            './/span[@class="Fam1ne EBe2gf"]')
        # Extracts review rating from class, the end of the class name is the rating e.g. bubble_40
        review_rating = re.findall("\d+", review_rating_element.get_attribute("aria-label"))[0]

        # Append the list with the data extracted
        data['reviews'].append({
            'userid': userid,
            'review_date': review_date,
            'review_body': review_body,
            'review_rating': review_rating
        })
    driver.quit()
    return data
