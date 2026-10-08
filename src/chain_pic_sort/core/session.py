"""1 フォルダ分の仕分け作業の状態（未仕分けの一覧と、表示中の位置）。"""

from pathlib import Path

from chain_pic_sort.core.metadata import load_metadata
from chain_pic_sort.core.mover import move_item
from chain_pic_sort.core.scanner import ImageItem, count_sorted, scan
from chain_pic_sort.core.sortlog import append_log


class LogWriteError(Exception):
    """移動はできたが sort_log.csv に書けなかった（Excel で開いている等）。"""


class SortSession:
    def __init__(self, folder: Path) -> None:
        self.folder = folder
        self.items: list[ImageItem] = []
        self.index = 0
        self.counts: dict[str, int] = {}
        self.reload()

    def reload(self) -> None:
        """フォルダを読み直す。表示位置はできるだけ保つ。"""
        self.items = scan(self.folder)
        self.counts = count_sorted(self.folder)
        self.index = min(self.index, max(len(self.items) - 1, 0))

    @property
    def current(self) -> ImageItem | None:
        return self.items[self.index] if self.items else None

    @property
    def remaining(self) -> int:
        return len(self.items)

    @property
    def total(self) -> int:
        return self.remaining + sum(self.counts.values())

    def next(self) -> bool:
        if self.index + 1 >= len(self.items):
            return False
        self.index += 1
        return True

    def prev(self) -> bool:
        if self.index == 0:
            return False
        self.index -= 1
        return True

    def sort_current(self, category: str) -> None:
        """表示中の画像を category へ移動し、ログに残して次の画像へ進む。

        移動に失敗したら MoveError（何も変わらない）。移動後のログ書き込みに失敗したら
        LogWriteError（移動は済んでいて次の画像へ進んでいる）。
        """
        item = self.current
        if item is None:
            return
        metadata = load_metadata(item.json)
        move_item(item, self.folder, category)
        del self.items[self.index]
        self.index = min(self.index, max(len(self.items) - 1, 0))
        self.counts[category] = self.counts.get(category, 0) + 1
        try:
            append_log(self.folder, item.jpg.name, category, metadata)
        except OSError as e:
            raise LogWriteError(f"sort_log.csv に書き込めませんでした: {e}") from e
