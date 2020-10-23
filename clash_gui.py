import sys

from PySide2.QtCore import QSize, Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QDialog, QSystemTrayIcon
from PySide2.QtWidgets import QToolButton, QMenu, QVBoxLayout, QHBoxLayout, \
    QTextBrowser, QSizePolicy, QMessageBox, QWidget, QAction

from clash import is_clash_running, ClashMediator
from utils import is_running_as_admin, clash_gui_config

clash_started = False
clash = ClashMediator()


class ClashTrayIcon(QSystemTrayIcon):

    # noinspection PyTypeChecker
    def __init__(self, icon, parent=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        self.start_item: QAction = None
        self.stop_item: QAction = None

        self.setToolTip("Simple Clash vpn GUI")
        self.create_menu(parent)

    def create_menu(self, parent):
        menu = QMenu(parent)

        open_window = menu.addAction("Open")
        # connect

        menu.addSeparator()

        start_item = menu.addAction("Start")
        start_item.setIcon(QIcon("images/start.svg"))
        start_item.setDisabled(clash_started)
        start_item.triggered.connect(self.start_clash)
        self.start_item = start_item

        stop_item = menu.addAction("Stop")
        stop_item.setIcon(QIcon("images/stop.svg"))
        stop_item.setDisabled(not clash_started)
        stop_item.triggered.connect(self.stop_clash)
        self.stop_item = stop_item

        menu.addSeparator()

        exit_item = menu.addAction("Exit")
        exit_item.triggered.connect(self.exit_clash)

        self.setContextMenu(menu)

    def start_clash(self):
        global clash
        global clash_started

        if is_clash_running():
            self.clash_message("Another instance of clash is already running. Terminate it to avoid conflicts")
        else:
            clash_started = True
            self.start_item.setDisabled(True)
            self.stop_item.setDisabled(False)
            self.setIcon(QIcon("images/clash-on.png"))
            clash.start(output_callback=self.clash_output, end_callback=self.clash_ended)
            self.clash_message("Clash started...")

    def stop_clash(self):
        global clash
        global clash_started
        clash_started = False

        self.setIcon(QIcon("images/clash-off.png"))
        self.start_item.setDisabled(False)
        self.stop_item.setDisabled(True)
        clash.kill()
        self.clash_message("Clash stopped")

    def clash_output(self, output):
        print(output)

    def clash_ended(self, return_code):
        print("clash ended with return code {}".format(return_code))

    def exit_clash(self):
        global clash
        clash.kill()
        exit(0)

    def clash_message(self, message):
        self.showMessage("clash-gui",
                         message,
                         QSystemTrayIcon.MessageIcon.NoIcon,
                         5000)


class ClashGUI(QDialog):

    def __init__(self, parent=None):
        super(ClashGUI, self).__init__(parent)
        self._clash: ClashMediator = None
        self.setWindowTitle("Clash GUI")
        self.setup_ui(parent)

    def setup_ui(self, parent):
        global clash_started

        self._height = 400
        self._width = 500
        self.resize(self._width, self._height)
        self.setMinimumSize(self._width, self._height)

        layout = QHBoxLayout(parent)
        controls = QVBoxLayout(parent)
        controls.setAlignment(Qt.AlignTop)
        controls.setSizeConstraint(QVBoxLayout.SetMinimumSize)

        start = QToolButton(parent)
        start.setIcon(QIcon("images/start.svg"))
        start.setToolTip("start clash")
        start.setIconSize(QSize(30, 30))
        start.clicked.connect(self.start)
        start.setFixedSize(50, 50)
        start.setDisabled(clash_started)
        controls.addWidget(start)

        stop = QToolButton(parent)
        stop.setIcon(QIcon("images/stop.svg"))
        stop.setToolTip("stop clash")
        stop.setIconSize(QSize(30, 30))
        stop.clicked.connect(self.stop)
        stop.setDisabled(not clash_started)
        stop.setFixedSize(50, 50)
        controls.addWidget(stop)

        layout.addLayout(controls)
        self._output = QTextBrowser(parent)
        self._output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self._output)

        for i in range(0, 100):
            self._output.append("current index is {}".format(i) * 5)

        self.setLayout(layout)

    def start(self):
        global clash_started
        if not clash_started:
            if is_clash_running():
                print("an instance of clash is already running")
                msg = QMessageBox(
                    QMessageBox.Icon.Warning,
                    "Clash is already running",
                    "Please kill other running clash instane(s) to avoid conflict",
                    QMessageBox.Ok,
                    parent=self
                )
                msg.exec_()
            else:
                # start clash (what if it is running?)
                if self._clash:
                    pass

    def clash_output(self, output):
        pass

    def stop(self):
        pass


def main():
    app = QApplication(sys.argv)
    # The default behaviour in Qt is to close an application once all the active windows have closed.
    # This won't affect this toy example, but will be an issue in application
    # where you do create windows and then close them.
    # Setting `app.setQuitOnLastWindowClosed(False)` stops this and
    # will ensure your application keeps running.
    app.setQuitOnLastWindowClosed(False)  # important

    widget = QWidget()
    icon = QIcon("images/clash-off.png")
    tray = ClashTrayIcon(icon=icon, parent=widget)
    tray.show()

    # clash = ClashGUI(widget)
    # clash.show()

    exit(app.exec_())


if __name__ == "__main__":
    if is_running_as_admin():
        print("Please run clash gui without elevated privileges.")
    else:
        from PySide2.QtCore import QLockFile

        lock_file = QLockFile("{}/multi_instance.lock".format(clash_gui_config()))
        if lock_file.tryLock(timeout=500):
            main()
        else:
            print("Another instance of clash-gui is already running.")
