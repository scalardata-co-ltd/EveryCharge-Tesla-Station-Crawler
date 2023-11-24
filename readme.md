# Tesla Station Crawler

테슬라 충전소 크롤러

**NOTE: 현재 chromedriver 작동이 되지 않습니다.**

## Installation + Run

* 파이썬 3.9버전을 사용하는 것을 권장합니다.

```shell
$ python -m venv venv venv
$ source venv/bin/activate
$ pip install upgrade --pip
$ pip install -r requirements.txt
$ python main.py
```

크롤링 결과는 ```result.json``` 에 저장됩니다.


## Architecture
```
tesla_crawer/
`-crawler.py
`-dawul_address.py
`-google_maps.py
`-juso_address.py
`-translator.py
main.py
```
* tesla_crawler: 크롤러 작동에 필요한 모든 모듈이 들어 있습니다.
  * crawler: 직접 크롤링을 작동시키는 모듈 입니다.
  * dawul_address: 다울에서 제공하는 주소찾기 서비스를 활용하는 모듈입니다. 좌표나 올바른 주소를 갖고올 때 사용합니다.
  * google_maps: 충전소의 좌포를 구하거나, 테슬라 웹에서 충전소 갯수를 가져오지 못할 때 대안으로 사용됩니다.
  * juso_address: 행정안전부에서 운영하는 도로명주소 서비스를 활용한 크롤러로, 정확한 주소명을 가져올 때 사용됩니다.
  * translator: 파파고를 크롤링해서 영어를 한국어로 전환할 때 사용합니다. 주소 또는 충전소명이 영어로 되어 있을 때 통역하기 위해 사용됩니다.

## Docs
* [테슬라 충전소 찾기 웹](https://www.tesla.com/ko_kr/findus?v=2&bounds=40.2904103810633%2C140.7727051941515%2C32.75308316424211%2C119.67895519415151&zoom=7&filters=supercharger%2Cdestination%20charger%2Cparty%2Cself%20serve%20demo%20drive)
* [개요(프로젝트 보드)](https://www.notion.so/6202f586cb0642a5a506181a183f61d2)
* [개발 로그](https://www.notion.so/673a844ce9ab48aca42489a400132766)