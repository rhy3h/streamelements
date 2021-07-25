from selenium import webdriver
from urllib.parse import unquote
import json


class SeleniumDriver:
    def __init__(self, authToken):
        chrome_options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get('https://www.twitch.tv/directory')
        if authToken != '':
            try:
                # add token for given websites
                self.driver.add_cookie({
                    'name': 'auth-token',
                    'value': authToken
                })
                self.driver.refresh()
            except Exception as e:
                # it'll fail for the first time, when cookie file is not present
                print(e)

    def get_cookies(self):
        # backup this cookie for next time login use
        token = self.driver.get_cookie('twilight-user')
        # parse necessary cookies
        necessary = json.loads(unquote(token['value']))
        return necessary

    def close_all(self):
        # close all open tabs
        if len(self.driver.window_handles) < 1:
            return
        for window_handle in self.driver.window_handles[:]:
            self.driver.switch_to.window(window_handle)
            self.driver.close()

    def get_and_quit(self):
        cookie = self.get_cookies()
        self.close_all()
        self.driver.quit()
        return cookie