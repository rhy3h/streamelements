from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
from ui import Ui_MainWindow
import sys

import chromedriver_autoinstaller

from drive import SeleniumDriver


class MainWindow(QMainWindow, Ui_MainWindow):
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
        QMessageBox.information(self, "提示", "保存成功")

if __name__ == '__main__':
    # install chromium with correct version and add driver path to env
    chromedriver_autoinstaller.install(cwd=True)

    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
