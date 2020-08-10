import re

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def largestNumber(in_str):
    l = [int(x) for x in in_str.split() if x.isdigit()]
    return max(l) if l else None


def scrape_yelp_reviews(yelp_url):
    data = {}
    data['listing'] = []
    data['reviews'] = []

    page = requests.get(yelp_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    name = soup.find('h1',
                     class_='lemon--h1__373c0__2ZHSL heading--h1__373c0___56D3 undefined heading--inline__373c0__1jeAh').text.strip()
    number_of_reviews = re.findall("\d+", soup.find('p',
                                  class_='lemon--p__373c0__3Qnnj text__373c0__2U54h text-color--mid__373c0__27i5f text-align--left__373c0__1Uy60 text-size--large__373c0__1j9OF').text.strip())[0]
    average_review = re.findall("\d+",soup.find('div', class_=re.compile(r'lemon--div__373c0__1mboc i-stars__373c0__1T6rz'))[
        'aria-label'].replace(".",""))[0]
    address = soup.find('address', class_='lemon--address__373c0__2sPac').text.strip()
    telephone_position = soup.find('p', string='Phone number')
    telephone = telephone_position.find_next_sibling().text.strip()
    website = soup.find('a',
                        class_='lemon--a__373c0__IEZFH link__373c0__2-XHa link-color--blue-dark__373c0__4vqlF link-size--inherit__373c0__nQcnG').text.strip()
    total_pages = largestNumber(soup.find('span', string=re.compile('^1 of')).text.strip())
    total_pages_number = total_pages

    data['listing'].append({
        'name': name,
        'number_of_reviews': number_of_reviews,
        'average_review': average_review,
        'address': address,
        'telephone': telephone,
        'website': website,
    })
    review_count = 0
    for z in tqdm(range(total_pages_number)):

        page = requests.get(yelp_url + '?start=' + str(review_count))
        soup = BeautifulSoup(page.content, 'html.parser')
        reviews = soup.find_all('li',
                                class_='lemon--li__373c0__1r9wz margin-b3__373c0__q1DuY padding-b3__373c0__342DA border--bottom__373c0__3qNtD border-color--default__373c0__3-ifU')
        for review in reviews:
            try:
                userid = review.find('a',
                                 class_='lemon--a__373c0__IEZFH link__373c0__1G70M link-color--inherit__373c0__3dzpk link-size--inherit__373c0__1VFlE').text.strip(),
            except AttributeError:
                userid = 'Hidden'

            review_date = review.find('span',
                                      class_='lemon--span__373c0__3997G text__373c0__2Kxyz text-color--mid__373c0__jCeOG text-align--left__373c0__2XGa-').text.strip(),
            review_body = review.find('span', class_='lemon--span__373c0__3997G raw__373c0__3rKqk').text.strip(),
            review_rating = str(largestNumber(review.find('div', class_=re.compile(r'lemon--div__373c0__1mboc i-stars__373c0__1T6rz'))[
                                'aria-label'].replace(".",""))),

            data['reviews'].append({
                'userid': userid[0],
                'review_date': review_date[0],
                'review_body': review_body[0],
                'review_rating': review_rating[0],
            })
        review_count = review_count + 20
    return data
