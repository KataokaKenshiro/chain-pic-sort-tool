"""表示用に画像を中心クロップ・回転する。"""

from enum import Enum

from PySide6.QtGui import QImage, QTransform

CROP_SIZE = 1200


class Rotation(Enum):
    NONE = "none"
    LEFT = "left"
    RIGHT = "right"

    @property
    def degrees(self) -> int:
        # Qt の座標系（y 下向き）では正の角度が時計回り
        return {Rotation.NONE: 0, Rotation.LEFT: -90, Rotation.RIGHT: 90}[self]


def center_crop(image: QImage, size: int = CROP_SIZE) -> QImage:
    """中心から size x size を切り出す。画像が小さい辺はその辺の長さまで。"""
    w = min(size, image.width())
    h = min(size, image.height())
    return image.copy((image.width() - w) // 2, (image.height() - h) // 2, w, h)


def rotate(image: QImage, rotation: Rotation) -> QImage:
    if rotation is Rotation.NONE:
        return image
    return image.transformed(QTransform().rotate(rotation.degrees))


def render(image: QImage, rotation: Rotation, full: bool = False) -> QImage:
    """表示する画像を作る。full=True なら切り出さずに全体を回転だけする。"""
    return rotate(image if full else center_crop(image), rotation)
