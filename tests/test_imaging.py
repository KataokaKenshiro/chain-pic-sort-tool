import pytest
from PySide6.QtGui import QColor, QImage

from chain_pic_sort.core.imaging import Rotation, center_crop, render

RED = QColor(255, 0, 0).rgb()


def make_image(width: int = 2048, height: int = 1200) -> QImage:
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(QColor(0, 0, 0))
    return image


def test_center_crop_cuts_square_from_middle() -> None:
    image = make_image()
    # 切り出し範囲の左上（x = (2048 - 1200) / 2 = 424）に目印を置く
    image.setPixel(424, 0, RED)

    cropped = center_crop(image)

    assert (cropped.width(), cropped.height()) == (1200, 1200)
    assert cropped.pixel(0, 0) == RED


def test_center_crop_keeps_smaller_side() -> None:
    cropped = center_crop(make_image(800, 600))

    assert (cropped.width(), cropped.height()) == (800, 600)


@pytest.mark.parametrize(
    ("rotation", "expected"),
    [
        (Rotation.NONE, (0, 0)),
        (Rotation.RIGHT, (1199, 0)),  # 時計回り: 左上 → 右上
        (Rotation.LEFT, (0, 1199)),  # 反時計回り: 左上 → 左下
    ],
)
def test_render_rotates_crop(rotation: Rotation, expected: tuple[int, int]) -> None:
    image = make_image()
    image.setPixel(424, 0, RED)

    rendered = render(image, rotation)

    assert (rendered.width(), rendered.height()) == (1200, 1200)
    assert rendered.pixel(*expected) == RED


def test_render_full_rotates_whole_image() -> None:
    image = make_image()
    image.setPixel(0, 0, RED)

    rendered = render(image, Rotation.RIGHT, full=True)

    assert (rendered.width(), rendered.height()) == (1200, 2048)
    assert rendered.pixel(1199, 0) == RED
