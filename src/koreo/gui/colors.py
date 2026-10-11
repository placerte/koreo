"""Small color helpers shared by prototype widgets."""

from PySide6.QtGui import QColor


def translucent(color: str, alpha: int = 210) -> QColor:
    """Return ``color`` with the requested opacity."""

    result = QColor(color)
    result.setAlpha(alpha)
    return result


def text_color(background: QColor) -> QColor:
    """Choose readable black or white text for ``background``."""

    luminance = (
        0.299 * background.red()
        + 0.587 * background.green()
        + 0.114 * background.blue()
    )
    return QColor("#111827") if luminance > 150 else QColor("#ffffff")
