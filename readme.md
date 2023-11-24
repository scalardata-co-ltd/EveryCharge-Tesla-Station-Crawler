# Tesla Station Crawler

테슬라 충전소 크롤러

**NOTE: 현재 chromedriver 작동이 되지 않습니다. 문제를 해결하는 대로 업데이트를 할 예정입니다.**

## Installation + Run

파이썬 3.9버전을 사용하는 것을 권장합니다.

```shell
$ python -m venv venv venv
$ source venv/bin/activate
$ pip install upgrade --pip
$ pip install -r requirements.txt
$ python main.py
```

크롤링 결과는 ```result.json``` 에 저장됩니다.