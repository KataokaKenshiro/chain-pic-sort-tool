from pathlib import Path

import pytest

from chain_pic_sort.core import session as session_module
from chain_pic_sort.core.mover import DestinationExistsError
from chain_pic_sort.core.session import LogWriteError, SortSession
from chain_pic_sort.core.sortlog import LOG_NAME


def make_folder(tmp_path: Path, stems: list[str]) -> Path:
    for stem in stems:
        (tmp_path / f"{stem}.jpg").write_bytes(b"jpg")
        (tmp_path / f"{stem}.json").write_text('{"verdict": "OK"}', encoding="utf-8")
    return tmp_path


def names(session: SortSession) -> list[str]:
    return [i.jpg.stem for i in session.items]


def test_counts_include_already_sorted_files(tmp_path: Path) -> None:
    make_folder(tmp_path, ["a", "b"])
    (tmp_path / "NG").mkdir()
    (tmp_path / "NG" / "z.jpg").write_bytes(b"jpg")

    session = SortSession(tmp_path)

    assert (session.total, session.remaining, session.counts["NG"]) == (3, 2, 1)


def test_next_and_prev_stop_at_ends(tmp_path: Path) -> None:
    session = SortSession(make_folder(tmp_path, ["a", "b"]))

    assert session.prev() is False
    assert session.next() is True
    assert session.next() is False
    assert session.current is not None and session.current.jpg.stem == "b"


def test_sort_current_moves_logs_and_shows_next(tmp_path: Path) -> None:
    session = SortSession(make_folder(tmp_path, ["a", "b", "c"]))

    session.sort_current("OK")

    assert (tmp_path / "OK" / "a.json").exists()
    assert names(session) == ["b", "c"]
    assert session.current is not None and session.current.jpg.stem == "b"
    assert (session.total, session.remaining, session.counts["OK"]) == (3, 2, 1)
    assert "a.jpg,OK,OK" in (tmp_path / LOG_NAME).read_text(encoding="utf-8-sig")


def test_sorting_last_item_falls_back_to_previous(tmp_path: Path) -> None:
    session = SortSession(make_folder(tmp_path, ["a", "b"]))
    session.next()

    session.sort_current("NG")
    assert session.current is not None and session.current.jpg.stem == "a"

    session.sort_current("SKIP")
    assert session.current is None
    assert session.remaining == 0


def test_failed_move_keeps_state(tmp_path: Path) -> None:
    session = SortSession(make_folder(tmp_path, ["a"]))
    (tmp_path / "END").mkdir()
    (tmp_path / "END" / "a.jpg").write_bytes(b"old")

    with pytest.raises(DestinationExistsError):
        session.sort_current("END")

    assert names(session) == ["a"]
    assert not (tmp_path / LOG_NAME).exists()


def test_log_failure_after_move_still_advances(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    session = SortSession(make_folder(tmp_path, ["a", "b"]))

    def locked(*args: object, **kwargs: object) -> None:
        raise PermissionError("locked by Excel")

    monkeypatch.setattr(session_module, "append_log", locked)

    with pytest.raises(LogWriteError):
        session.sort_current("OK")

    assert (tmp_path / "OK" / "a.jpg").exists()
    assert names(session) == ["b"]
