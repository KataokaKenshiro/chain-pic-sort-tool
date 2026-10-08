"""画像をウィンドウに収めて表示するビュー。"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPixmap, QResizeEvent
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView


class ImageView(QGraphicsView):
    def __init__(self) -> None:
        super().__init__()
        self._scene = QGraphicsScene(self)
        self._item = QGraphicsPixmapItem()
        self._item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self._scene.addItem(self._item)
        self.setScene(self._scene)
        self.setBackgroundBrush(QColor(32, 32, 32))
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def set_image(self, image: QImage | None) -> None:
        """画像を差し替えて、ウィンドウに収まる表示に戻す。None なら空にする。"""
        self._item.setPixmap(QPixmap.fromImage(image) if image is not None else QPixmap())
        self._scene.setSceneRect(self._item.boundingRect())
        self.fit()

    def has_image(self) -> bool:
        return not self._item.pixmap().isNull()

    def fit(self) -> None:
        self.resetTransform()
        if self.has_image():
            self.fitInView(self._item, Qt.AspectRatioMode.KeepAspectRatio)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.fit()
