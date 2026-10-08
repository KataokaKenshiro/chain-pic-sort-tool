"""jpg と json をまとめてカテゴリフォルダへ移動する。"""

import shutil
from pathlib import Path

from chain_pic_sort.core.scanner import CATEGORIES, ImageItem


class MoveError(Exception):
    """移動できなかった（ファイルは元の場所に残っている）。"""


class SourceMissingError(MoveError):
    """移動元の jpg が見つからない（ツールの外で動かされた等）。"""


class DestinationExistsError(MoveError):
    """移動先に同じ名前のファイルがある。"""


def move_item(item: ImageItem, folder: Path, category: str) -> Path:
    """item を folder/category/ へ移動し、移動先の jpg のパスを返す。

    移動先に同名ファイルがあれば何も動かさない。json の移動に失敗したら jpg を元に戻し、
    片方だけ移動した状態を残さない。
    """
    if category not in CATEGORIES:
        raise ValueError(f"unknown category: {category}")
    if not item.jpg.is_file():
        raise SourceMissingError(f"移動元が見つかりません: {item.jpg.name}")

    # 走査後に json が消えた・増えた場合も、今ある実体に合わせる
    json = item.jpg.with_suffix(".json")
    sources = [item.jpg] + ([json] if json.is_file() else [])
    dest_dir = folder / category
    conflicts = [src.name for src in sources if (dest_dir / src.name).exists()]
    if conflicts:
        raise DestinationExistsError(
            f"{category} フォルダに同じ名前のファイルがあります: {', '.join(conflicts)}"
        )

    try:
        dest_dir.mkdir(exist_ok=True)
        dest_jpg = Path(shutil.move(item.jpg, dest_dir / item.jpg.name))
    except OSError as e:
        raise MoveError(f"{item.jpg.name} を移動できません: {e}") from e

    if len(sources) == 2:
        try:
            shutil.move(json, dest_dir / json.name)
        except OSError as e:
            try:
                shutil.move(dest_jpg, item.jpg)
            except OSError as rollback_error:
                raise MoveError(
                    f"{json.name} を移動できず、{item.jpg.name} も元に戻せませんでした"
                    f"（{dest_dir} を確認してください）: {e} / {rollback_error}"
                ) from e
            raise MoveError(f"{json.name} を移動できないため中止しました: {e}") from e
    return dest_jpg
