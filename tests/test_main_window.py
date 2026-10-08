import json
from pathlib import Path

import pytest
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QColor, QImage

from chain_pic_sort.core.imaging import Rotation
from chain_pic_sort.core.settings import AppSettings
from chain_pic_sort.ui.main_window import MainWindow


def make_jpg(path: Path, width: int = 2048, height: int = 1200) -> None:
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(QColor(80, 80, 80))
    assert image.save(str(path))  # 形式は拡張子から決まる


def make_pair(folder: Path, stem: str, meta: dict | None = None) -> None:
    make_jpg(folder / f"{stem}.jpg")
    if meta is not None:
        (folder / f"{stem}.json").write_text(json.dumps(meta), encoding="utf-8")


@pytest.fixture
def settings(tmp_path: Path) -> AppSettings:
    return AppSettings(QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat))


@pytest.fixture
def images(tmp_path: Path) -> Path:
    folder = tmp_path / "images"
    folder.mkdir()
    make_pair(folder, "a", {"verdict": "OK", "confidence": 0.99268, "mahalanobis": 310.2276})
    make_pair(folder, "b")
    return folder


@pytest.fixture
def window(qtbot, settings: AppSettings) -> MainWindow:
    window = MainWindow(settings)
    qtbot.addWidget(window)
    return window


def scene_size(window: MainWindow) -> tuple[float, float]:
    rect = window.view.sceneRect()
    return rect.width(), rect.height()


def test_open_folder_shows_first_image_with_counts_and_metadata(
    window: MainWindow, images: Path, settings: AppSettings
) -> None:
    window.open_folder(images)

    assert window.file_label.text() == "a.jpg"
    assert window.position_label.text() == "1 / 2"
    assert window.count_labels["合計"].text() == "2"
    assert window.count_labels["残り"].text() == "2"
    assert window.meta_labels["verdict"].text() == "OK"
    assert window.meta_labels["confidence"].text() == "0.9927"
    assert window.meta_labels["mahalanobis"].text() == "310.2"
    assert scene_size(window) == (1200, 1200)
    assert settings.last_folder == images


def test_missing_json_shows_none(window: MainWindow, images: Path) -> None:
    window.open_folder(images)
    assert window.session is not None
    window.session.next()
    window.show_current()

    assert window.file_label.text() == "b.jpg"
    assert window.meta_labels["verdict"].text() == "なし"


def test_rotation_menu_saves_setting(
    window: MainWindow, images: Path, settings: AppSettings
) -> None:
    make_jpg(images / "a.jpg", 2048, 800)  # 縦が 1200 未満なら回転で縦横が入れ替わる
    window.open_folder(images)
    assert scene_size(window) == (1200, 800)

    window.rotation_actions[Rotation.LEFT].trigger()

    assert settings.rotation is Rotation.LEFT
    assert scene_size(window) == (800, 1200)


def test_empty_folder_shows_nothing(window: MainWindow, tmp_path: Path) -> None:
    window.open_folder(tmp_path)

    assert window.file_label.text() == "なし"
    assert not window.view.has_image()


@pytest.fixture
def messages(window: MainWindow, monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """警告・完了ダイアログ（モーダル）を出さずに記録する。"""
    shown: list[str] = []
    monkeypatch.setattr(window, "warn", lambda text: shown.append(f"warn:{text}"))
    monkeypatch.setattr(window, "info", lambda text: shown.append(f"info:{text}"))
    return shown


@pytest.fixture
def active(qtbot, window: MainWindow) -> MainWindow:
    window.show()
    qtbot.waitExposed(window)
    window.activateWindow()
    qtbot.waitUntil(window.isActiveWindow)
    return window


def test_number_key_sorts_and_shows_next(
    qtbot, active: MainWindow, images: Path, messages: list[str]
) -> None:
    active.open_folder(images)

    qtbot.keyClick(active, Qt.Key.Key_2)

    assert sorted(p.name for p in (images / "NG").iterdir()) == ["a.jpg", "a.json"]
    assert active.file_label.text() == "b.jpg"
    assert active.count_labels["NG"].text() == "1"
    assert active.count_labels["残り"].text() == "1"
    assert active.count_labels["合計"].text() == "2"
    assert messages == []


def test_keys_work_while_a_button_has_focus(
    qtbot, active: MainWindow, images: Path, messages: list[str]
) -> None:
    active.open_folder(images)
    active.open_button.setFocus()
    qtbot.waitUntil(active.open_button.hasFocus)

    qtbot.keyClick(active.open_button, Qt.Key.Key_Right)
    assert active.file_label.text() == "b.jpg"

    qtbot.keyClick(active.open_button, Qt.Key.Key_4)
    assert (images / "END" / "b.jpg").exists()


def test_buttons_sort_and_end_does_not_close(
    qtbot, active: MainWindow, images: Path, messages: list[str]
) -> None:
    active.open_folder(images)

    qtbot.mouseClick(active.buttons["END"], Qt.MouseButton.LeftButton)
    qtbot.mouseClick(active.buttons["SKIP"], Qt.MouseButton.LeftButton)

    assert (images / "END" / "a.jpg").exists()
    assert (images / "SKIP" / "b.jpg").exists()
    assert active.isVisible()
    assert messages == ["info:すべての画像を振り分けました。"]


def test_arrow_keys_stop_at_ends(qtbot, active: MainWindow, images: Path) -> None:
    active.open_folder(images)

    qtbot.keyClick(active, Qt.Key.Key_Left)
    assert active.file_label.text() == "a.jpg"
    qtbot.keyClick(active, Qt.Key.Key_Right)
    qtbot.keyClick(active, Qt.Key.Key_Right)
    assert active.file_label.text() == "b.jpg"
    assert active.position_label.text() == "2 / 2"


def test_destination_conflict_warns_and_keeps_image(
    qtbot, active: MainWindow, images: Path, messages: list[str]
) -> None:
    (images / "OK").mkdir()
    (images / "OK" / "a.jpg").write_bytes(b"old")
    active.open_folder(images)

    qtbot.keyClick(active, Qt.Key.Key_1)

    assert (images / "a.jpg").exists()
    assert active.file_label.text() == "a.jpg"
    assert len(messages) == 1 and messages[0].startswith("warn:")
