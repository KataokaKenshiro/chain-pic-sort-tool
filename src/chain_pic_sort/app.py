"""アプリの起動処理。"""

import sys
import traceback
from types import TracebackType

from PySide6.QtWidgets import QApplication, QMessageBox

from chain_pic_sort.core.settings import AppSettings
from chain_pic_sort.ui.main_window import MainWindow


def show_unexpected_error(
    exc_type: type[BaseException], exc: BaseException, tb: TracebackType | None
) -> None:
    """想定外の例外をダイアログで知らせる（Windows の exe はコンソールが無く出力が見えない）。"""
    if sys.stderr is not None:  # PyInstaller のコンソール無し exe では None
        traceback.print_exception(exc_type, exc, tb)
    QMessageBox.critical(
        None, "エラー", f"予期しないエラーが発生しました。\n{exc_type.__name__}: {exc}"
    )


def main() -> int:
    app = QApplication(sys.argv)
    sys.excepthook = show_unexpected_error
    settings = AppSettings()
    window = MainWindow(settings)
    window.show()
    last = settings.last_folder
    if last is not None and last.is_dir():
        window.open_folder(last)
    return app.exec()
