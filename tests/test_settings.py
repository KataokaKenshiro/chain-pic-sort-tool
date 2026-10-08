from pathlib import Path

from PySide6.QtCore import QSettings

from chain_pic_sort.core.imaging import Rotation
from chain_pic_sort.core.settings import AppSettings


def ini_store(tmp_path: Path) -> QSettings:
    return QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)


def test_defaults_when_nothing_saved(tmp_path: Path) -> None:
    settings = AppSettings(ini_store(tmp_path))

    assert settings.rotation is Rotation.NONE
    assert settings.last_folder is None


def test_saved_values_survive_reopen(tmp_path: Path) -> None:
    settings = AppSettings(ini_store(tmp_path))
    settings.rotation = Rotation.LEFT
    settings.last_folder = tmp_path / "images"

    reopened = AppSettings(ini_store(tmp_path))

    assert reopened.rotation is Rotation.LEFT
    assert reopened.last_folder == tmp_path / "images"


def test_unknown_rotation_falls_back_to_none(tmp_path: Path) -> None:
    store = ini_store(tmp_path)
    store.setValue("rotation", "diagonal")

    assert AppSettings(store).rotation is Rotation.NONE
