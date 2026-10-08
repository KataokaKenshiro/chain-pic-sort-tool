from pathlib import Path

from chain_pic_sort.core.scanner import CATEGORIES, count_sorted, scan


def touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")
    return path


def test_scan_lists_jpgs_in_name_order_with_json_pairs(tmp_path: Path) -> None:
    touch(tmp_path / "b_000002.jpg")
    touch(tmp_path / "a_000001.jpg")
    touch(tmp_path / "a_000001.json")
    touch(tmp_path / "c_000003.JPG")
    touch(tmp_path / "notes.txt")

    items = scan(tmp_path)

    assert [i.jpg.name for i in items] == ["a_000001.jpg", "b_000002.jpg", "c_000003.JPG"]
    assert items[0].json == tmp_path / "a_000001.json"
    assert items[1].json is None


def test_scan_ignores_subfolders_and_category_folders(tmp_path: Path) -> None:
    touch(tmp_path / "top.jpg")
    touch(tmp_path / "OK" / "sorted.jpg")
    touch(tmp_path / "other" / "nested.jpg")

    assert [i.jpg.name for i in scan(tmp_path)] == ["top.jpg"]


def test_count_sorted_counts_jpgs_per_category(tmp_path: Path) -> None:
    touch(tmp_path / "OK" / "1.jpg")
    touch(tmp_path / "OK" / "1.json")
    touch(tmp_path / "OK" / "2.jpg")
    touch(tmp_path / "NG" / "3.jpg")

    assert count_sorted(tmp_path) == {"OK": 2, "NG": 1, "SKIP": 0, "END": 0}
    assert tuple(count_sorted(tmp_path)) == CATEGORIES
