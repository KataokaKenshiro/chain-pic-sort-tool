"""アプリの起動処理。"""

import sys

from PySide6.QtWidgets import QApplication

from chain_pic_sort.core.settings import AppSettings
from chain_pic_sort.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    settings = AppSettings()
    window = MainWindow(settings)
    window.show()
    last = settings.last_folder
    if last is not None and last.is_dir():
        window.open_folder(last)
    return app.exec()
