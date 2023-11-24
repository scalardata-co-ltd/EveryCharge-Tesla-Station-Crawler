from tesla_crawler.juso_address import JusoAddressFinder
from tesla_crawler.translator import TranslatorCrawler
from tesla_crawler.crawler import TeslaStationCrawler

if __name__ == '__main__':
    """
    jdf = JusoAddressFinder()
    jdf.open_driver()

    jdf.action_search_address('고성군 두포 1길 삼산면 166-5', '52959')
    print(jdf.get_searched_address())

    jdf.close_driver()
    """
    
    tr = TranslatorCrawler()
    tr.open_driver()

    address = 'Goseong-gun Dupo 1-gil Samsan-myeon 166-5'

    splited_address = address.split()
    new_splited_address = []
    have_splited_words = []

    for word in splited_address:
        translated_word = word
        if TeslaStationCrawler.Regex.english_address_word.match(word) and \
                not TeslaStationCrawler.Regex.only_number_and_hipen.match(word):
            if word.lower() == 'seoul':
                translated_word = '서울특별시'
            elif word.lower() == 'seongnam':
                translated_word = '성남시'
            else:
                have_english_word = True
        new_splited_address.append(translated_word)
    address_name = ' '.join(new_splited_address)

    if have_english_word:
        address_name = tr.translate(address_name)
    print(address_name)
