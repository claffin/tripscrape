import re

from selenium.common.exceptions import NoSuchElementException


def scrape_opentable_reviews(page_url, driver):
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
    name = driver.find_element_by_xpath("//h1[@class='a6481dc2 _4a4e7a6a']").text

    # Find the total number of reviews and captures in number_of_reviews
    number_of_reviews = re.findall("\d+",
                                   driver.find_element_by_xpath("//div[@id='total-reviews']//span").text.replace(
                                       ',', ''))[0]

    # Find the average review score
    average_review = \
        re.findall("\d+", driver.find_element_by_xpath("//div[@id='star-rating']//div[@class='c3981cf8 _965a91d5']").text.replace('.', ''))[
            0]

    # Checks address is provided on listing
    if check_exists_by_xpath("//div[@class='c3981cf8 _965a91d5']//a[contains(@class,'_3ddfcf5c _5c8483c8')]//span"):
        # Set's address as address on listing
        address = driver.find_element_by_xpath(
            "//div[@class='c3981cf8 _965a91d5']//a[contains(@class,'_3ddfcf5c _5c8483c8')]//span").text
    else:
        # Set's address as None
        address = None
    # Checks telephone number provided on listing
    if check_exists_by_xpath("//div[@class='_93f3b715']//div[2]//div[1]//div[2]//div[2]"):
        # Set's telephone as telephone on listing
        print('found telephone')
        telephone = driver.find_element_by_xpath("//div[@class='_93f3b715']//div[2]//div[1]//div[2]//div[2]").text
        print(telephone)
    else:
        # Set's telephone as None
        print('No telephone')
        telephone = None
    # Checks website url provide on listing
    if check_exists_by_xpath("//div[@class='e7ff71b6 b2f6d1a4']//a[contains(@class,'_3ddfcf5c _5c8483c8')]"):
        # Set's website as website on listing
        redirect_url = driver.find_element_by_xpath(
            "//div[@class='e7ff71b6 b2f6d1a4']//a[contains(@class,'_3ddfcf5c _5c8483c8')]").get_attribute(
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

    return data
