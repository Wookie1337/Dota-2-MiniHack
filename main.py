from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from config.logger import setup_logger
import sys

if __name__ == "__main__":
    logger = setup_logger()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    