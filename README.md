# scrap_amazon_books


* Using scrapy to scrap information about books from amazon
## sample output
```json
[
    {
        "book_title": "Learning Python, 5th Edition",
        "book_rate": "4.0 out of 5 stars",
        "number_of_people_rating_book": "343",
        "final_price": "$29.81",
        "book_url": "/Learning-Python-5th-Mark-Lutz/dp/1449355730/ref=sr_1_1?keywords=python&qid=1565893950&s=books&sr=1-1",
        "publisher_name_and_date": " O'Reilly Media; Fifth edition (July 6, 2013)",
        "number_of_pages": " 1648 pages"
    }
]
```

## Run

```sh
$ cd scrap_amazon_books
$ scrapy crawl amazonbooks -o book.json -a search_keyword="<search_keyword>" 
```

or run in docker-compose

```sh
$  docker-compose up --build
```
