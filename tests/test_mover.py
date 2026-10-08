import shutil
from pathlib import Path

import pytest

from chain_pic_sort.core import mover
from chain_pic_sort.core.mover import DestinationExistsError, MoveError, SourceMissingError
from chain_pic_sort.core.scanner import ImageItem, scan


def make_pair(folder: Path, stem: str, with_json: bool = True) -> ImageItem:
    (folder / f"{stem}.jpg").write_bytes(b"jpg")
    if with_json:
        (folder / f"{stem}.json").write_text("{}", encoding="utf-8")
    return scan(folder)[0]


def test_moves_jpg_and_json_into_new_category_folder(tmp_path: Path) -> None:
    item = make_pair(tmp_path, "a")

    dest = mover.move_item(item, tmp_path, "NG")

    assert dest == tmp_path / "NG" / "a.jpg"
    assert sorted(p.name for p in (tmp_path / "NG").iterdir()) == ["a.jpg", "a.json"]
    assert not (tmp_path / "a.jpg").exists()
    assert not (tmp_path / "a.json").exists()


def test_moves_jpg_alone_when_json_missing(tmp_path: Path) -> None:
    item = make_pair(tmp_path, "a", with_json=False)

    mover.move_item(item, tmp_path, "OK")

    assert [p.name for p in (tmp_path / "OK").iterdir()] == ["a.jpg"]


@pytest.mark.parametrize("existing", ["a.jpg", "a.json"])
def test_refuses_when_destination_has_same_name(tmp_path: Path, existing: str) -> None:
    item = make_pair(tmp_path, "a")
    (tmp_path / "OK").mkdir()
    (tmp_path / "OK" / existing).write_bytes(b"old")

    with pytest.raises(DestinationExistsError):
        mover.move_item(item, tmp_path, "OK")

    assert (tmp_path / "a.jpg").exists()
    assert (tmp_path / "a.json").exists()
    assert (tmp_path / "OK" / existing).read_bytes() == b"old"


def test_rolls_back_jpg_when_json_move_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    item = make_pair(tmp_path, "a")
    real_move = shutil.move

    def fail_on_json(src, dst):
        if str(src).endswith(".json"):
            raise PermissionError("locked")
        return real_move(src, dst)

    monkeypatch.setattr(mover.shutil, "move", fail_on_json)

    with pytest.raises(MoveError):
        mover.move_item(item, tmp_path, "SKIP")

    assert (tmp_path / "a.jpg").read_bytes() == b"jpg"
    assert (tmp_path / "a.json").exists()
    assert list((tmp_path / "SKIP").iterdir()) == []


def test_reports_missing_source(tmp_path: Path) -> None:
    item = make_pair(tmp_path, "a")
    (tmp_path / "a.jpg").unlink()

    with pytest.raises(SourceMissingError):
        mover.move_item(item, tmp_path, "END")


def test_reports_error_when_category_name_is_a_file(tmp_path: Path) -> None:
    item = make_pair(tmp_path, "a")
    (tmp_path / "NG").write_bytes(b"not a folder")

    with pytest.raises(MoveError):
        mover.move_item(item, tmp_path, "NG")

    assert (tmp_path / "a.jpg").exists()
