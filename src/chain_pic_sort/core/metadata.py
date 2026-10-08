"""画像に対応する json（AI 判定結果）を読む。"""

import json
from pathlib import Path
from typing import Any

# 画面に表示する項目（この順で並べる）
DISPLAY_KEYS = (
    "verdict",
    "composite_verdict",
    "confidence",
    "mahalanobis",
    "end_threshold",
    "timestamp",
)


def load_metadata(path: Path | None) -> dict[str, Any] | None:
    """json を読んで dict を返す。無い・読めない・オブジェクトでない場合は None。"""
    if path is None:
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None
