import pytest

from chain_pic_sort import app


def test_unexpected_error_is_shown_in_dialog(qtbot, monkeypatch: pytest.MonkeyPatch) -> None:
    shown: list[str] = []
    monkeypatch.setattr(
        app.QMessageBox, "critical", lambda _parent, _title, text: shown.append(text)
    )

    try:
        raise PermissionError("denied")
    except PermissionError as e:
        app.show_unexpected_error(type(e), e, e.__traceback__)

    assert shown == ["予期しないエラーが発生しました。\nPermissionError: denied"]
