"""scaffold smoke test — 実装テストが揃ったら削除する。"""

from PySide6.QtWidgets import QLabel

import chain_pic_sort


def test_package_imports() -> None:
    assert chain_pic_sort.__doc__


def test_qt_widget_runs_offscreen(qtbot) -> None:
    label = QLabel("ok")
    qtbot.addWidget(label)
    label.show()
    assert label.isVisible()
