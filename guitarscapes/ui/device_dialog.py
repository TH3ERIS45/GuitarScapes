"""PyQt6 device selection dialog with dark theme.

Shows a list of audio input devices and lets the user select one.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from guitarscapes.utils.logger import get_logger

logger = get_logger("ui.device_dialog")

try:
    from PyQt6.QtWidgets import (
        QDialog,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QPushButton,
        QDialogButtonBox,
    )
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont

    _PYQT6_AVAILABLE = True
except ImportError:
    _PYQT6_AVAILABLE = False
    logger.debug("PyQt6 not available — device dialog will be skipped.")


DARK_STYLESHEET = """
QDialog {
    background-color: #1a1a2e;
    color: #e0e0e0;
}
QLabel {
    color: #e0e0e0;
    font-size: 14px;
}
QLabel#title {
    font-size: 20px;
    font-weight: bold;
    color: #b0b0ff;
    padding: 8px;
}
QListWidget {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #333366;
    border-radius: 6px;
    padding: 4px;
    font-size: 13px;
}
QListWidget::item {
    padding: 10px 8px;
    border-bottom: 1px solid #222244;
}
QListWidget::item:selected {
    background-color: #4a00e0;
    color: #ffffff;
    border-radius: 4px;
}
QListWidget::item:hover {
    background-color: #2a2a5e;
}
QPushButton {
    background-color: #4a00e0;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #5a10f0;
}
QPushButton:pressed {
    background-color: #3a00c0;
}
QPushButton#refresh {
    background-color: #333366;
}
QPushButton#refresh:hover {
    background-color: #444488;
}
QDialogButtonBox QPushButton {
    min-width: 80px;
}
"""


if _PYQT6_AVAILABLE:

    class DeviceSelectionDialog(QDialog):
        """Dark-themed dialog for selecting an audio input device.

        Args:
            devices: List of device dicts with keys: index, name, channels,
                     sample_rate, is_default.
            default_index: Pre-selected device index.
            refresh_callback: Called when user clicks Refresh; should return a
                              new device list.
        """

        def __init__(
            self,
            devices: list[dict[str, Any]],
            default_index: Optional[int] = None,
            refresh_callback: Optional[Callable[[], list[dict[str, Any]]]] = None,
            parent=None,
        ) -> None:
            super().__init__(parent)
            self._devices = devices
            self._default_index = default_index
            self._refresh_callback = refresh_callback
            self._selected_index: Optional[int] = default_index

            self.setWindowTitle("GuitarScapes Pro — Selecionar Dispositivo de Áudio")
            self.setMinimumSize(520, 400)
            self.setStyleSheet(DARK_STYLESHEET)

            self._build_ui()
            self._populate_list()

        # ── UI Construction ─────────────────────────────────────────────────

        def _build_ui(self) -> None:
            layout = QVBoxLayout(self)
            layout.setSpacing(12)

            # Title
            title = QLabel("🎸 Selecionar Dispositivo de Áudio")
            title.setObjectName("title")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)

            # Subtitle
            subtitle = QLabel(
                "Escolha o microfone ou interface de áudio para captura:"
            )
            subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(subtitle)

            # Device list
            self._list_widget = QListWidget()
            self._list_widget.itemSelectionChanged.connect(self._on_selection_changed)
            self._list_widget.itemDoubleClicked.connect(self.accept)
            layout.addWidget(self._list_widget)

            # Bottom row: Refresh + OK/Cancel
            bottom_layout = QHBoxLayout()

            refresh_btn = QPushButton("🔄 Atualizar")
            refresh_btn.setObjectName("refresh")
            refresh_btn.clicked.connect(self._on_refresh)
            bottom_layout.addWidget(refresh_btn)

            bottom_layout.addStretch()

            button_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok
                | QDialogButtonBox.StandardButton.Cancel
            )
            button_box.accepted.connect(self.accept)
            button_box.rejected.connect(self.reject)
            bottom_layout.addWidget(button_box)

            layout.addLayout(bottom_layout)

        def _populate_list(self) -> None:
            """Fill the list widget with device entries."""
            self._list_widget.clear()
            for dev in self._devices:
                default_tag = " ★" if dev.get("is_default") else ""
                text = (
                    f"[{dev['index']}] {dev['name']}{default_tag}\n"
                    f"    {dev['channels']} canal(is) · {dev['sample_rate']:.0f} Hz"
                )
                item = QListWidgetItem(text)
                item.setData(Qt.ItemDataRole.UserRole, dev["index"])
                self._list_widget.addItem(item)

                # Pre-select default
                if dev["index"] == self._default_index:
                    self._list_widget.setCurrentItem(item)

        # ── Properties ──────────────────────────────────────────────────────

        @property
        def selected_device_index(self) -> Optional[int]:
            """Index of the selected device, or None."""
            return self._selected_index

        # ── Slots ───────────────────────────────────────────────────────────

        def _on_selection_changed(self) -> None:
            items = self._list_widget.selectedItems()
            if items:
                self._selected_index = items[0].data(Qt.ItemDataRole.UserRole)

        def _on_refresh(self) -> None:
            if self._refresh_callback:
                try:
                    self._devices = self._refresh_callback()
                    self._populate_list()
                    logger.info("Device list refreshed")
                except Exception as exc:
                    logger.error("Failed to refresh devices: %s", exc)

else:
    # Stub when PyQt6 is not installed
    class DeviceSelectionDialog:  # type: ignore[no-redef]
        """Stub dialog when PyQt6 is not available."""

        def __init__(self, *args, **kwargs):
            self._selected_index = kwargs.get("default_index")

        @property
        def selected_device_index(self):
            return self._selected_index

        def exec(self):
            return False
