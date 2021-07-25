import sys
import json
import asyncio
import threading
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QVariant, Qt
from PyQt5.QtWidgets import QApplication, QInputDialog, QMainWindow, QMessageBox
from ui import Ui_MainWindow
from driver import SeleniumDriver
from Chatroom import Chatroom


class MyWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def closeEvent(self, event) -> None:
        reply = QMessageBox.question(self, '警告', "是否要退出程式",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.controller.exit()
            event.accept()
        else:
            event.ignore()


class Controller:
    config_path = './config.json'

    def __init__(self):
        # load config json
        with open(Controller.config_path, 'r', encoding='utf-8') as config:
            self.config = json.load(config)
        # init ui
        self.ui_init()
        # init chatrooms
        self.chatrooms = []

    def ui_init(self):
        self.app = QApplication([])
        self.ui = Ui_MainWindow()
        self.window = MyWindow(self)
        self.ui.setupUi(self.window)
        # set stylesheet
        with open('dark.css') as cssfile:
            self.window.setStyleSheet(cssfile.read())

        # set chatroom list
        self.listModel = QStandardItemModel()
        self.ui.channelListView.setModel(self.listModel)
        # set channel list from config file
        if 'channel' in self.config:
            for channel in self.config['channel']:
                self.listModel.appendRow(Controller.newChannelItem(channel))

        # binding button event
        self.ui.loginBtn.clicked.connect(self.login)
        self.ui.addBtn.clicked.connect(self.addItem)
        self.ui.delBtn.clicked.connect(self.delItem)
        self.ui.saveListBtn.clicked.connect(self.saveList)
        self.ui.watchBtn.clicked.connect(self.afk)

    def newChannelItem(text: str):
        'Create new checkable item'
        item = QStandardItem(text)
        item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item.setData(QVariant(Qt.CheckState.Unchecked),
                     Qt.ItemDataRole.CheckStateRole)
        return item

    def login(self):
        'Open chromium for login use, change button method and text'
        self.Selenium = SeleniumDriver(self.config['auth-token'])
        self.ui.loginBtn.clicked.disconnect(self.login)
        self.ui.loginBtn.clicked.connect(self.saveCookie)
        self.ui.loginBtn.setText("保存cookie")

    def saveCookie(self):
        'Save chromium twitch cookie'
        if not self.Selenium is None:
            cookie = self.Selenium.get_and_quit()
            # save with json type
            self.config['auth-token'] = cookie['authToken']
            self.config['nickname'] = cookie['login']
            self.saveConfig()
            QMessageBox.information(self.window, "提示", "保存成功")

    def addItem(self):
        'Add channel list item'
        channel, okPressed = QInputDialog.getText(self.window, "新增", "要掛的台的ID")
        if okPressed:
            self.listModel.appendRow(Controller.newChannelItem(channel))

    def delItem(self):
        'Delete channel from list'
        cnt = self.listModel.rowCount()
        i = 0
        while i < cnt:
            item = self.listModel.item(i, 0)
            if item.checkState() == 2:
                self.listModel.takeRow(i)
                cnt -= 1
            else:
                i += 1

    def saveList(self):
        'Save channel to list'
        self.config['channel'] = []
        for i in range(self.listModel.rowCount()):
            item = self.listModel.item(i, 0)
            self.config['channel'].append(item.text())
        self.saveConfig()

    def afk(self):
        'Afk chatroom method'
        self.chatrooms = []
        self.loop = asyncio.get_event_loop()
        for i in range(self.listModel.rowCount()):
            item = self.listModel.item(i, 0)
            room = Chatroom(self.config['auth-token'], self.config['nickname'],
                            item.text())
            room.afk_task = self.loop.create_task(room.connect_chatroom())
            self.chatrooms.append(room)
        self.thread = threading.Thread(target=self.loop.run_forever)
        self.thread.start()

    def saveConfig(self):
        'Save all config to config.json'
        with open(Controller.config_path, 'w', encoding='utf-8') as config:
            json.dump(self.config, config)

    def start(self):
        self.window.show()
        sys.exit(self.app.exec_())

    def exit(self):
        if hasattr(self, 'loop'):
            self.loop.stop()