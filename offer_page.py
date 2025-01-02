import http
from abc import abstractmethod, ABC
from functools import reduce
from typing import Optional

import requests
from bs4 import BeautifulSoup, Tag

from offer import Offer


class OfferPage(ABC):
    def __init__(self, href_url: str):
        self.href_url = href_url

    def parse_if_word_present(self, keyword: str) -> Optional[Offer]:
        response = requests.get(self.href_url)
        if response.status_code != http.HTTPStatus.OK:
            return None

        soup = BeautifulSoup(response.content, features='html.parser')
        description = self.get_description(soup)
        if keyword not in description:
            return None

        return Offer(
            self.href_url,
            area=self.get_area(soup),
            district=self.get_district(soup),
            name=self.get_name(soup),
            rent=self.get_rent(soup),
            rooms=self.get_rooms(soup),
            utilities=self.get_utilities(soup),
            description=description
        )

    @abstractmethod
    def get_description(self, soup: BeautifulSoup) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_rent(self, soup: BeautifulSoup) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_utilities(self, soup: BeautifulSoup) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_rooms(self, soup: BeautifulSoup) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_area(self, soup: BeautifulSoup) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_name(self, soup: BeautifulSoup) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_district(self, soup: BeautifulSoup) -> str:
        raise NotImplementedError

class OfferPageOlx(OfferPage):
    def get_description(self, soup: BeautifulSoup) -> str:
        description = soup.find('div', attrs={'class': 'css-bgzo2k er34gjf0'})
        if description is None:
            return ''
        plaintext = reduce(lambda a, e: a + e.text, description.contents, '')
        return plaintext

    def get_rent(self, soup: BeautifulSoup) -> int:
        rent_box = soup.find('h3', attrs={'class': 'css-t9ee1 er34gjf0'})
        text = rent_box.contents[0].text[:-2].replace(' ', '')
        return num_to_int(text)

    def get_utilities(self, soup: BeautifulSoup) -> int:
        cstr = 'Czynsz (dodatkowo):'
        boxes = self.get_prop_box(soup, cstr)
        text = boxes.contents[0].text[len(cstr):-2].replace(' ', '')
        return num_to_int(text)

    def get_rooms(self, soup: BeautifulSoup) -> int:
        cstr = 'Liczba pokoi:'
        boxes = self.get_prop_box(soup, cstr)
        text = boxes.contents[0].text[len(cstr):]
        if 'Kawalerka' in text:
            return 1
        texts = text.split()
        return num_to_int(texts[0])

    def get_area(self, soup: BeautifulSoup) -> int:
        cstr = 'Powierzchnia:'
        boxes = self.get_prop_box(soup, cstr)
        text = boxes.contents[0].text[len(cstr):-2].replace(' ', '')
        return num_to_int(text)

    def get_name(self, soup: BeautifulSoup) -> str:
        header = soup.find('h1')
        return header.contents[0].text

    def get_district(self, soup: BeautifulSoup) -> str:
        ol = soup.find('ol', attrs={'data-testid': 'breadcrumbs'})
        li = ol.contents[-1]
        return " ".join(li.text.split()[2:])

    def get_prop_box(self, soup: BeautifulSoup, tag: str) -> Tag:
        boxes = soup.find_all('p', attrs={'class': 'css-b5m1rv er34gjf0'})
        filtered = list(filter(lambda b: tag in b.text, boxes))[0]
        return filtered


class OfferPageOtodom(OfferPage):
    def get_description(self, soup: BeautifulSoup) -> str:
        description = soup.find('div', attrs={'data-cy': 'adPageAdDescription'})
        if description is None:
            return ''
        plaintext = reduce(lambda a, e: a + e.text, description.contents, '')
        return plaintext

    def get_rent(self, soup: BeautifulSoup) -> int:
        rent_box = soup.find('strong', attrs={'data-cy': 'adPageHeaderPrice'})
        text = rent_box.contents[0].text[:-2].replace(' ', '')
        return num_to_int(text)

    def get_utilities(self, soup: BeautifulSoup) -> int:
        cstr = 'Czynsz'
        box = self.get_prop_box(soup, cstr)
        if box is None:
            return -1
        text = box[:-2].replace(' ', '')
        return num_to_int(text)

    def get_rooms(self, soup: BeautifulSoup) -> int:
        cstr = 'Liczba pokoi'
        box = self.get_prop_box(soup, cstr)
        if box is None:
            return -1
        text = box.replace(' ', '')
        return num_to_int(text)

    def get_area(self, soup: BeautifulSoup) -> int:
        cstr = 'Powierzchnia'
        box = self.get_prop_box(soup, cstr)
        if box is None:
            return -1
        text = box.split()[0]
        return num_to_int(text)

    def get_name(self, soup: BeautifulSoup) -> str:
        description = soup.find('div', attrs={'data-cy': 'adPageAdTitle'})
        plaintext = reduce(lambda a, e: a + e.text, description.contents, '')
        return plaintext

    def get_district(self, soup: BeautifulSoup) -> str:
        description = soup.find('div', attrs={'data-cy': 'ad.breadcrumbs'})
        return description.contents[4].text

    def get_prop_box(self, soup: BeautifulSoup, tag: str) -> Optional[Tag]:
        boxes = soup.find_all('div', attrs={'role': 'region'})

        for box in boxes:
            left = box.contents[1]
            right = box.contents[2]
            if tag in left:
                t = right.contents[0].text
                if 'Zapytaj' not in t:
                    return t

        return None


def num_to_int(numstr: str) -> int:
    return int(float(numstr.replace(',', '.')))
