from tesla_crawler.crawler import TeslaStationCrawler
import json
import time

if __name__ == "__main__":
    start = time.time()
    crawler = TeslaStationCrawler()
    res = crawler.get_stations()

    print("time: " + str(time.time() - start))
    with open("result.json", "wt") as f:
        json_obj = json.dumps(res, indent=4, ensure_ascii=False)
        f.write(json_obj)
