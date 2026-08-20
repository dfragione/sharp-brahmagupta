import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QSize, QUrl, QMimeData, QPoint
)
from PyQt6.QtGui import (
    QIcon, QPixmap, QImage, QPainter, QColor, QFont, QDragEnterEvent,
    QDropEvent, QDesktopServices, QCursor
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QCheckBox, QFileDialog, QListWidget,
    QListWidgetItem, QProgressBar, QFrame, QSplitter, QMessageBox,
    QScrollArea, QSizePolicy, QToolButton, QDialog, QTextEdit, QButtonGroup
)

import converter_engine
import updater

# Windows 11 Fluent Dark Theme QSS
WINDOWS_11_QSS = """
QMainWindow, QWidget#CentralWidget, QDialog {
    background-color: #1a1b1e;
    color: #f3f4f6;
    font-family: "Segoe UI Variable", "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

/* Format Segmented Tab Container */
#FormatTabContainer {
    background-color: #222328;
    border: 1px solid #33353e;
    border-radius: 10px;
    padding: 3px;
}

QPushButton.FormatTab {
    background-color: transparent;
    color: #9ca3af;
    border: none;
    border-radius: 7px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton.FormatTab:hover {
    color: #ffffff;
    background-color: #2b2e36;
}
QPushButton.FormatTab:checked {
    background-color: #0078d4;
    color: #ffffff;
    font-weight: 700;
}

/* Drop Zone Frame */
#DropZone {
    background-color: #24252a;
    border: 2px dashed #444853;
    border-radius: 14px;
    transition: all 0.2s ease-in-out;
}
#DropZone:hover, #DropZone[dragActive="true"] {
    background-color: #2b2e36;
    border: 2px dashed #0078d4;
}

/* Control Cards */
#SettingsCard, #DialogCard {
    background-color: #222328;
    border: 1px solid #33353e;
    border-radius: 12px;
    padding: 12px;
}

/* Buttons */
QPushButton {
    background-color: #32343d;
    color: #ffffff;
    border: 1px solid #454854;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #3e414c;
    border-color: #585c6a;
}
QPushButton:pressed {
    background-color: #292a31;
}
QPushButton:disabled {
    background-color: #24252a;
    color: #666974;
    border-color: #33353e;
}

/* Primary Accent Button */
QPushButton#PrimaryButton {
    background-color: #0078d4;
    border: 1px solid #1a88df;
    font-size: 14px;
    font-weight: 600;
    padding: 10px 24px;
}
QPushButton#PrimaryButton:hover {
    background-color: #1084d9;
    border-color: #2692e5;
}
QPushButton#PrimaryButton:pressed {
    background-color: #006bbd;
}

/* Preset Buttons */
QPushButton#PresetButton {
    padding: 4px 10px;
    font-size: 11px;
    border-radius: 6px;
    background-color: #2a2c34;
}
QPushButton#PresetButton:hover {
    background-color: #383a45;
}

/* Header Action Button */
QPushButton#HeaderButton {
    background-color: #26272e;
    border: 1px solid #3c3f4c;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 12px;
    color: #d1d5db;
}
QPushButton#HeaderButton:hover {
    background-color: #33353f;
    color: #ffffff;
    border-color: #0078d4;
}

/* List Widget */
QListWidget {
    background-color: #202126;
    border: 1px solid #33353e;
    border-radius: 12px;
    padding: 6px;
    outline: none;
}
QListWidget::item {
    background-color: #27282f;
    border: 1px solid #363843;
    border-radius: 8px;
    margin: 3px 2px;
    padding: 6px;
}
QListWidget::item:hover {
    background-color: #30323a;
    border-color: #4a4d5c;
}
QListWidget::item:selected {
    background-color: #353842;
    border-color: #0078d4;
}

/* Sliders */
QSlider::groove:horizontal {
    height: 6px;
    background: #363842;
    border-radius: 3px;
}
QSlider::sub-page:horizontal {
    background: #0078d4;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #ffffff;
    border: 2px solid #0078d4;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}
QSlider::handle:horizontal:hover {
    background: #e1f0ff;
}

/* Checkbox */
QCheckBox {
    spacing: 8px;
    color: #e1e3e8;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #505461;
    background-color: #27282f;
}
QCheckBox::indicator:hover {
    border-color: #0078d4;
}
QCheckBox::indicator:checked {
    background-color: #0078d4;
    border-color: #0078d4;
}

/* Progress Bar */
QProgressBar {
    background-color: #27282f;
    border: 1px solid #363842;
    border-radius: 6px;
    text-align: center;
    color: #ffffff;
    font-size: 11px;
    font-weight: bold;
    height: 16px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0078d4, stop:1 #00a4ef);
    border-radius: 5px;
}

/* Text Edit */
QTextEdit {
    background-color: #1a1b1f;
    border: 1px solid #363842;
    border-radius: 8px;
    color: #e5e7eb;
    font-size: 12px;
    padding: 8px;
}
"""


