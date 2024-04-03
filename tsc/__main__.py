from tsc.converter import to_csv
from tsc.crawler import TeslaStationCrawler
from tsc.types import ChargerType


if __name__ == "__main__":
    crawler = TeslaStationCrawler()

    print("START CRAWL SUPERCHARGER...")
    supercharger_stations = crawler.crawl(ChargerType.SUPERCHARGER)
    print("WRITE TO CSV FILE...")
    to_csv(supercharger_stations, "./supercharger.csv")
    print("CRAWLING SUPERCHARGER IS COMPLETED\n\n")

    print("START CRAWL DESTINATION...")
    supercharger_stations = crawler.crawl(ChargerType.DESTINATION)
    print("WRITE TO CSV FILE...")
    to_csv(supercharger_stations, "./destination.csv")
    print("CRAWLING DESTINATION IS COMPLETED")
