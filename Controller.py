import os
import sys
import json
import asyncio
import threading
from PyQt5.QtGui import QStandardItemModel, QStandardItem
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
        if os.path.exists(Controller.config_path):
            with open(Controller.config_path, 'r', encoding='utf-8') as config:
                try:
                    self.config = json.load(config)
                except:
                    self.config = {}
        else:
            self.config = {}
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
        self.ui.watchBtn.clicked.connect(self.afk)

    def newChannelItem(text: str):
        'Create new checkable item'
        item = QStandardItem(text)
        return item

    def login(self):
        'Open chromium for login use, change button method and text'
        if 'auth-token' in self.config:
            token = self.config['auth-token']
        else:
            token = ''
        self.Selenium = SeleniumDriver(token)
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
        self.saveList()

    def delItem(self):
        'Delete channel from list'
        idxs = self.ui.channelListView.selectedIndexes()
        if len(idxs) != 0:
            reply = QMessageBox.warning(self.window, '警告', "確定刪除選定項目?",
                                        QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.No)
            if reply == QMessageBox.Yes:
                offset = 0
                for idx in idxs:
                    row = idx.row()
                    self.listModel.takeRow(row - offset)
                    offset += 1
                self.saveList()

    def saveList(self):
        'Save channel to list'
        self.config['channel'] = []
        for i in range(self.listModel.rowCount()):
            item = self.listModel.item(i, 0)
            self.config['channel'].append(item.text())
        self.saveConfig()

    def afk(self):
        'Afk list channel chatroom'
        # check if has token can afk
        if ('nickname' in self.config) and ('auth-token' in self.config):
            self.chatrooms = []
            self.loop = asyncio.get_event_loop()
            for channel in self.config['channel']:
                room = Chatroom(self.config['auth-token'],
                                self.config['nickname'], channel)
                room.afk_task = self.loop.create_task(room.connect_chatroom())
                self.chatrooms.append(room)
            self.thread = threading.Thread(target=self.loop.run_forever)
            self.thread.start()
            self.ui.watchBtn.clicked.connect(self.outOfRoom)
            self.ui.watchBtn.clicked.disconnect(self.afk)
            self.ui.watchBtn.setText("結束掛台")
        else:
            QMessageBox.warning(self.window, "警告", "未登入twitch，請先登入")

    def outOfRoom(self):
        reply = QMessageBox.question(self.window, '警告', "確定結束掛台?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes and hasattr(self, 'loop'):
            self.loop.stop()
            delattr(self, 'loop')
            self.thread.join()
            delattr(self, 'thread')
            self.ui.watchBtn.clicked.connect(self.afk)
            self.ui.watchBtn.clicked.disconnect(self.outOfRoom)
            self.ui.watchBtn.setText("開始掛台")

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