import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://webscraper.io/"
HOME_URL = urljoin(BASE_URL, "test-sites/e-commerce/allinone")
LAPTOP_URL = urljoin(
    BASE_URL, "test-sites/e-commerce/static/computers/laptops"
)


@dataclass
class Product:
    title: str
    description: str
    price: float
    num_of_reviews: int
    rating: int
    num_of_reviews: int


PRODUCT_FIELDS = [field.name for field in fields(Product)]

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s] %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout),
    ]
)


def parse_single_product(product: Tag) -> Product:
    return Product(
        title=product.select_one(".title")["title"],
        description=product.select_one(".description").text,
        price=float(product.select_one(".price").text.replace("$", "")),
        rating=int(product.select_one("p[data-rating]")["data-rating"]),
        num_of_reviews=int(
            product.select_one(".review-count").text.split()[0]
        )
    )


def get_home_products() -> [Product]:
    text = requests.get(HOME_URL).content
    soup = BeautifulSoup(text, "html.parser")
    products = soup.select(".card-body")
    return [parse_single_product(product) for product in products]


def get_num_pages(page_soup: Tag) -> int:
    pagination = page_soup.select_one(".pagination")
    if pagination is None:
        return 1
    return int(pagination.select("li")[-2].text)


def get_single_page_products(page_soup: Tag) -> [Product]:
    products = page_soup.select(".card-body")
    return [parse_single_product(product) for product in products]


def get_laptop_page_products() -> [Product]:
    logging.info(f"Start parsing page #1")
    text = requests.get(LAPTOP_URL).content
    first_page_soup = BeautifulSoup(text, "html.parser")
    all_products = get_single_page_products(first_page_soup)
    # num of pages
    num_pages = get_num_pages(first_page_soup)
    # iterate
    for page_num in range(2, num_pages + 1):
        logging.info(f"Start parsing page #{page_num}")
        text = requests.get(LAPTOP_URL, {"page": page_num}).content
        next_page_soup = BeautifulSoup(text, "html.parser")
        all_products.extend(get_single_page_products(next_page_soup))
    return all_products


def write_products_to_csv(products: [Product]) -> None:
    with open("results.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(PRODUCT_FIELDS)
        writer.writerows([astuple(product) for product in products])


def main():
    # print(get_home_products())
    write_products_to_csv(get_laptop_page_products())


if __name__ == "__main__":
    main()
