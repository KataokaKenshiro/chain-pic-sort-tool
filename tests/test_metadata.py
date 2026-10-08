from pathlib import Path

from chain_pic_sort.core.metadata import load_metadata


def test_load_metadata_reads_json(tmp_path: Path) -> None:
    path = tmp_path / "a.json"
    path.write_text('{"verdict": "OK", "confidence": 0.99}', encoding="utf-8")

    assert load_metadata(path) == {"verdict": "OK", "confidence": 0.99}


def test_load_metadata_keeps_partial_fields(tmp_path: Path) -> None:
    path = tmp_path / "a.json"
    path.write_text('{"verdict": "NG"}', encoding="utf-8")

    data = load_metadata(path)

    assert data is not None
    assert data.get("mahalanobis") is None


def test_load_metadata_returns_none_when_missing_or_broken(tmp_path: Path) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")
    not_object = tmp_path / "list.json"
    not_object.write_text("[1, 2]", encoding="utf-8")

    assert load_metadata(None) is None
    assert load_metadata(tmp_path / "missing.json") is None
    assert load_metadata(broken) is None
    assert load_metadata(not_object) is None
