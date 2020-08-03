# tripscrape

Scrapes Tripadvisor reviews and outputs the high level info about the place (e.g. name, number of reviews, average rating, address, telephone, website). 

Individual reviews are also outputted with user id, review date, date of visit, review body, review rating. See example output below.

Only supports Hotels and Restaurants currently. Attractions and Vacation Rentals are on the roadmap (see issues).

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

Python 3.8 or Docker required. 

## Get started (using virtualenv)

A step by step series of examples that tell you how to get a development env running.

Clone the repository

```
git clone https://github.com/claffin/tripscrape.git
```


And create virtualenv and install requirements.

```
python3 -m venv /path/to/new/virtual/environment
source /path/to/new/virtual/environment/bin/activate
pip install -r requirements.txt
```

Run tripscrape.

```
python main.py $url
e.g. python main.py https://www.tripadvisor.co.uk/Hotel_Review-g186338-d187686-Reviews-The_Savoy-London_England.html
```

## Get Started (Docker)

Pull the Docker image.
```
docker pull laffin/tripscrape
```
Run the Docker image.
```
docker run laffin/tripscrape $url 
```
### Example
```
docker run laffin/tripscrape https://www.tripadvisor.co.uk/Hotel_Review-g186338-d187686-Reviews-The_Savoy-London_England.html
```

## Options

Two options:
url = The URL you would like to scrape.

```
tripscrape $url --proxy $proxy
```

## Output
The output is stored in 'tmp' in the same folder the app runs in. 

### Example Output

```
{
    "listing": [
        {
            "name": "The Green Papaya",
            "number_of_reviews": "164",
            "average_review": "40",
            "address": "191 Mare Street, London E8 3QE England",
            "telephone": "+44 20 8985 5486",
            "website": "http://www.green-papaya.com/"
        }
    ],
    "reviews": [
        {
            "userid": "elenav527",
            "review_date": "3 January 2020",
            "date_of_visit": "January 2020",
            "review_title": "Would go back, very good options on menu",
            "review_body": "Nice little resto. I would consider giving higher rating but we only tried 3 dishes. The service was good, fast and attentive. Food came fast even if there were many guests. Veggie Pho very good, spicy noodles with chicken fair and fried spring rolls with pork and seafood yummy",
            "review_rating": "40"
        },
        {
            "userid": "A6125KMdaved",
            "review_date": "27 December 2019",
            "date_of_visit": "December 2019",
            "review_title": "Disappointing food. Miserable staff.",
            "review_body": "We were only the second group in on the early Sunday evening so the staff were not rushed or stressed but were simply miserable. Two of us had phos and both described them as watery and lacking in flavour. We will never return.",
            "review_rating": "20"
        },
    ]
}
```

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/claffin/tripscrape/tags). 

## Authors

* **claffin** - *Initial work* - [claffin](https://github.com/claffin)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

