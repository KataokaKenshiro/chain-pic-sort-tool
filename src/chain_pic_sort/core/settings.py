"""回転方向と最後に開いたフォルダを保存・読込する。

保存場所は QSettings に任せる（Windows はレジストリ、Linux は ~/.config/chain-pic-sort/）。
"""

from pathlib import Path

from PySide6.QtCore import QSettings

from chain_pic_sort.core.imaging import Rotation

ORGANIZATION = "chain-pic-sort"
APPLICATION = "chain-pic-sort"


class AppSettings:
    def __init__(self, store: QSettings | None = None) -> None:
        self._store = store if store is not None else QSettings(ORGANIZATION, APPLICATION)

    @property
    def rotation(self) -> Rotation:
        try:
            return Rotation(str(self._store.value("rotation", Rotation.NONE.value)))
        except ValueError:
            return Rotation.NONE

    @rotation.setter
    def rotation(self, value: Rotation) -> None:
        self._store.setValue("rotation", value.value)
        self._store.sync()

    @property
    def last_folder(self) -> Path | None:
        value = self._store.value("last_folder", "")
        return Path(str(value)) if value else None

    @last_folder.setter
    def last_folder(self, value: Path) -> None:
        self._store.setValue("last_folder", str(value))
        self._store.sync()
