import sys
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

import database.database as database
from ui.login_window import LoginWindow


def main():
    # db
    database.init_database()

    app = QApplication(sys.argv)
    app.setApplicationName("LabTrack")
    app.setOrganizationName("LabTrack Systems")

    # global font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # login
    window = LoginWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
