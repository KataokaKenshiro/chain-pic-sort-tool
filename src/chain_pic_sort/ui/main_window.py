"""メイン画面: 画像表示・振り分けボタン・件数・メタデータ。"""

from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QActionGroup, QImage, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from chain_pic_sort.core.imaging import Rotation, render
from chain_pic_sort.core.metadata import DISPLAY_KEYS, load_metadata
from chain_pic_sort.core.mover import MoveError, SourceMissingError
from chain_pic_sort.core.scanner import CATEGORIES
from chain_pic_sort.core.session import LogWriteError, SortSession
from chain_pic_sort.core.settings import AppSettings
from chain_pic_sort.ui.image_view import ImageView

NONE_TEXT = "なし"
ROTATION_LABELS = {Rotation.NONE: "なし", Rotation.LEFT: "左 90°", Rotation.RIGHT: "右 90°"}


def format_value(value: Any) -> str:
    if value is None:
        return NONE_TEXT
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


class MainWindow(QMainWindow):
    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self.settings = settings
        self.session: SortSession | None = None
        self.full_view = False
        self.setWindowTitle("Chain Pic Sort")
        self.resize(1280, 900)

        self.view = ImageView()
        self.buttons: dict[str, QPushButton] = {}
        button_row = QHBoxLayout()
        for number, category in enumerate(CATEGORIES, start=1):
            button = QPushButton(f"{category}  [{number}]")
            button.setMinimumHeight(48)
            # Space/Enter で直前に押したボタンが誤って押されないよう、フォーカスを取らせない
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.clicked.connect(lambda _=False, c=category: self.sort_current(c))
            button_row.addWidget(button)
            self.buttons[category] = button

        left = QVBoxLayout()
        left.addWidget(self.view, stretch=1)
        left.addLayout(button_row)

        self.folder_label = QLabel(NONE_TEXT)
        self.folder_label.setWordWrap(True)
        self.open_button = QPushButton("フォルダを開く…")
        self.open_button.clicked.connect(self.choose_folder)

        self.count_labels: dict[str, QLabel] = {}
        counts = QFormLayout()
        for key in ("合計", "残り", *CATEGORIES):
            self.count_labels[key] = QLabel("0")
            counts.addRow(f"{key}:", self.count_labels[key])
        counts_box = QGroupBox("件数")
        counts_box.setLayout(counts)

        self.position_label = QLabel("")
        self.file_label = QLabel(NONE_TEXT)
        self.file_label.setWordWrap(True)
        self.meta_labels: dict[str, QLabel] = {}
        meta = QFormLayout()
        meta.addRow("ファイル:", self.file_label)
        meta.addRow("表示中:", self.position_label)
        self.view_mode_label = QLabel("")
        meta.addRow("表示範囲:", self.view_mode_label)
        for key in DISPLAY_KEYS:
            self.meta_labels[key] = QLabel(NONE_TEXT)
            meta.addRow(f"{key}:", self.meta_labels[key])
        meta_box = QGroupBox("画像の情報")
        meta_box.setLayout(meta)

        right = QVBoxLayout()
        right.addWidget(self.open_button)
        right.addWidget(self.folder_label)
        right.addWidget(counts_box)
        right.addWidget(meta_box)
        right.addStretch(1)
        right_panel = QWidget()
        right_panel.setLayout(right)
        right_panel.setFixedWidth(300)

        root = QHBoxLayout()
        root.addLayout(left, stretch=1)
        root.addWidget(right_panel)
        central = QWidget()
        central.setLayout(root)
        self.setCentralWidget(central)

        self._build_menus()
        self._build_shortcuts()

    def _build_menus(self) -> None:
        file_menu = self.menuBar().addMenu("ファイル(&F)")
        open_action = QAction("フォルダを開く…", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.choose_folder)
        file_menu.addAction(open_action)

        rotate_menu = self.menuBar().addMenu("表示(&V)").addMenu("回転")
        group = QActionGroup(self)
        self.rotation_actions: dict[Rotation, QAction] = {}
        for rotation, label in ROTATION_LABELS.items():
            action = QAction(label, self, checkable=True)
            action.setChecked(rotation is self.settings.rotation)
            action.triggered.connect(lambda _=False, r=rotation: self.set_rotation(r))
            group.addAction(action)
            rotate_menu.addAction(action)
            self.rotation_actions[rotation] = action

    def _build_shortcuts(self) -> None:
        # QShortcut はウィンドウ内のどのウィジェットにフォーカスがあっても効く
        def bind(key: QKeySequence | Qt.Key | str, slot: Any) -> None:
            QShortcut(QKeySequence(key), self).activated.connect(slot)

        for number, category in enumerate(CATEGORIES, start=1):
            digit = getattr(Qt.Key, f"Key_{number}")
            bind(str(number), lambda c=category: self.sort_current(c))
            bind(
                QKeySequence(Qt.KeyboardModifier.KeypadModifier | digit),
                lambda c=category: self.sort_current(c),
            )
        bind(Qt.Key.Key_Left, self.show_prev)
        bind(Qt.Key.Key_Right, self.show_next)
        bind(Qt.Key.Key_F, self.toggle_full_view)

    def choose_folder(self) -> None:
        start = self.settings.last_folder
        path = QFileDialog.getExistingDirectory(
            self, "画像フォルダを選択", str(start) if start else ""
        )
        if path:
            self.open_folder(Path(path))

    def open_folder(self, folder: Path) -> None:
        self.session = SortSession(folder)
        self.settings.last_folder = folder
        self.folder_label.setText(str(folder))
        self.refresh()

    def set_rotation(self, rotation: Rotation) -> None:
        self.settings.rotation = rotation
        self.rotation_actions[rotation].setChecked(True)
        self.show_current()

    def sort_current(self, category: str) -> None:
        if self.session is None or self.session.current is None:
            return
        try:
            self.session.sort_current(category)
        except SourceMissingError as e:
            self.warn(f"{e}\nフォルダを読み直します。")
            self.session.reload()
        except MoveError as e:
            self.warn(str(e))
            return
        except LogWriteError as e:
            self.warn(f"画像は {category} に移動しましたが、{e}")
        self.refresh()
        if self.session.remaining == 0:
            self.info("すべての画像を振り分けました。")

    def show_prev(self) -> None:
        if self.session is not None and self.session.prev():
            self.show_current()

    def show_next(self) -> None:
        if self.session is not None and self.session.next():
            self.show_current()

    def toggle_full_view(self) -> None:
        self.full_view = not self.full_view
        self.show_current()

    def warn(self, text: str) -> None:
        QMessageBox.warning(self, "警告", text)

    def info(self, text: str) -> None:
        QMessageBox.information(self, "完了", text)

    def refresh(self) -> None:
        self.update_counts()
        self.show_current()

    def update_counts(self) -> None:
        session = self.session
        self.count_labels["合計"].setText(str(session.total if session else 0))
        self.count_labels["残り"].setText(str(session.remaining if session else 0))
        for category in CATEGORIES:
            count = session.counts.get(category, 0) if session else 0
            self.count_labels[category].setText(str(count))

    def show_current(self) -> None:
        self.view_mode_label.setText("全体 [F]" if self.full_view else "中心 1200x1200 [F]")
        item = self.session.current if self.session else None
        if item is None or self.session is None:
            self.view.set_image(None)
            self.file_label.setText(NONE_TEXT)
            self.position_label.setText("")
            self._show_metadata(None)
            return
        image = QImage(str(item.jpg))
        self.view.set_image(
            None if image.isNull() else render(image, self.settings.rotation, self.full_view)
        )
        self.file_label.setText(item.jpg.name + ("" if not image.isNull() else "（読めません）"))
        self.position_label.setText(f"{self.session.index + 1} / {self.session.remaining}")
        self._show_metadata(load_metadata(item.json))

    def _show_metadata(self, metadata: dict[str, Any] | None) -> None:
        for key, label in self.meta_labels.items():
            label.setText(format_value(metadata.get(key) if metadata else None))
