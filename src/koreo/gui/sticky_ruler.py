"""Fixed ruler overlay synchronized with a scroll area's canvas."""

from collections.abc import Callable

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QColor, QPaintEvent, QPainter
from PySide6.QtWidgets import QScrollArea, QWidget


class StickyRuler(QWidget):
    """Keep a canvas-provided ruler visible while its rows scroll vertically."""

    def __init__(
        self,
        scroll_area: QScrollArea,
        height: int,
        paint_ruler: Callable[[QPainter], None],
    ) -> None:
        super().__init__(scroll_area.viewport())
        self._scroll_area = scroll_area
        self._paint_ruler = paint_ruler
        self.setFixedHeight(height)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        scroll_area.viewport().installEventFilter(self)
        scroll_area.horizontalScrollBar().valueChanged.connect(self.update)
        self._sync_geometry()
        self.raise_()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self._scroll_area.viewport() and event.type() in (
            QEvent.Type.Resize,
            QEvent.Type.Show,
        ):
            self._sync_geometry()
        return super().eventFilter(watched, event)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#f8fafc"))
        painter.translate(-self._scroll_area.horizontalScrollBar().value(), 0)
        self._paint_ruler(painter)
        painter.end()

    def refresh(self) -> None:
        """Repaint after project, zoom, or display-mode changes."""

        self.raise_()
        self.update()

    def _sync_geometry(self) -> None:
        self.setGeometry(0, 0, self._scroll_area.viewport().width(), self.height())
