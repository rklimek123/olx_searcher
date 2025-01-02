import http
from typing import List, Optional, Iterable

import requests
from bs4 import BeautifulSoup

from offer import Offer
from offer_page import OfferPageOlx, OfferPageOtodom


class OfferListing:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.url_storage = set()

    def find_word(self, keyword: str) -> List[Offer]:
        offers = self._process_url(self.base_url, keyword)
        if offers is None:
            return []
        i = 2
        while True:
            new_offers = self._process_url(self.base_url, keyword, page=i)
            if new_offers is None:
                break

            offers.extend(new_offers)
            i += 1
        return offers


    def _process_url(self, url: str, keyword: str, **kwargs) -> Optional[List[Offer]]:
        response = requests.get(url, params=kwargs)
        if response.status_code != http.HTTPStatus.OK:
            return None

        content = response.content
        soup = BeautifulSoup(content, features='html.parser')
        links: Iterable[str] = map(lambda a: a.get("href"), soup.select("a.css-rc5s2u"))

        offers = []

        for link in links:
            if link in self.url_storage:
                continue
            self.url_storage.add(link)

            if link.startswith('/d/'):
                offer = OfferPageOlx('https://olx.pl' + link)
            elif 'www.otodom.pl' in link:
                offer = OfferPageOtodom(link)
            else:
                raise NotImplementedError(link)

            parsed_offer = offer.parse_if_word_present(keyword)
            if parsed_offer is not None and predic(parsed_offer):
                print(parsed_offer)
                offers.append(parsed_offer)

        return offers


def predic(offer: Offer) -> bool:
    return (offer.total_rent <= 3000
            and offer.district not in (
                'Rembertów',
                'Wawer',
                'Białołęka',
                'Wesoła',
                'Ursus',
                'Włochy',
            )
    )