class UpdateCheckThread(QThread):
    """Worker thread to check for updates without blocking UI."""
    check_finished = pyqtSignal(dict)

    def run(self):
        result = updater.check_for_updates()
        self.check_finished.emit(result)


class UpdateDialog(QDialog):
    """Modern Windows 11 dialog for checking and installing updates."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PixShift Update Manager")
        self.setFixedSize(460, 360)
        self.setStyleSheet(WINDOWS_11_QSS)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        head_layout = QHBoxLayout()
        icon_lbl = QLabel("⚡")
        icon_lbl.setStyleSheet("font-size: 28px;")
        head_layout.addWidget(icon_lbl)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        self.title_lbl = QLabel("Checking for Updates...")
        self.title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        title_col.addWidget(self.title_lbl)

        self.ver_lbl = QLabel(f"Current Version: v{updater.get_current_version()}")
        self.ver_lbl.setStyleSheet("font-size: 12px; color: #9ca3af;")
        title_col.addWidget(self.ver_lbl)
        head_layout.addLayout(title_col, stretch=1)
        layout.addLayout(head_layout)

        self.card = QFrame()
        self.card.setObjectName("DialogCard")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(8)

        self.status_icon = QLabel("🔄")
        self.status_icon.setStyleSheet("font-size: 24px;")
        self.status_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.status_icon)

        self.status_text = QLabel("Connecting to update server...")
        self.status_text.setStyleSheet("color: #e5e7eb; font-size: 13px;")
        self.status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_text.setWordWrap(True)
        card_layout.addWidget(self.status_text)

        self.notes_box = QTextEdit()
        self.notes_box.setReadOnly(True)
        self.notes_box.setVisible(False)
        card_layout.addWidget(self.notes_box)

        self.dl_progress = QProgressBar()
        self.dl_progress.setVisible(False)
        card_layout.addWidget(self.dl_progress)

        layout.addWidget(self.card, stretch=1)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.action_btn = QPushButton("Install Update")
        self.action_btn.setObjectName("PrimaryButton")
        self.action_btn.setVisible(False)
        self.action_btn.clicked.connect(self.start_download)
        btn_layout.addWidget(self.action_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)

        self.update_data: Dict[str, Any] = {}
        self.start_check()

    def start_check(self):
        self.thread = UpdateCheckThread()
        self.thread.check_finished.connect(self.on_check_completed)
        self.thread.start()

    def on_check_completed(self, data: Dict[str, Any]):
        self.update_data = data
        if data.get("has_update"):
            latest = data.get("latest_version")
            self.title_lbl.setText("🎉 New Update Available!")
            self.status_icon.setText("🚀")
            self.status_text.setText(f"A new version (v{latest}) is ready for download.")
            self.notes_box.setVisible(True)
            self.notes_box.setPlainText(f"Release Notes (v{latest}):\n\n{data.get('release_notes', '')}")
            self.action_btn.setVisible(bool(data.get("download_url")))
            self.action_btn.setText(f"Download & Update (v{latest})")
        else:
            self.title_lbl.setText("PixShift is Up to Date")
            self.status_icon.setText("✅")
            msg = data.get("status_message", f"You are currently running the latest version (v{updater.get_current_version()}).")
            self.status_text.setText(msg)

    def start_download(self):
        download_url = self.update_data.get("download_url")
        if not download_url:
            return

        self.action_btn.setEnabled(False)
        self.status_text.setText("Downloading update...")
        self.dl_progress.setVisible(True)
        self.dl_progress.setValue(0)

        def on_prog(pct):
            self.dl_progress.setValue(pct)
            QApplication.processEvents()

        success = updater.download_and_install_update(download_url, progress_callback=on_prog)
        if not success:
            self.status_text.setText("Update download failed. Please check your internet connection.")
            self.action_btn.setEnabled(True)


class DropZoneWidget(QFrame):
    """Interactive drag and drop zone for importing images."""
    files_dropped = pyqtSignal(list)
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("dragActive", False)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 22, 20, 22)

        self.icon_label = QLabel("📥")
        self.icon_label.setStyleSheet("font-size: 36px; background: transparent;")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)

        self.title_label = QLabel("Drop image files here or click to import")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #ffffff; background: transparent;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.sub_label = QLabel("Converts PNG, HEIC, WEBP, AVIF, SVG, TIFF, BMP, GIF, PSD & RAW")
        self.sub_label.setStyleSheet("font-size: 12px; color: #9ca3af; background: transparent;")
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sub_label)

        self.browse_btn = QPushButton("📁 Browse Image(s)...")
        self.browse_btn.setFixedWidth(160)
        self.browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_btn.clicked.connect(self.clicked.emit)
        layout.addWidget(self.browse_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setProperty("dragActive", True)
            self.style().unpolish(self)
            self.style().polish(self)

    def dragLeaveEvent(self, event):
        self.setProperty("dragActive", False)
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent):
        self.setProperty("dragActive", False)
        self.style().unpolish(self)
        self.style().polish(self)

        urls = event.mimeData().urls()
        filepaths = []
        for url in urls:
            local_path = url.toLocalFile()
            if os.path.isfile(local_path):
                filepaths.append(local_path)
            elif os.path.isdir(local_path):
                for root, _, files in os.walk(local_path):
                    for file in files:
                        fp = os.path.join(root, file)
                        if converter_engine.is_supported_image(fp):
                            filepaths.append(fp)
        
        if filepaths:
            self.files_dropped.emit(filepaths)


class FileItemWidget(QWidget):
    """Custom row widget representing a single image in the batch queue."""
    remove_requested = pyqtSignal(str)

    def __init__(self, filepath: str, target_format: str = "JPG", parent=None):
        super().__init__(parent)
        self.filepath = filepath
        self.target_format = target_format
        self.output_path = None
        self.status = "pending"

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(12)

        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(44, 44)
        self.thumb_label.setStyleSheet("background-color: #1c1d22; border-radius: 6px; border: 1px solid #363842;")
        self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.load_thumbnail()
        layout.addWidget(self.thumb_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)

        top_row = QHBoxLayout()
        top_row.setSpacing(6)

        badge_text = converter_engine.get_format_badge(filepath)
        self.badge = QLabel(badge_text)
        self.badge.setStyleSheet("""
            background-color: #0078d4;
            color: #ffffff;
            font-size: 10px;
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 4px;
        """)
        top_row.addWidget(self.badge)

        file_name = Path(filepath).name
        self.name_label = QLabel(file_name)
        self.name_label.setStyleSheet("font-weight: 600; color: #ffffff; font-size: 13px;")
        top_row.addWidget(self.name_label, stretch=1)
        info_layout.addLayout(top_row)

        file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
        size_str = converter_engine.get_file_size_str(file_size)
        self.sub_label = QLabel(f"Size: {size_str} · Ready to convert to {self.target_format}")
        self.sub_label.setStyleSheet("color: #9ca3af; font-size: 11px;")
        info_layout.addWidget(self.sub_label)

        layout.addLayout(info_layout, stretch=1)

        self.status_label = QLabel(f"Ready ({self.target_format})")
        self.status_label.setStyleSheet("color: #60cdff; font-weight: 500; font-size: 12px;")
        layout.addWidget(self.status_label)

        self.reveal_btn = QPushButton("📂")
        self.reveal_btn.setToolTip("Show in Explorer")
        self.reveal_btn.setFixedSize(30, 30)
        self.reveal_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reveal_btn.setVisible(False)
        self.reveal_btn.clicked.connect(self.reveal_in_explorer)
        layout.addWidget(self.reveal_btn)

        self.remove_btn = QPushButton("✕")
        self.remove_btn.setToolTip("Remove from queue")
        self.remove_btn.setFixedSize(30, 30)
        self.remove_btn.setStyleSheet("QPushButton { color: #e57373; font-weight: bold; } QPushButton:hover { background-color: #4a2828; }")
        self.remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remove_btn.clicked.connect(lambda: self.remove_requested.emit(self.filepath))
        layout.addWidget(self.remove_btn)

    def load_thumbnail(self):
        try:
            pixmap = QPixmap(self.filepath)
            if not pixmap.isNull():
                scaled = pixmap.scaled(44, 44, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                self.thumb_label.setPixmap(scaled)
            else:
                self.thumb_label.setText("🖼️")
        except Exception:
            self.thumb_label.setText("🖼️")

    def update_target_format(self, target_format: str):
        self.target_format = target_format
        if self.status == "pending":
            self.status_label.setText(f"Ready ({target_format})")
            file_size = os.path.getsize(self.filepath) if os.path.exists(self.filepath) else 0
            size_str = converter_engine.get_file_size_str(file_size)
            self.sub_label.setText(f"Size: {size_str} · Ready to convert to {target_format}")

    def set_converting(self):
        self.status = "converting"
        self.status_label.setText(f"⏳ Converting to {self.target_format}...")
        self.status_label.setStyleSheet("color: #ffd166; font-weight: 500; font-size: 12px;")
        self.remove_btn.setEnabled(False)

    def set_done(self, result: Dict[str, Any]):
        self.status = "done"
        self.output_path = result.get("output_path")
        out_size = result.get("output_size", 0)
        size_str = converter_engine.get_file_size_str(out_size)
        dims = result.get("dimensions", (0, 0))
        fmt = result.get("target_format", self.target_format)

        self.status_label.setText(f"✓ {fmt} ({size_str})")
        self.status_label.setStyleSheet("color: #4ade80; font-weight: 600; font-size: 12px;")
        self.sub_label.setText(f"{dims[0]}x{dims[1]} px · Saved: {Path(self.output_path).name}")
        self.reveal_btn.setVisible(True)
        self.remove_btn.setEnabled(True)

    def set_error(self, err_msg: str):
        self.status = "error"
        self.status_label.setText("✗ Failed")
        self.status_label.setStyleSheet("color: #f87171; font-weight: 600; font-size: 12px;")
        self.sub_label.setText(f"Error: {err_msg[:45]}...")
        self.remove_btn.setEnabled(True)

    def reveal_in_explorer(self):
        path_to_open = self.output_path if self.output_path and os.path.exists(self.output_path) else self.filepath
        if os.path.exists(path_to_open):
            subprocess.run(f'explorer /select,"{os.path.abspath(path_to_open)}"', shell=True)


class ConversionWorker(QThread):
    """Background worker thread for non-blocking batch conversion."""
    progress = pyqtSignal(int, int, str, dict)
    finished_all = pyqtSignal(int, int)

    def __init__(self, items: List[str], target_format: str, output_dir: str, quality: int, delete_original: bool, same_dir: bool):
        super().__init__()
        self.items = items
        self.target_format = target_format
        self.output_dir = output_dir
        self.quality = quality
        self.delete_original = delete_original
        self.same_dir = same_dir
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        total = len(self.items)
        successes = 0
        errors = 0

        for idx, filepath in enumerate(self.items, start=1):
            if self._is_cancelled:
                break

            target_folder = str(Path(filepath).parent) if self.same_dir else self.output_dir

            result = converter_engine.convert_image(
                input_path=filepath,
                output_dir=target_folder,
                target_format=self.target_format,
                quality=self.quality,
                delete_original=self.delete_original
            )

            if result.get("success"):
                successes += 1
            else:
                errors += 1

            self.progress.emit(idx, total, filepath, result)

        self.finished_all.emit(successes, errors)


class PixShiftApp(QMainWindow):
    """Main Application Window for PixShift."""

    def __init__(self, initial_files: Optional[List[str]] = None):
        super().__init__()
        self.setWindowTitle("PixShift Image Converter")
        self.resize(880, 720)
        self.setMinimumSize(740, 560)

        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.current_target_format = "JPG"
        self.file_queue: List[str] = []
        self.item_widgets: Dict[str, FileItemWidget] = {}
        self.current_output_dir = converter_engine.get_default_downloads_folder()
        self.worker: Optional[ConversionWorker] = None

        self.init_ui()
        self.setStyleSheet(WINDOWS_11_QSS)

        if initial_files:
            self.add_files(initial_files)

    def init_ui(self):
        central = QWidget(self)
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(18, 16, 18, 16)
        main_layout.setSpacing(12)

        # --- Header Section ---
        header_layout = QHBoxLayout()
        header_title = QLabel("⚡ PixShift")
        header_title.setStyleSheet("font-size: 20px; font-weight: 700; color: #ffffff;")
        header_layout.addWidget(header_title)

        ver_badge = QLabel(f"v{updater.get_current_version()}")
        ver_badge.setStyleSheet("background-color: #27282f; color: #60cdff; font-size: 11px; padding: 4px 8px; border-radius: 6px; font-weight: bold; border: 1px solid #363843;")
        header_layout.addWidget(ver_badge)

        header_layout.addStretch()

        self.btn_update = QPushButton("🔄 Check for Updates")
        self.btn_update.setObjectName("HeaderButton")
        self.btn_update.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_update.clicked.connect(self.show_update_dialog)
        header_layout.addWidget(self.btn_update)

        main_layout.addLayout(header_layout)

        # --- Target Format Segmented Tab Bar ---
        format_bar_layout = QHBoxLayout()
        format_bar_layout.setSpacing(10)

        fmt_label = QLabel("Convert To:")
        fmt_label.setStyleSheet("font-weight: 700; color: #e5e7eb; font-size: 13px;")
        format_bar_layout.addWidget(fmt_label)

        tab_container = QFrame()
        tab_container.setObjectName("FormatTabContainer")
        tab_layout = QHBoxLayout(tab_container)
        tab_layout.setContentsMargins(3, 3, 3, 3)
        tab_layout.setSpacing(4)

        self.tab_group = QButtonGroup(self)
        self.tab_group.setExclusive(True)

        self.tab_jpg = QPushButton("🖼️ JPG (Default)")
        self.tab_jpg.setProperty("class", "FormatTab")
        self.tab_jpg.setCheckable(True)
        self.tab_jpg.setChecked(True)
        self.tab_jpg.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tab_group.addButton(self.tab_jpg)
        tab_layout.addWidget(self.tab_jpg)

        self.tab_webp = QPushButton("🌐 WEBP")
        self.tab_webp.setProperty("class", "FormatTab")
        self.tab_webp.setCheckable(True)
        self.tab_webp.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tab_group.addButton(self.tab_webp)
        tab_layout.addWidget(self.tab_webp)

        self.tab_avif = QPushButton("⚡ AVIF")
        self.tab_avif.setProperty("class", "FormatTab")
        self.tab_avif.setCheckable(True)
        self.tab_avif.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tab_group.addButton(self.tab_avif)
        tab_layout.addWidget(self.tab_avif)

        self.tab_jpg.clicked.connect(lambda: self.on_format_tab_changed("JPG"))
        self.tab_webp.clicked.connect(lambda: self.on_format_tab_changed("WEBP"))
        self.tab_avif.clicked.connect(lambda: self.on_format_tab_changed("AVIF"))

        format_bar_layout.addWidget(tab_container)

        self.format_desc_label = QLabel("High-compatibility sRGB JPEG")
        self.format_desc_label.setStyleSheet("color: #9ca3af; font-size: 12px; margin-left: 8px;")
        format_bar_layout.addWidget(self.format_desc_label, stretch=1)

        main_layout.addLayout(format_bar_layout)

        # --- Drop Zone ---
        self.drop_zone = DropZoneWidget(self)
        self.drop_zone.files_dropped.connect(self.add_files)
        self.drop_zone.clicked.connect(self.browse_files_dialog)
        main_layout.addWidget(self.drop_zone)

        # --- Settings & Options Card ---
        settings_card = QFrame()
        settings_card.setObjectName("SettingsCard")
        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setContentsMargins(14, 10, 14, 10)
        settings_layout.setSpacing(10)

        # Row 1: Destination Folder
        dest_row = QHBoxLayout()
        dest_row.setSpacing(10)

        dest_icon = QLabel("📁")
        dest_icon.setStyleSheet("font-size: 16px;")
        dest_row.addWidget(dest_icon)

        dest_label = QLabel("Save to:")
        dest_label.setStyleSheet("font-weight: 600; color: #ffffff;")
        dest_row.addWidget(dest_label)

        self.dest_path_label = QLabel(self.current_output_dir)
        self.dest_path_label.setStyleSheet("color: #60cdff; font-family: monospace; font-size: 12px; background-color: #1a1b1f; padding: 4px 8px; border-radius: 6px; border: 1px solid #363842;")
        self.dest_path_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        dest_row.addWidget(self.dest_path_label, stretch=1)

        self.btn_change_dest = QPushButton("Change Folder...")
        self.btn_change_dest.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_change_dest.clicked.connect(self.browse_destination_folder)
        dest_row.addWidget(self.btn_change_dest)

        self.btn_open_dest = QPushButton("Open Folder")
        self.btn_open_dest.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_dest.clicked.connect(self.open_current_output_dir)
        dest_row.addWidget(self.btn_open_dest)

        settings_layout.addLayout(dest_row)

        # Row 2: Options (Delete Original & Same Folder)
        opts_row = QHBoxLayout()
        opts_row.setSpacing(20)

        self.chk_delete_orig = QCheckBox("🗑️ Delete original file after conversion")
        self.chk_delete_orig.setToolTip("Safely moves original image(s) to Windows Recycle Bin once converted")
        self.chk_delete_orig.setCursor(Qt.CursorShape.PointingHandCursor)
        opts_row.addWidget(self.chk_delete_orig)

        self.chk_same_folder = QCheckBox("Save alongside original file")
        self.chk_same_folder.setToolTip("Places each converted image in the same folder where the source image came from")
        self.chk_same_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_same_folder.toggled.connect(self.toggle_same_folder)
        opts_row.addWidget(self.chk_same_folder)

        opts_row.addStretch()
        settings_layout.addLayout(opts_row)

        # Row 3: Quality Slider
        qual_row = QHBoxLayout()
        qual_row.setSpacing(12)

        self.qual_title_label = QLabel("JPG Quality:")
        self.qual_title_label.setStyleSheet("font-weight: 600; color: #ffffff;")
        qual_row.addWidget(self.qual_title_label)

        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(40, 100)
        self.quality_slider.setValue(92)
        self.quality_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.quality_slider.valueChanged.connect(self.on_quality_changed)
        qual_row.addWidget(self.quality_slider, stretch=1)

        self.quality_val_label = QLabel("92% (High Quality)")
        self.quality_val_label.setStyleSheet("color: #60cdff; font-weight: bold; min-width: 120px;")
        qual_row.addWidget(self.quality_val_label)

        for name, val in [("Max 100%", 100), ("High 92%", 92), ("Standard 80%", 80), ("Small 70%", 70)]:
            p_btn = QPushButton(name)
            p_btn.setObjectName("PresetButton")
            p_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            p_btn.clicked.connect(lambda checked, v=val: self.quality_slider.setValue(v))
            qual_row.addWidget(p_btn)

        settings_layout.addLayout(qual_row)
        main_layout.addWidget(settings_card)

        # --- Queue List Area ---
        list_header = QHBoxLayout()
        self.queue_count_label = QLabel("Queue (0 files)")
        self.queue_count_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #ffffff;")
        list_header.addWidget(self.queue_count_label)
        list_header.addStretch()

        self.btn_clear_all = QPushButton("Clear All")
        self.btn_clear_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_all.clicked.connect(self.clear_queue)
        self.btn_clear_all.setEnabled(False)
        list_header.addWidget(self.btn_clear_all)

        main_layout.addLayout(list_header)

        self.list_widget = QListWidget()
        self.list_widget.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        main_layout.addWidget(self.list_widget, stretch=1)

        # --- Bottom Action Bar ---
        bottom_bar = QVBoxLayout()
        bottom_bar.setSpacing(8)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        bottom_bar.addWidget(self.progress_bar)

        action_row = QHBoxLayout()
        action_row.setSpacing(12)

        self.status_summary_label = QLabel("Add images to begin")
        self.status_summary_label.setStyleSheet("color: #9ca3af; font-size: 13px;")
        action_row.addWidget(self.status_summary_label, stretch=1)

        self.btn_convert = QPushButton("🚀 Convert to JPG")
        self.btn_convert.setObjectName("PrimaryButton")
        self.btn_convert.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_convert.setEnabled(False)
        self.btn_convert.clicked.connect(self.start_conversion)
        action_row.addWidget(self.btn_convert)

        bottom_bar.addLayout(action_row)
        main_layout.addLayout(bottom_bar)

    def on_format_tab_changed(self, fmt: str):
        self.current_target_format = fmt
        self.qual_title_label.setText(f"{fmt} Quality:")

        fmt_desc = {
            "JPG": "High-compatibility sRGB JPEG (composites transparency over white)",
            "WEBP": "Lightweight Google WebP format (preserves alpha transparency)",
            "AVIF": "Next-Gen AV1 Image File (ultra-high compression, preserves alpha)"
        }.get(fmt, "")
        self.format_desc_label.setText(fmt_desc)

        # Update queue items
        for w in self.item_widgets.values():
            w.update_target_format(fmt)

        self.update_queue_status()

    def show_update_dialog(self):
        dlg = UpdateDialog(self)
        dlg.exec()

    def on_quality_changed(self, val: int):
        if val >= 96:
            desc = "Maximum"
        elif val >= 88:
            desc = "High Quality"
        elif val >= 76:
            desc = "Balanced"
        else:
            desc = "Compressed"
        self.quality_val_label.setText(f"{val}% ({desc})")

    def toggle_same_folder(self, checked: bool):
        self.btn_change_dest.setEnabled(not checked)
        if checked:
            self.dest_path_label.setText("[Same as original image]")
        else:
            self.dest_path_label.setText(self.current_output_dir)

    def browse_destination_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            f"Select Output Folder for Converted {self.current_target_format}s",
            self.current_output_dir
        )
        if folder:
            self.current_output_dir = folder
            self.dest_path_label.setText(folder)

    def open_current_output_dir(self):
        if os.path.exists(self.current_output_dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.current_output_dir))

    def browse_files_dialog(self):
        exts = " ".join([f"*{ext}" for ext in sorted(converter_engine.SUPPORTED_EXTENSIONS)])
        filter_str = f"All Supported Images ({exts});;All Files (*.*)"

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images to Convert",
            str(Path.home()),
            filter_str
        )
        if files:
            self.add_files(files)

    def add_files(self, filepaths: List[str]):
        for fp in filepaths:
            norm_fp = os.path.abspath(fp)
            if norm_fp in self.file_queue:
                continue
            if not converter_engine.is_supported_image(norm_fp):
                continue

            self.file_queue.append(norm_fp)
            item_widget = FileItemWidget(norm_fp, target_format=self.current_target_format)
            item_widget.remove_requested.connect(self.remove_file)

            list_item = QListWidgetItem(self.list_widget)
            list_item.setSizeHint(QSize(0, 56))
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, item_widget)

            self.item_widgets[norm_fp] = item_widget

        self.update_queue_status()

    def remove_file(self, filepath: str):
        if filepath in self.file_queue:
            idx = self.file_queue.index(filepath)
            self.file_queue.remove(filepath)
            item = self.list_widget.takeItem(idx)
            del item
            if filepath in self.item_widgets:
                del self.item_widgets[filepath]
            self.update_queue_status()

    def clear_queue(self):
        self.file_queue.clear()
        self.item_widgets.clear()
        self.list_widget.clear()
        self.update_queue_status()

    def update_queue_status(self):
        count = len(self.file_queue)
        self.queue_count_label.setText(f"Queue ({count} file{'s' if count != 1 else ''})")
        self.btn_clear_all.setEnabled(count > 0)
        self.btn_convert.setEnabled(count > 0)

        fmt = self.current_target_format
        if count == 0:
            self.status_summary_label.setText("Drop or import images above to begin")
            self.btn_convert.setText(f"🚀 Convert to {fmt}")
        else:
            total_size = sum([os.path.getsize(f) for f in self.file_queue if os.path.exists(f)])
            size_str = converter_engine.get_file_size_str(total_size)
            self.status_summary_label.setText(f"{count} image(s) ready · Total {size_str}")
            self.btn_convert.setText(f"🚀 Convert {count} Image{'s' if count != 1 else ''} to {fmt}")

    def start_conversion(self):
        if not self.file_queue:
            return

        self.btn_convert.setEnabled(False)
        self.btn_clear_all.setEnabled(False)
        self.drop_zone.setEnabled(False)

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(self.file_queue))
        self.progress_bar.setValue(0)

        for w in self.item_widgets.values():
            w.set_converting()

        self.worker = ConversionWorker(
            items=list(self.file_queue),
            target_format=self.current_target_format,
            output_dir=self.current_output_dir,
            quality=self.quality_slider.value(),
            delete_original=self.chk_delete_orig.isChecked(),
            same_dir=self.chk_same_folder.isChecked()
        )
        self.worker.progress.connect(self.on_item_converted)
        self.worker.finished_all.connect(self.on_conversion_finished)
        self.worker.start()

    def on_item_converted(self, idx: int, total: int, filepath: str, result: Dict[str, Any]):
        self.progress_bar.setValue(idx)
        self.status_summary_label.setText(f"Converting ({idx}/{total}): {Path(filepath).name}...")

        widget = self.item_widgets.get(filepath)
        if widget:
            if result.get("success"):
                widget.set_done(result)
            else:
                widget.set_error(result.get("error", "Unknown error"))

    def on_conversion_finished(self, successes: int, errors: int):
        self.btn_convert.setEnabled(True)
        self.btn_clear_all.setEnabled(True)
        self.drop_zone.setEnabled(True)
        self.progress_bar.setVisible(False)

        total = successes + errors
        fmt = self.current_target_format
        msg = f"Done! {successes} of {total} images successfully converted to {fmt}."
        if errors > 0:
            msg += f" ({errors} failed)"

        self.status_summary_label.setText(msg)

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Conversion Complete")
        msg_box.setText(f"🎉 Successfully converted {successes} image(s) to {fmt}!")
        
        target_dir = self.current_output_dir if not self.chk_same_folder.isChecked() else "original folders"
        msg_box.setInformativeText(f"Saved to: {target_dir}")
        
        open_btn = msg_box.addButton("📂 Open Output Folder", QMessageBox.ButtonRole.AcceptRole)
        msg_box.addButton("Close", QMessageBox.ButtonRole.RejectRole)
        
        msg_box.exec()
        if msg_box.clickedButton() == open_btn:
            self.open_current_output_dir()


# Compatibility alias
QuickJPGApp = PixShiftApp

