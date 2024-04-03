import re
from typing import List
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from abc import ABCMeta, abstractmethod

from tsc.types import Charger, Coordinate


class ElementCollector(metaclass=ABCMeta):
    CHARGER_TEXT_REGEX: re.Pattern
    crawling_instance: BeautifulSoup

    def get_charger_data_from_text(self, text: str) -> Charger | None:
        matched = self.CHARGER_TEXT_REGEX.match(text)
        if matched:
            return Charger(
                charging_speed=float(matched.group(1)),
                charger_count=int(matched.group(2)),
            )
        return None

    @staticmethod
    def _get_coordinate_from_url(url: str) -> Coordinate | None:
        parsed = urlparse(url)
        queries = parsed.query.split("&")

        for q in queries:
            elements = q.split("=")
            if len(elements) == 3 and elements[0] == "scale":
                s_lat, s_lng = elements[2].split(",")
                lat, lng = float(s_lat), float(s_lng)

                return Coordinate(
                    latitude=float("{:.6f}".format(lat)),
                    longitude=float("{:.6f}".format(lng)),
                )

        return None

    def __init__(self, instance: BeautifulSoup) -> None:
        self.crawling_instance = instance

    def is_data_exists(self) -> bool:
        title = self.crawling_instance.find("h1").text
        return title and "Find Us" not in title

    def get_name(self) -> str:
        return self.crawling_instance.find("h1").text

    def get_coordinate(self) -> Coordinate | None:
        location_map_tag = self.crawling_instance.find(id="location-map")
        location_map_url = location_map_tag.find("img").get("src")
        return self._get_coordinate_from_url(location_map_url)

    def get_charger_data(self) -> List[Charger]:
        p_tags = self.crawling_instance.find(class_="vcard").find_all(
            "p", recursive=False
        )

        chargers = []
        texts = [str(s) for s in p_tags]
        for text in texts:
            if "충전" in text:
                # LOG
                with open("aaa.txt", "at") as f:
                    f.write(text + "\n")

                _arr = text.replace("<p>", "").replace("</p>", "").split("<br/>")
                for _e in _arr:
                    charger = self.get_charger_data_from_text(_e)
                    if charger is not None:
                        chargers.append(charger)

        return chargers


class ElementSuperchargerCollector(ElementCollector):
    CHARGER_TEXT_REGEX = re.compile(
        r"^최대 ([0-9]{1,})kW로 연중 무휴 이용 가능한 ([0-9]{1,}) 수퍼차저$"
    )


class ElementDestinationCollector(ElementCollector):
    CHARGER_TEXT_REGEX = re.compile(
        r"^최대 ([0-9]{1,})kW로 연중 무휴 이용 가능한 ([0-9]{1,}) Tesla 커넥터$"
    )
