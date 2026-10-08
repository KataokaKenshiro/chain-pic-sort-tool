import json
from pathlib import Path

import pytest
from PySide6.QtCore import QSettings
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
