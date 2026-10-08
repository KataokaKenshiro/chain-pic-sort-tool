"""画像をウィンドウに収めて表示し、ホイールで拡大・ドラッグで移動できるビュー。"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPixmap, QResizeEvent, QWheelEvent
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView

ZOOM_STEP = 1.25
MAX_SCALE = 8.0  # 元画像の 1 画素が画面の 8 画素になるまで


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
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self._zoomed = False

    def set_image(self, image: QImage | None) -> None:
        """画像を差し替えて、ウィンドウに収まる表示に戻す。None なら空にする。"""
        self._item.setPixmap(QPixmap.fromImage(image) if image is not None else QPixmap())
        self._scene.setSceneRect(self._item.boundingRect())
        self.fit()

    def has_image(self) -> bool:
        return not self._item.pixmap().isNull()

    def scale_factor(self) -> float:
        return self.transform().m11()

    def fit(self) -> None:
        self._zoomed = False
        self.resetTransform()
        if self.has_image():
            self.fitInView(self._item, Qt.AspectRatioMode.KeepAspectRatio)

    def _fit_scale(self) -> float:
        rect = self._item.boundingRect()
        view = self.viewport().rect()
        return min(view.width() / rect.width(), view.height() / rect.height())

    def wheelEvent(self, event: QWheelEvent) -> None:
        if not self.has_image():
            return
        current = self.scale_factor()
        target = min(current * ZOOM_STEP ** (event.angleDelta().y() / 120), MAX_SCALE)
        # 収まる大きさより小さくはしない
        if target <= self._fit_scale():
            self.fit()
            return
        self.scale(target / current, target / current)
        self._zoomed = True

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if not self._zoomed:
            self.fit()
