import requests
from typing import List
from bs4 import BeautifulSoup
import re

class AsinParser:
    def __init__(self):
        self.URL = "https://www.amazon.com/hz/reviews-render/ajax/reviews/get/"
        self.HEADERS = {
            'accept': 'text/html,*/*',
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            # 'x-requested-with': 'XMLHttpRequest',
            'Cookie': 'session-id=139-1826338-8807151; session-id-time=2082787201l; session-token=PGFIPkWZd/+RwqUvBwXpx34aevojZUuYdossQeFG5sFpk0jgd/9RWB5ITL6vjBYiSBihX41xOiMUL9pwliVx5Nj9sDMdoX1wWD8dsR4gyM5j4iHk6K0O7IlT9N6QJfCE2WveDi/RLgeux6a1gA5oCJ5d+BiTjrM32s+wVM5fGua7RQyCLiLv4i8kZquJCrWgGNVdDD8cayqItYQM5uoBSJXdrx8OcyRJ; ubid-main=134-9972213-6249236'
        }

    def valid_html(self, html_str: str) -> bool:
        if html_str == "":
            return False
        if html_str.startswith("loaded"):
            return False
        if html_str.startswith("<div id=\"filter-info-section\""):
            return False
        if html_str.startswith("<div class=\"a-section cr-list-loading reviews-loading aok-hidden\""):
            return False
        if html_str.startswith("<h3 data-hook=\"arp-local-reviews-header\""):
            return False
        if html_str.startswith("<div id=\"cr-translate-"):
            return False
        if html_str.startswith("<div class=\"a-form-actions a-spacing-top-extra-large\">"):
            return False
        return True

    def get_htmls(self, asin: str) -> List[str]:
        html_reviews = []
        page_number = 1
        while True:
            payload = f"reviewerType=all_reviews&pageNumber={page_number}&pageSize=200&asin={asin}"
            response = requests.request("POST", self.URL, headers=self.HEADERS, data=payload)

            htmls = [eval(x.strip(" \n"))[-1] for x in response.text.split("&&&")[:-1]]
            htmls = list(filter(self.valid_html, htmls))

            if len(htmls) == 0:
                break
            html_reviews.extend(htmls)
            page_number += 1
        return html_reviews
    
    def parse_review(self, html_review: str) -> dict:
        bs_html = BeautifulSoup(html_review)

        bs_text = bs_html.find(attrs={'data-hook' : "review-star-rating"})
        stars_text = bs_text.text.strip("\n") if bs_text is not None else None

        bs_text = bs_html.find(attrs={'data-hook' : "review-date"})
        review_date_location_text = bs_text.text.strip("\n") if bs_text is not None else None

        bs_text = bs_html.find(attrs={'data-hook' : "review-body"})
        review_body_text = bs_text.text.strip("\n") if bs_text is not None else None

        bs_text = bs_html.find(attrs={'data-hook' : "review-title"})
        review_title_text = bs_text.text.strip("\n") if bs_text is not None else None

        bs_text = bs_html.find(attrs={'data-hook' : "helpful-vote-statement"})
        vote_stats_text = bs_text.text.strip("\n") if bs_text is not None else None

        bs_text = bs_html.find(attrs={'data-hook' : "avp-badge"})
        verified_text = bs_text.text.strip("\n") if bs_text is not None else None

        try:
            user_id = bs_html.find(attrs={"data-hook": "genome-widget"}).find("a").attrs["href"].split("/")[3].split(".")[-1]
        except:
            user_id = None

        image_urls = None
        for script in bs_html.find_all("script"):
            if "imagePopoverController.initImagePopover" in script.text:
                image_urls = ", ".join(re.findall(r'\[(.*?)\]', script.text))

        return {
            "review_title": review_title_text,
            "review": review_body_text,
            "date_location": review_date_location_text,
            "stars": stars_text,
            "votes": vote_stats_text,
            "verified": verified_text,
            "image_urls": image_urls,
            "user_id": user_id,
        }


    def get_reviews(self, asin: str) -> List[dict]:
        html_reviews = self.get_htmls(asin)

        return [self.parse_review(x) for x in html_reviews]