from selenium import webdriver
import json


class SeleniumDriver(object):
    def __init__(self):
        self.token_file_path = './token.json'
        chrome_options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.driver.implicitly_wait(5)
        try:
            # load token for given websites
            token = json.load(open(self.token_file_path, "r",
                                   encoding='utf-8'))
            self.driver.get('https://www.twitch.tv/directory')
            self.driver.add_cookie(token)
            self.driver.refresh()

        except Exception as e:
            # it'll fail for the first time, when cookie file is not present
            print(str(e))
            print("Error loading cookies")

    def save_cookies(self):
        # backup this cookie for next time login use
        token = self.driver.get_cookie('auth-token')
        # save with json type
        json.dump(token, open(self.token_file_path, "w", encoding='utf-8'))

    def close_all(self):
        # close all open tabs
        if len(self.driver.window_handles) < 1:
            return
        for window_handle in self.driver.window_handles[:]:
            self.driver.switch_to.window(window_handle)
            self.driver.close()

    def quit(self):
        self.save_cookies()
        self.close_all()
        self.driver.quit()