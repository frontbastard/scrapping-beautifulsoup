from pathlib import Path

import scrapy
from scrapy.http import Response


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["webscraper.io"]
    start_urls = [
        "https://webscraper.io/test-sites/e-commerce/static/computers/laptops",
    ]

    def parse(self, response: Response, **kwargs):
        for product in response.css(".thumbnail"):
            yield {
                "title": product.css(".title::attr(title)").get(),
                "description": product.css(".description::text").get(),
                "price": float(
                    product.css(".price::text").get().replace("$", "")
                ),
                "rating": int(product.css("p::attr(data-rating)").get()),
                "num_of_reviews": int(
                    product.css(".review-count::text").get().split()[0]
                )
            }
