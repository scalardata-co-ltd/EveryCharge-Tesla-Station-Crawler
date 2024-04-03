from typing import List
from bs4 import BeautifulSoup
import requests

from tsc.constants import TESLA_BASE_URL, USER_AGENT
from tsc.element_collector import (
    ElementDestinationCollector,
    ElementSuperchargerCollector,
)
from tsc.types import Charger, ChargerType, Station


class TeslaStationCrawler:
    list_urls = {
        ChargerType.SUPERCHARGER: "https://www.tesla.com/ko_kr/findus/list/superchargers/South+Korea",
        ChargerType.DESTINATION: "https://www.tesla.com/ko_kr/findus/list/chargers/South+Korea",
    }
    collectors = {
        ChargerType.SUPERCHARGER: ElementSuperchargerCollector,
        ChargerType.DESTINATION: ElementDestinationCollector,
    }

    def _get_html(self, charger_type: ChargerType) -> str:
        url: str = self.list_urls[charger_type]

        try:
            response = requests.get(url, headers={"user-agent": USER_AGENT}, timeout=10)
        except requests.ReadTimeout:
            print("Timeout Error")

        if response.status_code == 200:
            return response.text
        else:
            raise RuntimeError("HTML 요청에 실패했습니다.")

    @staticmethod
    def _get_station_detail_urls(html: str) -> List[str]:
        urls = []
        soup = BeautifulSoup(html, "html.parser")

        station_tags = soup.find_all("address")
        for station_tag in station_tags:
            detail_url_tag = station_tag.find("a")
            detail_url_suffix = detail_url_tag.get("href")
            detail_url = f"{TESLA_BASE_URL}{detail_url_suffix}"
            urls.append(detail_url)
        return urls

    def _get_station_from_html(
        self, html: str, charger_type: ChargerType
    ) -> Station | None:
        soup = BeautifulSoup(html, "html.parser")
        collector = self.collectors[charger_type](soup)

        if not collector.is_data_exists():
            return None

        name = collector.get_name()
        coordinate = collector.get_coordinate()
        chargers: List[Charger] = collector.get_charger_data()
        is_always = True  # 연중 무휴

        if len(chargers) == 0:
            match charger_type:
                case ChargerType.SUPERCHARGER:
                    chargers.append(Charger(charging_speed=100, charger_count=1))
                case ChargerType.DESTINATION:
                    chargers.append(Charger(charging_speed=7, charger_count=1))

        return Station(
            coordinate=coordinate,
            name=name,
            chargers=chargers,
            is_always=is_always,
            charger_type=charger_type,
        )

    def crawl(self, charger_type: ChargerType) -> List[Station]:
        stations = []
        html = self._get_html(charger_type)
        station_detail_urls = self._get_station_detail_urls(html)
        for i, url in enumerate(station_detail_urls):
            print(f"Crawling: {i+1}/{len(station_detail_urls)}")
            response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
            if response.status_code == 200:
                detail_html = response.text
                station = self._get_station_from_html(
                    detail_html,
                    charger_type,
                )
                if station:
                    print(station)
                    stations.append(station)
        return stations
