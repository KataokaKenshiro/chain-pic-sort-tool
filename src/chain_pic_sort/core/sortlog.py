"""振り分け結果を選択フォルダの sort_log.csv に追記する。"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Any

LOG_NAME = "sort_log.csv"
HEADER = ("timestamp", "filename", "category", "verdict", "confidence", "mahalanobis")


def append_log(
    folder: Path,
    filename: str,
    category: str,
    metadata: dict[str, Any] | None,
    now: datetime | None = None,
) -> None:
    """1 行追記する。ファイルが無ければヘッダ行から書く。

    Windows の Excel で開いても文字化けしないよう UTF-8 BOM 付きにする
    （utf-8-sig は追記時には BOM を書かない）。
    """
    path = folder / LOG_NAME
    is_new = not path.exists() or path.stat().st_size == 0
    meta = metadata or {}
    row = [
        (now or datetime.now()).isoformat(timespec="seconds"),
        filename,
        category,
        meta.get("verdict", ""),
        meta.get("confidence", ""),
        meta.get("mahalanobis", ""),
    ]
    with path.open("a", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(HEADER)
        writer.writerow(row)
