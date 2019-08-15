# -*- coding: utf-8 -*-
import scrapy
from parsel.selector import Selector
from scrapy.http.response.html import HtmlResponse
# import requests
# from PIL import Image
# import pytesseract
# import urllib

from scrapy.exceptions import CloseSpider


class AmazonbooksSpider(scrapy.Spider):
    name = 'amazonbooks'
    amazon_url = 'https://www.amazon.com'
    search_keyword = ''

    def start_requests(self):
        url = f'{self.amazon_url}/s?k={self.search_keyword}&i=stripbooks-intl-ship&ref=nb_sb_noss_2'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: scrapy.http.response.html.HtmlResponse):
        if self.detect_captcha(response):
            # print('captcha_detected')
            raise CloseSpider('captcha_detected')
            # pattern = self.solve_captcha(response)

        pages = response.selector.xpath(
            '//li[contains(@class,"a-last")]/preceding-sibling::li')

        last_page_number = pages[-1].xpath('.//a/text()').extract_first()
        if not last_page_number:
            last_page_number = pages[-1].xpath('text()').extract_first()
        currenr_page = response.selector.xpath(
            '//li[contains(@class,"a-selected")]/a/text()').extract_first()
        print('currenr_page', currenr_page, 'last_page_number',
              last_page_number)

        book_div_selector = '//div[@class="a-section a-spacing-medium"]'
        book_name_and_url_selector = './/a[@class="a-link-normal a-text-normal"]'
        book_rate_selector = './/span[@class="a-icon-alt"]'
        number_of_people_rating_book_selector = './/a/span[@class="a-size-base"]'
        final_price_selector = ('.//a[contains(text(),"Paperback")]/'
                                'parent::node()/following-sibling::div//'
                                'span[@data-a-size="l"]/'
                                'span[@class="a-offscreen"]/text()')
        book_div: Selector
        for book_div in response.selector.xpath(book_div_selector):
            book_title = book_div.xpath(book_name_and_url_selector +
                                        '/span/text()').extract_first()
            book_url = book_div.xpath(book_name_and_url_selector +
                                      '/@href').extract_first()
            book_rate = book_div.xpath(book_rate_selector +
                                       '/text()').extract_first()
            number_of_people_rating_book = book_div.xpath(
                number_of_people_rating_book_selector +
                '/text()').extract_first()
            final_price = book_div.xpath(final_price_selector).extract_first()
            meta = {
                'book_title': book_title,
                'book_rate': book_rate,
                'number_of_people_rating_book': number_of_people_rating_book,
                'final_price': final_price if final_price else '',
                'book_url': book_url
            }

            yield scrapy.Request(url=f'https://www.amazon.com{book_url}',
                                 callback=self.parse_book_details,
                                 meta=meta)
        next_page_url_selector = '//li[@class="a-last"]/a/@href'
        next_page_url = response.selector.xpath(
            next_page_url_selector).extract_first()
        if next_page_url:
            yield scrapy.Request(
                url=f'https://www.amazon.com{next_page_url}',
                callback=self.parse,
            )

    def detect_captcha(self, response):
        captcha_selector = response.selector.xpath(
            '//button[@type="submit"]').extract_first()
        return True if captcha_selector else False

    # def solve_captcha(self, response):
    #     image_url = response.selector.xpath('//div[@class="a-box"]')
    #     image_url = image_url.xpath('.//img/@src').extract_first()
    #     print(image_url)
    #     r = requests.get(image_url, stream=True)
    #     if r.status_code == 200:
    #         with open('detect_captcha.jpg', 'wb') as f:
    #             for chunk in r.iter_content(1024):
    #                 f.write(chunk)
    #     pattern = pytesseract.image_to_string(Image.open('detect_captcha.jpg'))
    #     args = {}
    #     for hidden_field in response.selector.xpath('//input[@type="hidden"]'):
    #         name = hidden_field.xpath('@name').extract_first()
    #         value = hidden_field.xpath('@value').extract_first()
    #         args[name] = value
    #     args['field-keywords'] = pattern
    #     print('args', args)
    #     url = self.amazon_url + '/errors/validateCaptcha?' + urllib.parse.urlencode(
    #         args)
    #     print('url', url)

    def parse_book_details(self, response: HtmlResponse):
        self.detect_captcha(response)
        publisher_name_and_date_selector = (
            '//b[contains(text(),"Publisher")]/parent::node()/text()')
        number_of_pages_selector = ('//li[contains(text(),"pages")]/text()')

        publisher_name_and_date = response.selector.xpath(
            publisher_name_and_date_selector).extract_first()
        number_of_pages_first = response.selector.xpath(
            number_of_pages_selector).extract_first()
        # if not number_of_pages_first:
        #     print('aakklklaa', response.text)
        response.meta.pop('depth', None)
        response.meta.pop('download_timeout', None)
        response.meta.pop('download_slot', None)
        response.meta.pop('download_latency', None)
        yield {
            **response.meta, 'publisher_name_and_date':
            publisher_name_and_date if publisher_name_and_date else '',
            'number_of_pages':
            number_of_pages_first
        }
