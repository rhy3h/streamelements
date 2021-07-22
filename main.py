from PyQt5 import QtWidgets, QtGui, QtCore
from ui import Ui_MainWindow
import sys

import chromedriver_autoinstaller

import pickle
from selenium import webdriver

class SeleniumDriver(object):
    def __init__(self):
        self.cookies_file_path = f'./twitch.pkl'
        self.cookies_websites = ["https://www.twitch.tv/directory"]
        chrome_options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(
            options=chrome_options
        )
        self.driver.maximize_window()
        self.driver.implicitly_wait(5)
        try:
            # load cookies for given websites
            cookies = pickle.load(open(self.cookies_file_path, "rb"))
            for website in self.cookies_websites:
                self.driver.get(website)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                self.driver.refresh()

        except Exception as e:
            # it'll fail for the first time, when cookie file is not present
            print(str(e))
            print("Error loading cookies")

    def save_cookies(self):
        # save cookies
        cookies = self.driver.get_cookies()
        pickle.dump(cookies, open(self.cookies_file_path, "wb"))

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

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.LoginButton.clicked.connect(self.login)
        self.ui.SaveButton.clicked.connect(self.save)

    def login(self):
        self.Selenium = SeleniumDriver()
        self.Selenium.driver.get("https://www.twitch.tv/directory")

    def save(self):
        self.Selenium.quit()

if __name__ == '__main__':
    chromedriver_autoinstaller.install(cwd=True)
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
