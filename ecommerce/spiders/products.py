from typing import Union

import scrapy
from scrapy import Selector
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from twisted.internet.defer import Deferred


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["webscraper.io"]
    start_urls = [
        "https://webscraper.io/test-sites/e-commerce/static/computers/laptops",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason: str) -> Union[Deferred, None]:
        self.driver.close()
        return self.close(reason)

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
                ),
                "additional_info": {
                    "hdd_prices": self._parse_hdd_block_prices(
                        response, product
                    )
                }
            }
        next_page = response.css(".pagination > li")[-1].css(
            "a::attr(href)"
        ).get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def _parse_hdd_block_prices(
        self, response: Response, product: Selector
    ) -> dict[str, float]:
        absolute_url = response.urljoin(product.css(".title::attr(href)").get())
        self.driver.get(absolute_url)
        swatches = self.driver.find_element(By.CLASS_NAME, "swatches")
        buttons = swatches.find_elements(By.TAG_NAME, "button")
        prices = {}

        for button in buttons:
            if not button.get_property("disabled"):
                button.click()
                prices[button.get_property("value")] = float(
                    self.driver.find_element(
                        By.CLASS_NAME, "price"
                    ).text.replace("$", "")
                )
        return prices
