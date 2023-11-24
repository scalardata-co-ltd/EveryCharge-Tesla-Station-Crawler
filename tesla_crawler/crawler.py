import time
import re
from typing import List, Tuple, Dict, Optional

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    StaleElementReferenceException, 
    ElementNotInteractableException,
    NoSuchElementException)

from .google_maps import GoogleMapCrawlerForDestinationCharger
from .dawul_address import DawulAddressFinder
from .translator import TranslatorCrawler
from .juso_address import JusoAddressFinder


class TeslaStationCrawler:
    target_url: str
    korean_translator: TranslatorCrawler
    destination_finder: GoogleMapCrawlerForDestinationCharger
    dawul_address_finder: DawulAddressFinder
    juso_address_finder: JusoAddressFinder
    search_urls: List[str] = [
        'https://www.tesla.com/ko_kr/findus?v=2&bounds=39.110112646920825%2C129.6242396484375%2C37.513296134837034%2C125.47140761718752&zoom=9&filters=supercharger%2Cdestination%20charger%2Cparty',
        'https://www.tesla.com/ko_kr/findus?v=2&bounds=38.42700531281709%2C129.74349759375002%2C36.815096402772696%2C125.5906655625&zoom=9&filters=supercharger%2Cdestination%20charger%2Cparty',
        'https://www.tesla.com/ko_kr/findus?v=2&bounds=37.76976193944103%2C129.8773390625%2C36.14355549047675%2C125.72450703125&zoom=9&filters=supercharger%2Cdestination%20charger%2Cparty',
        'https://www.tesla.com/ko_kr/findus?v=2&bounds=37.23818332476419%2C130.08406157031249%2C35.600574576918525%2C125.93122953906249&zoom=9&filters=supercharger%2Cdestination%20charger%2Cparty',
        'https://www.tesla.com/ko_kr/findus?v=2&bounds=36.627951982555906%2C129.9995711328125%2C34.97743329711568%2C125.84673910156249&zoom=9&filters=supercharger%2Cdestination%20charger%2Cparty',
        'https://www.tesla.com/ko_kr/findus?v=2&bounds=35.85900840262777%2C129.7660826171875%2C34.192497338131574%2C125.6132505859375&zoom=9&filters=supercharger%2Cdestination%20charger%2Cparty',
        'https://www.tesla.com/ko_kr/findus?v=2&bounds=35.354508757678836%2C129.54539601562502%2C33.677673161810105%2C125.392563984375&zoom=9&filters=supercharger%2Cdestination%20charger%2Cparty',
        'https://www.tesla.com/ko_kr/findus?v=2&bounds=34.5779959615957%2C128.38359181640627%2C32.885531248426055%2C124.23075978515625&zoom=9&filters=supercharger%2Cdestination%20charger%2Cparty',
    ]
    address_unit = ('도', '시', '군', '구', '동', '읍', '면', '리', '로', '길', 'number')

    class Regex:
        supercharger = re.compile(r'^최대 [0-9]{1,}kW로 연중무휴 이용 가능한 [0-9]{1,} 수퍼차저$')
        destination = re.compile(r'^최대 [0-9]{1,}kW로 연중무휴 이용 가능한 [0-9]{1,} Tesla 커넥터$')
        kwh = re.compile(r'[0-9]{1,}kW')
        charger_count = re.compile(r' [0-9]{1,} ')
        english_address_word = re.compile(r'^[a-zA-Z0-9|-]{1,}$')
        only_number_and_hipen = re.compile(r'^[0-9|-]{1,}$')
        map_build_number = re.compile(r'^[0-9]{1,}[0-9|-]{0,}$')
        japanese = re.compile(r'([ぁ-ゔァ-ヴー々〆〤一-龥]){1,}')
        beongil = re.compile(r'^[0-9]{0,}번길$')

    def __init__(self):
        self.driver = None
        self.korean_translator = TranslatorCrawler()
        self.destination_finder = GoogleMapCrawlerForDestinationCharger()
        self.dawul_address_finder = DawulAddressFinder()
        self.juso_address_finder = JusoAddressFinder()

    def action_after_open_driver(self):
        # 우측 모달 없애기
        try:
            modal_exit_btn = self.driver.find_element(By.CLASS_NAME, 'tds-modal-close')
            modal_exit_btn.click()
            time.sleep(10)
        except (NoSuchElementException, ElementNotInteractableException):
            pass

        # 새로고침
        self.driver.refresh()
        self.driver.implicitly_wait(3)
        time.sleep(3)

        # Google Map 켜기
        self.destination_finder.open_driver()
        # 주소 위경도 찾는 크롤러 열기
        self.dawul_address_finder.open_driver()
        # 도로명, 지역명, 우편번호 구하는 크롤러 열기
        self.juso_address_finder.open_driver()
        # 구글 번역기 열기
        self.korean_translator.open_driver()

    def generate_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--window-size=1920,1080')
        options.add_experimental_option("detach", True)
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
        self.driver = driver

    def open_driver(self, url: str):
        self.generate_driver()
        self.driver.get(url)
        self.driver.implicitly_wait(10)
        self.action_after_open_driver()

    def close_driver(self):
        if self.driver:
            self.korean_translator.close_driver()
            self.dawul_address_finder.close_driver()
            self.destination_finder.close_driver()
            self.juso_address_finder.close_driver()
            self.driver.quit()
            self.driver = None

    def __del__(self):
        self.close_driver()

    def get_charger(self, charger_info_strings: List[str]) -> Dict:
        """
        충전소 내의 충전기 정보 가져오기
        """
        chargers, info = [], None
        
        for data in charger_info_strings:
            charger_data = {}

            if self.Regex.supercharger.search(data):
                charger_data['type'] = 'supercharger'
            elif self.Regex.destination.search(data):
                charger_data['type'] = 'destination'
            else:
                if data:
                    # 기타 정보 (고객 젼용, 공용 ...)
                    info = data
                    continue

            charger_data['max_kwh'] = \
                int(self.Regex.kwh.search(data)[0][:-2])
            charger_data['charger_count'] = \
                int(self.Regex.charger_count.search(data)[0][1:-1])
            chargers.append(charger_data)

        return {'chargers': chargers, 'info': info}
    
    def pre_process_before_modify(self, address: str):
        splited = address.split()
        wrong_road_regex = re.compile(r'^.{1,}로[0-9]{1,}$')
        for idx, word in enumerate(splited):
            if wrong_road_regex.match(word):
                splited[idx] += '길'
                break
        return  ' '.join(splited)

    def split_address(self, prev_address: str) -> Tuple[Dict, str]:
        """
        주소 단위가 뒤죽박죽된 주소를 바로잡기 위해
        문자열인 주소를 주소 단위로 나눈다
        """
        address_map = {unit: '' for unit in self.address_unit}
        address_words = prev_address.split()
        split_road_regex = re.compile(r'^(\w+)로(\d+)$')
        
        for word in address_words:
            if word in ('부산', '대구', '인천', '광주', '대전', '울산',
                        '부산시', '대구시', '인천시', '광주시', '대전시', '울산시'):
                word = word[:2] + '광역시'
            elif word == '서울' or word == '서울시':
                word =  '서울특별시'
            elif word == '세종' or word == '세종시':
                word += '세종특별자치시'
            elif word in ('강원', '강원특별자치도'):
                # 강원특별자치도는 2023년 6월 11일에 출범
                # 이전 명칭과 동기화 하기 위해 강원도로 변경
                word = '강원도'

            if word[-1] == '번':
                # x번 -> x번길
                word += '길'

            if word[-1] in address_map and address_map[word[-1]] == '':
                address_map[word[-1]] = word
            elif split_road_regex.match(word):
                # regex: XX로YY -> XX로 YY길
                # big road: XX로
                # small road: YY길
                big_road, small_road = word.split('로')
                address_map['로'] = big_road + '로'
                address_map['길'] = small_road + '길'
            elif address_map['number'] == '' and \
                self.Regex.map_build_number.match(word):
                # %d-%d, %d
                address_map['number'] = word

        address_type = ''
        if address_map['로'] or address_map['길']:
            # 도로명
            if self.Regex.beongil.match(address_map['길']):
                # x로 y번길 -> x로y번길
                address_map['길'] = address_map['로'] + address_map['길']
                address_map.pop('길')
            address_type = 'road'
        else:
            # 지역명
            address_type = 'local'
        return address_map, address_type

    def concat_address(
            self, splited_address: Dict[str, str], 
            region3: bool = False) -> Optional[str]:
        """
        split_address로 나뉘진 주소를 하나로 합치기
        """
        targets = []
        for key in self.address_unit:
            if region3 and key in ('리', '로', '길', 'number'):
                continue
            if splited_address.get(key):
                targets.append(splited_address[key])

        res =  ' '.join(targets)
        if not res or region3 and res[-1] not in ('동', '읍', '면'):
            return None
        return res

    def get_modified_address_by_juso(
            self, address: str, postal_code: str = ''
        ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        행정안전부에서 운영하는 도로명 서비스를 이용한 주소 데이터 정제
        """
        road_address, local_address, generated_postal_code = \
            self.juso_address_finder.search_address(address, postal_code)
        if not road_address:
            # 우편번호 없이 시도
            road_address, local_address, generated_postal_code = \
                self.juso_address_finder.search_address(address)
        if not road_address:
            # 건물 번호 없이 시도, 이때 지번은 갖고올 수 없다.
            road_address, local_address, generated_postal_code = \
                self.juso_address_finder.search_address(
                    ' '.join(address.split()[:-1]), postal_code)
            if road_address:
                road_address = ' '.join(road_address.split()[:-1]) + ' ' + address.split()[-1]
                local_address = None
                generated_postal_code = postal_code

        return road_address, local_address, generated_postal_code

    def get_modified_address_by_dawul(
            self, address: str) -> Tuple[Optional[str], Optional[str]]:
        """
        주소 데이터 정제
        """
        new_address1, new_address2 = \
            self.dawul_address_finder.get_modified_address(address)
        if not new_address1 and not new_address2:
            return None, None
        if not new_address1:
            new_address1 = new_address2

        splited_new_address1, new_address1_type = self.split_address(new_address1)
        splited_new_address2, new_address2_type = self.split_address(new_address2)

        # 지역명은 region3로 표현해야 한다.
        if (new_address1_type, new_address2_type) == ('road', 'local'):
            new_address = self.concat_address(splited_new_address1)
            region3_address = self.concat_address(splited_new_address2, True)
        elif (new_address1_type, new_address2_type) == ('local', 'road'):
            new_address = self.concat_address(splited_new_address2)
            region3_address = self.concat_address(splited_new_address1, True)
        elif new_address1_type == new_address2_type == 'local':
            new_address = self.concat_address(splited_new_address1)
            region3_address = self.concat_address(splited_new_address2, True)
        else:
            new_address = self.concat_address(splited_new_address1)
            region3_address = None

        return new_address, region3_address

    def translate_station_name(self, station_name: str) -> str:
        translated_name = station_name
        if all([ch.isascii() or ch == 'é' for ch in station_name]):
            translated_name = self.korean_translator.translate(station_name)
        return translated_name

    def translate_address_name(self, address_name: str) -> str:
        address_name = address_name.replace(',', '')
        splited_address = address_name.split()
        have_english_word = False

        for word in splited_address:
            if self.Regex.english_address_word.match(word) and \
                    not self.Regex.only_number_and_hipen.match(word):
                have_english_word = True
                break
        
        if have_english_word:
            address_name = \
                self.korean_translator.translate(address_name)
        return address_name

    def get_station_detail_element(self):
        """
        충전소 상세정보 카드 엘리먼트 가져오기
        """
        cards = self.driver.find_elements(By.CLASS_NAME, 'card')
        for card in cards:
            if card.get_attribute('class').split()[1] == 'card--desktop':
                station_detail_element = card
        return station_detail_element
    
    def collect_markers(self):
        """
        지도상의 마커 전부 가져오기
        """
        map_container = self.driver.find_element(By.CLASS_NAME, 'map') \
                            .find_element(By.CLASS_NAME, 'gm-style')

        table_e = None
        for element in map_container.find_elements(By.XPATH, ".//*"):
            if element.get_attribute('tabindex') == '0':
                table_e = element
                break

        parent_e = None
        for element in table_e.find_elements(By.XPATH, ".//*"):
            if element.get_attribute('style') == \
                'position: absolute; left: 0px; top: 0px; z-index: 106; width: 100%;':
                parent_e = element
                break

        childs = parent_e.find_elements(By.XPATH, ".//*")
        markers = []

        for child in childs:
            if child.get_attribute('tabindex') is not None:
                markers.append(child)
        return markers

    def get_detail(self):
        # 충전소 세부정보 가져오기
        res = {}
        card_element = self.get_station_detail_element()
        card_type = card_element.find_element(By.CLASS_NAME, 'card-header') \
                                .find_element(By.CLASS_NAME, 'card-type')
        station_status_class = card_type.find_element(By.TAG_NAME, 'span') \
                                        .get_attribute('class')
        if station_status_class == 'card-type_icon tsla-icon-star-ribbon':
            # 개장 전의 충전소
            return {}
        
        card_items = card_element.find_element(By.CLASS_NAME, 'card-body') \
                                    .find_elements(By.CLASS_NAME, 'card-item')
        for item in card_items:
            attr = item.get_attribute('class').split()[1].split('--')[1]
            
            if attr == 'name':
                if self.Regex.japanese.match(item.text):
                    # 일본 충전소는 검색하지 않음
                    return {}
                res['name'] = self.translate_station_name(item.text)

            elif attr == 'address':
                address = item.find_element(By.CLASS_NAME, 'card-item_content').text.split('\n')
                postal_code = '' if len(address) < 2 else address[1]

                print('=====')
                print(address[0])
                address = self.translate_address_name(address[0])
                print(address)
                print('=====')

                if postal_code:
                    if all([ch.isdigit() for ch in postal_code]):
                        postal_code = postal_code.zfill(5)
                    else:
                        postal_code = ''

                address = self.pre_process_before_modify(address)

                # 행정안전부에서 운영하는 도로명 서비스를 이용한 주소 데이터 정제
                road_address, local_address, generated_postal_code = \
                    self.get_modified_address_by_juso(address, postal_code)

                if generated_postal_code:
                    road_address = self.concat_address(self.split_address(road_address)[0])
                    res['address'] = {
                        'name': road_address,
                        'postal_code': postal_code,
                    }
                    if local_address:
                        res['address']['region3'] = \
                            self.concat_address(self.split_address(local_address)[0], True)
                    print('=========GET=========')
                else:
                    # 다올 주소명 서비스로 주소 데이터 정제
                    modified_address, _ = self.get_modified_address_by_dawul(address)
                    if modified_address:
                        address = modified_address
                    address = self.concat_address(self.split_address(address)[0])
                    res['address'] = {'name': address, 'postal_code': postal_code}

                    address, region3_address = \
                        self.get_modified_address_by_dawul(res['address']['name'])
                    if address:
                        res['address']['name'] = address
                    if region3_address:
                        res['address']['region3'] = region3_address

            elif attr == 'chargers':
                info_data = item.find_element(By.CLASS_NAME, 'card-item_content') \
                                .find_element(By.TAG_NAME, 'p').text.split('\n')
                res['charger'] = self.get_charger(info_data)
            
            elif attr == 'website':
                res['website'] = item.find_element(By.CLASS_NAME, 'card-item_content') \
                                        .find_element(By.TAG_NAME, 'a') \
                                        .get_attribute('href')
                    
            elif attr == 'phones':
                res['phone'] = item.find_element(By.CLASS_NAME, 'card-phone_number') \
                        .find_element(By.TAG_NAME, 'a').text
                
            elif attr == 'directions':
                res['latitude'], res['longitude'] = map(float, item.find_element(By.TAG_NAME, 'a') \
                            .get_attribute('href').split('=')[1].split(','))
        
            elif attr == 'ameneties-icon':
                facilities = []
                facility_elements = item \
                                    .find_element(By.CLASS_NAME, 'amenities-icons') \
                                    .find_elements(By.TAG_NAME, 'li')
                for facility_element in facility_elements:
                    facilities.append(facility_element.find_element(By.TAG_NAME, 'a').text)
                
                res['facilities'] = facilities
            
        if not res.get('address'):
            # 주소 없는 데이터는 검색하지 않음
            return {}
            
        if not res.get('latitude') and res['address'].get('name'):
            coord = self.dawul_address_finder \
                        .get_latitude_and_longitude(res['address']['name'])
            if not coord:
                # 위경도 갖고오기 실패
                print('===== Failed ======')
                print(res)
                print('===== ====== ======')
                return None

            res['latitude'], res['longitude'] = coord['latitude'], coord['longitude']

        if not res['charger']['chargers']:
            destination_data = self.destination_finder \
                .find_tesla_destinaiton_charger_data(res['address']['name'])
            if destination_data:
                res['charger']['chargers'].append(destination_data)
        print(res)
        return res
    
    def click_marker(self, marker):
        try:
            marker.send_keys(Keys.ENTER)
            self.driver.implicitly_wait(10)
        except (ElementNotInteractableException, 
                StaleElementReferenceException):
            try:
                # 실패시 재시도
                time.sleep(2)
                marker.send_keys(Keys.ENTER)
                self.driver.implicitly_wait(10)
            except (ElementNotInteractableException, 
                    StaleElementReferenceException):
                return False
            return True
        return True
    
    def sort_markers(self, markers):
        sorted_markers = []
        for marker in markers:
            sorted_markers.append({
                **marker.location,
                'element': marker,
            })
        sorted_markers.sort(key=lambda e: (e['y'], -e['x']))
        return sorted_markers
    
    def get_markers_for_crwaling(self, direction='left'):
        # 크롤링을 위해 화면상 전체 마커 중 해당 범위에 포함되는 마커만 가져오기
        _markers = self.sort_markers(self.collect_markers())
        markers = [_marker['element'] for _marker in _markers]
        selected_markers = []
        center_x, center_y = 737, 320

        for marker in markers:
            x, y = marker.location['x'], marker.location['y']
            if direction == 'right':
                if x - center_x >= 0 and y >= center_y:
                    selected_markers.append(marker)
            elif direction == 'left':
                if x - center_x <= 0 and y >= center_y:
                    selected_markers.append(marker)

        return selected_markers

    def get_stations_certain_area(self, direction='left'):
        stations_dict = {}
        markers = self.get_markers_for_crwaling(direction)

        for marker in markers:
            if not self.click_marker(marker):
                print('==================ERROR==================')
                continue
            time.sleep(2)
            station_data = {}
            try:
                station_data = self.get_detail()
            except StaleElementReferenceException:
                time.sleep(5)
                station_data = self.get_detail()

            if station_data:
                # 동일한 충전소 중복 검색을 피하기 위한 dictionary key
                dict_key = f'{station_data["name"]}-{station_data["address"]["name"]}'
                if dict_key not in stations_dict:
                    stations_dict[dict_key] = station_data
            self.driver.implicitly_wait(3)

        return stations_dict

    def get_stations(self):
        result_dict = {}
        try:
            for i, url in enumerate(self.search_urls):
                print(f'{i}/{len(self.search_urls)}')
                self.open_driver(url)
                time.sleep(1)
                result_dict.update(self.get_stations_certain_area('left'))
                self.close_driver()

                self.open_driver(url)
                time.sleep(1)
                result_dict.update(self.get_stations_certain_area('right'))
                self.close_driver()

            results = [data for data in result_dict.values()]
        except Exception as e:
            if self.driver:
                self.driver.quit()
            raise e
        else:
            return results
