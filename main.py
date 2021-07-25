import chromedriver_autoinstaller
from Controller import Controller
if __name__ == '__main__':
    # install chromium with correct version and add driver path to env
    chromedriver_autoinstaller.install(cwd=True)
    controller = Controller()
    controller.start()