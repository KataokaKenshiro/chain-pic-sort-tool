import csv
from datetime import datetime
from pathlib import Path

from chain_pic_sort.core.sortlog import HEADER, LOG_NAME, append_log

NOW = datetime(2026, 6, 22, 14, 7, 10)


def read_rows(folder: Path) -> list[list[str]]:
    with (folder / LOG_NAME).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def test_creates_log_with_header_and_bom(tmp_path: Path) -> None:
    meta = {"verdict": "OK", "confidence": 0.99, "mahalanobis": 310.2}

    append_log(tmp_path, "a.jpg", "OK", meta, now=NOW)

    assert (tmp_path / LOG_NAME).read_bytes().startswith(b"\xef\xbb\xbf")
    assert read_rows(tmp_path) == [
        list(HEADER),
        ["2026-06-22T14:07:10", "a.jpg", "OK", "OK", "0.99", "310.2"],
    ]


def test_appends_without_repeating_header_or_bom(tmp_path: Path) -> None:
    append_log(tmp_path, "a.jpg", "OK", None, now=NOW)
    append_log(tmp_path, "b.jpg", "NG", None, now=NOW)

    assert (tmp_path / LOG_NAME).read_bytes().count(b"\xef\xbb\xbf") == 1
    rows = read_rows(tmp_path)
    assert [r[1] for r in rows] == ["filename", "a.jpg", "b.jpg"]


def test_writes_empty_fields_when_metadata_missing(tmp_path: Path) -> None:
    append_log(tmp_path, "a.jpg", "END", None, now=NOW)

    assert read_rows(tmp_path)[1] == ["2026-06-22T14:07:10", "a.jpg", "END", "", "", ""]
