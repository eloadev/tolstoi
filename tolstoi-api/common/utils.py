from urllib.request import urlopen

import requests
from lxml import etree, html


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def find_image(url, xpath_selector):
        """

        :param url: url of the page
        :param xpath_selector: xpath selector of the image
        :return: url of the image
        """
        response = urlopen(url)

        htmlparser = etree.HTMLParser()

        tree = etree.parse(response, htmlparser)

        element = tree.xpath(xpath_selector)[0]

        return element.get('src')

    @staticmethod
    def get_image_in_bytes(image_url):
        """
        :param image_url: url of the image
        :return: bytes of the image
        """

        response = requests.get(image_url)

        return response.content

    @staticmethod
    def get_bytes_from_image(image_path):
        """
        :param image_path: path of the image
        :return: bytes of the image
        """
        with open(image_path, 'rb') as image_file:
            return image_file.read()
