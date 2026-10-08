"""仕分け対象の画像を列挙し、振り分け済みの件数を数える。"""

from dataclasses import dataclass
from pathlib import Path

CATEGORIES = ("OK", "NG", "SKIP", "END")


@dataclass(frozen=True)
class ImageItem:
    """仕分け対象の 1 組（jpg と、同じ名前の json があればそのパス）。"""

    jpg: Path
    json: Path | None


def _is_jpg(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() == ".jpg"


def scan(folder: Path) -> list[ImageItem]:
    """フォルダ直下の jpg をファイル名の昇順で返す（サブフォルダは見ない）。"""
    items = []
    for jpg in sorted((p for p in folder.iterdir() if _is_jpg(p)), key=lambda p: p.name):
        json = jpg.with_suffix(".json")
        items.append(ImageItem(jpg=jpg, json=json if json.is_file() else None))
    return items


def count_sorted(folder: Path) -> dict[str, int]:
    """各カテゴリフォルダにある jpg の枚数を返す（フォルダが無ければ 0）。"""
    counts = {}
    for category in CATEGORIES:
        sub = folder / category
        counts[category] = sum(1 for p in sub.iterdir() if _is_jpg(p)) if sub.is_dir() else 0
    return counts
