import os
import pdb
import random
import re
import sys
from time import sleep, time

import requests

import speech_recognition as sr
from pydub import AudioSegment

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium_stealth import stealth

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), './../..')))
from common import CONST as CONST


class ReCaptchaV2AudioSolver:
    def __init__(self):
        self.driver = None

    def solve(self, url, sitekey):
        captcha_response = ''

        try:
            print('Instantiating driver...')
            self.instantiate_driver()
            wait = WebDriverWait(self.driver, 10)

            print('Getting url...')
            self.driver.get(url)

            sleep(1)
            print('Finding recaptcha div...')
            recaptcha_div = wait.until(
                EC.presence_of_element_located((
                    By.XPATH, f"//*[contains(@data-sitekey, '{sitekey}')]"
                ))
            )
            print('Found recaptcha div, now finding frame and switching...')
            recaptcha_iframe = recaptcha_div.find_element(By.TAG_NAME, "iframe")

            self.driver.switch_to.frame(recaptcha_iframe)
            sleep(2)
            print('Switched to frame, now finding checkbox and clicking it...')
            self.click_checkbox()
            sleep(2)
            self.driver.switch_to.default_content()

            print('Clicked checkbox, now checking if checkbox is checked...')
            if self.is_checked():
                print('Checkbox is checked, now getting captcha response...')
                return self.get_recaptcha_response()

            print('Checkbox is not checked, now clicking audio button...')
            self.click_audio_button()

            attempts = 3
            while attempts:
                attempts -= 1

                print('Clicked audio button, now getting audio link...')
                link = self.get_audio_link()

                print('Got audio link, now downloading audio...')
                mp3_audio_path = self.download_audio(link)
                print('Downloaded audio, now converting to wav...')
                wav_audio_path = self.convert_to_wav(mp3_audio_path)
                print('Converted to wav, now getting text from audio...')
                text = self.speech_to_text(wav_audio_path)

                print('Got text from audio, now typing text...')
                self.type_text(text)

                print('Typed text, now removing mp3 and wav file...')
                self.remove_files(CONST.AUDIO_DOWNLOADS_FOLDER, '.mp3')
                self.remove_files(CONST.AUDIO_DOWNLOADS_FOLDER, '.wav')

                print('Removed wav file, now checking if checkbox is checked...')
                checked = self.is_checked()

                if checked or not attempts:
                    print('Checkbox is checked, now getting captcha response...')
                    captcha_response = self.get_recaptcha_response()
                    print('Got captcha response, now breaking...')
                    break
        except Exception as e:
            raise e

        print(f"Returning response {captcha_response}...")
        return captcha_response

    def instantiate_driver(self):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0'
        ]

        user_agent = random.choice(user_agents)

        options = webdriver.ChromeOptions()

        options.add_argument('user-agent={}'.format(user_agent))
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-gpu')
        options.add_argument('window-size=1146,671')
        options.add_argument("start-maximized")
        options.add_argument("headless")
        options.add_argument("no-sandbox")
        options.add_argument("disable-dev-shm-usage")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-application-cache")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        options.add_argument("--dns-prefetch-disable")
        options.add_argument("--disable-features=site-per-process")

        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(options=options)

        stealth(
            self.driver,
            languages=['en-US', 'en'],
            vendor='Google Inc.',
            platform='Win32',
            webgl_vendor='Intel Inc.',
            renderer='Intel Iris OpenGL Engine',
            fix_hairline=True,
        )

        self.driver.execute_script('Object.defineProperty(navigator, \'webdriver\', {get: () => undefined})')
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {'userAgent': f"{user_agent}"})

    def click_checkbox(self):
        wait = WebDriverWait(self.driver, 10)

        check_box = wait.until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR, "#recaptcha-anchor"
            ))
        )
        check_box.click()

    def is_checked(self):
        wait = WebDriverWait(self.driver, 10)
        dr = self.driver

        sleep(3)
        dr.switch_to.frame(
            wait.until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, 'iframe[name^=a]'
                ))
            )
        )

        try:
            dr.find_element(By.CSS_SELECTOR, '.recaptcha-checkbox-checked')
            dr.switch_to.default_content()
            return True
        except:
            dr.switch_to.default_content()
            return False

    def get_recaptcha_response(self):
        wait = WebDriverWait(self.driver, 10)
        captcha_response = wait.until(
            EC.presence_of_element_located((
                By.ID, "g-recaptcha-response"
            ))
        ).get_attribute('value')

        return captcha_response

    def click_audio_button(self):
        dr = self.driver
        dr.switch_to.frame(
            dr.find_element(By.XPATH, "//*[contains(@src, 'https://www.google.com/recaptcha/api2/bframe')]"))
        audio_btn = WebDriverWait(dr, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#recaptcha-audio-button")))
        audio_btn.click()
        dr.switch_to.default_content()

    def get_audio_link(self):
        dr = self.driver
        voice = dr.find_element(By.XPATH, "//*[contains(@src, 'https://www.google.com/recaptcha/"
                                          "api2/bframe')]")

        dr.switch_to.frame(voice)
        download_button = WebDriverWait(dr, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".rc-audiochallenge-tdownload-link")))
        link = download_button.get_attribute('href')
        dr.switch_to.default_content()

        return link

    def download_audio(self, link: str) -> str:
        """
        Downloads audio and returns file path
        """
        file_name = f'{int(time())}_{random.randint(10000, 99999)}.mp3'
        file_path = os.path.abspath(os.path.join(CONST.AUDIO_DOWNLOADS_FOLDER, file_name))
        os.makedirs(CONST.AUDIO_DOWNLOADS_FOLDER, exist_ok=True)

        response = requests.get(link)
        open(file_path, 'wb').write(response.content)
        return file_path

    def convert_to_wav(self, file_path: str) -> str:
        """
        Converts audio to wav and returns file path
        """
        wav_file_path = re.sub(r'\.mp3$', '.wav', file_path)
        os.path.isfile(file_path)
        AudioSegment.from_mp3(file_path).export(wav_file_path, format='wav')

        return wav_file_path

    def speech_to_text(self, audio_path: str) -> str:
        r = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = r.record(source)

        return r.recognize_sphinx(audio)

    def type_text(self, text):
        dr = self.driver
        wait = WebDriverWait(self.driver, 10)

        voice = dr.find_element(By.XPATH, "//*[contains(@src, 'https://www.google.com/recaptcha/"
                                          "api2/bframe')]")
        dr.switch_to.frame(voice)

        text_field = wait.until(
            EC.presence_of_element_located((
                By.ID, "audio-response"
            ))
        )
        text_field.send_keys(text, Keys.ENTER)
        dr.switch_to.default_content()

    def remove_files(self, directory, extension, exclude=[]):
        for filename in os.listdir(directory):
            if filename.endswith(extension) and filename not in exclude:
                file_path = os.path.join(directory, filename)
                os.remove(file_path)
