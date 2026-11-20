"""
neural_workspace.py - Neural Workspace Expansion ("Extend" Mode)
Floating Translucent Glass Windows (NP, AI, ANY) with 60 FPS Bezier Neural Tethers
Windows 11 Dynamic Island Desktop Companion
"""

import os
import sys
import time
import math
import logging
import subprocess
import ctypes
from ctypes import wintypes
from PySide6.QtCore import (
    Qt,
    QRect,
    QRectF,
    QPoint,
    QPointF,
    Signal,
    QTimer,
    QEasingCurve,
    QProcess,
    QObject,
)
from PySide6.QtGui import (
    QPainter,
    QColor,
    QBrush,
    QPen,
    QFont,
    QPainterPath,
    QLinearGradient,
    QGuiApplication,
    QMouseEvent,
    QWindow,
    QDragEnterEvent,
    QDropEvent,
)
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QPlainTextEdit,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QFrame,
    QGraphicsDropShadowEffect,
    QComboBox,
    QStackedWidget,
)

from ai_workers import (
    OpenRouterChatWorker,
    OpenRouterKeyInfoWorker,
    OpenRouterTelemetryTracker,
    DEFAULT_OPENROUTER_KEY,
)
from widgets_panel import GlassButton, get_editorial_font
from theme_misty_sage import (
    GRAD_TOP,
    GRAD_MID,
    GRAD_BOT,
    BG_PARCHMENT,
    BG_PARCHMENT_LIGHT,
    BG_PINE_SLATE,
    BG_PINE_PLATE,
    BG_WELL_PINE,
    BG_WHITE,
    BOT_BG,
    BORDER_MUTED,
    BORDER_DARK,
    BORDER_CAPSULE,
    ACCENT_TERRACOTTA,
    ACCENT_SIENNA,
    ACCENT_PRESSED,
    ACCENT_AMBER,
    ACCENT_MAHOGANY,
    ACCENT_SAGE,
    TEXT_WHITE,
    TEXT_CHARCOAL,
    TEXT_LIGHT,
    TEXT_MUTED,
    TEXT_FAINT,
    TETHER_BLACK,
    COLOR_GRAD_TOP,
    COLOR_GRAD_MID,
    COLOR_GRAD_BOT,
    COLOR_PARCHMENT,
    COLOR_PARCHMENT_LIGHT,
    COLOR_PINE_SLATE,
    COLOR_PINE_PLATE,
    COLOR_WHITE,
    COLOR_BOT_BG,
    COLOR_BORDER_MUTED,
    COLOR_BORDER_CAPSULE,
    COLOR_TERRACOTTA,
    COLOR_SIENNA,
    COLOR_AMBER,
    COLOR_MAHOGANY,
    COLOR_SAGE,
    COLOR_TEXT_CHARCOAL,
    COLOR_TEXT_WHITE,
    COLOR_TETHER_BLACK,
    get_display_font,
    get_nav_pill_font,
    get_body_font,
    get_retro_swiss_font,
    TERRACOTTA_BTN_QSS,
    PINE_PILL_BTN_QSS,
    PARCHMENT_INPUT_QSS,
    PARCHMENT_TEXTEDIT_QSS,
    MISTY_SCROLL_QSS,
    MISTY_MENU_QSS,
    create_atmospheric_gradient,
    draw_misty_capsule,
    # Backward compatibility aliases
    BG_CANVAS,
    BG_BEIGE,
    BG_WELL,
    BG_CARD,
    INK_BLACK,
    INK_MUTED,
    BORDER_STRUCT,
    BEVEL_LIGHT,
    BEVEL_DARK,
    BEVEL_DEPRESSED,
    ACCENT_RED,
    ACCENT_RED_HOVER,
    ACCENT_RED_PRESSED,
    ACCENT_BLUE,
    ACCENT_GREEN,
    COLOR_BG_CANVAS,
    COLOR_BG_CARD,
    COLOR_BG_WELL,
    COLOR_INK_BLACK,
    COLOR_ACCENT_RED,
    COLOR_ACCENT_BLUE,
    COLOR_ACCENT_GREEN,
    COLOR_BEVEL_LIGHT,
    COLOR_BEVEL_DARK,
    SWISS_BTN_RED_QSS,
    SWISS_BTN_BEIGE_QSS,
    SWISS_INPUT_QSS,
    SWISS_TEXTEDIT_QSS,
    SWISS_SCROLL_QSS,
    SWISS_MENU_QSS,
    draw_retro_bevel,
)

logger = logging.getLogger("NeuralWorkspace")


# =========================================================================
# Base Floating Glass Node Window with Free-Roam Dragging
# =========================================================================

class FloatingNodeWindow(QWidget):
    """
    Base floating window for neural workspace nodes (NP, AI, ANY).
    Matches Translucent Frosted-Glass & Italic Bold Editorial aesthetic:
    - Base fill: rgba(18, 22, 30, 0.85)
    - Specular rim: 1.2px rgba(255, 255, 255, 0.28)
    - Corner radius: 18px
    - Free-roam dragging: Right-click hold anywhere OR Left-click drag on header bar.
    - Emits windowMoved on move and closed on close.
    """
    windowMoved = Signal()
    closed = Signal()
    plusClicked = Signal()

    def __init__(self, node_id: str, title: str, width: int = 270, height: int = 360, parent=None):
        super().__init__(parent)
        self.node_id = node_id
        self.node_title = title
        self._target_w = width
        self._target_h = height

        # Window Flags & Attributes
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(width, height)

        # Ambient glass elevation shadow
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(28)
        self._shadow.setColor(QColor(0, 0, 0, 190))
        self._shadow.setOffset(0, 8)
        self.setGraphicsEffect(self._shadow)

        # Dragging state
        self._is_dragging = False
        self._drag_start_pos = QPoint()

        # Build shell layout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(14, 12, 14, 14)
        self._main_layout.setSpacing(10)

        # Header Bar
        self.header_widget = QWidget(self)
        self.header_widget.setFixedHeight(28)
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(8)

        # Node badge (e.g. NP, AI, DASH)
        self.badge_lbl = QLabel(node_id, self.header_widget)
        self.badge_lbl.setFont(get_nav_pill_font(size=7.5, weight=QFont.Bold, wide_spacing=False))
        self.badge_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {BG_PINE_PLATE};
                color: #FFFFFF;
                border: 1px solid {BORDER_MUTED};
                border-radius: 3px;
                padding: 1px 6px;
            }}
        """)
        self.header_layout.addWidget(self.badge_lbl)

        # Window Title in Display Header font
        self.title_lbl = QLabel(title, self.header_widget)
        self.title_lbl.setFont(get_display_font(size=10.5, weight=QFont.Black))
        self.title_lbl.setStyleSheet("color: #FFFFFF;")
        self.header_layout.addWidget(self.title_lbl)
        self.header_layout.addStretch(1)

        # Plus button (+) to expand / add extra extension tab/window (up to 6)
        self.btn_plus = QPushButton("+", self.header_widget)
        self.btn_plus.setFixedSize(22, 22)
        self.btn_plus.setCursor(Qt.PointingHandCursor)
        self.btn_plus.setFont(get_display_font(size=11.5, weight=QFont.Black))
        self.btn_plus.setToolTip("Add new extension window (up to 6)")
        self.btn_plus.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_PARCHMENT};
                color: {TEXT_CHARCOAL};
                border: 1.2px solid {BORDER_MUTED};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {ACCENT_TERRACOTTA};
                color: #FFFFFF;
                border-color: {ACCENT_MAHOGANY};
            }}
            QPushButton:pressed {{
                background-color: {ACCENT_PRESSED};
            }}
        """)
        self.btn_plus.clicked.connect(self.plusClicked.emit)
        self.header_layout.addWidget(self.btn_plus)

        # Close button (×) - Tactile Pill Bevel
        self.btn_close = QPushButton("×", self.header_widget)
        self.btn_close.setFixedSize(22, 22)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setFont(get_display_font(size=11.0, weight=QFont.Black))
        self.btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_PARCHMENT};
                color: {TEXT_CHARCOAL};
                border: 1.2px solid {BORDER_MUTED};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {ACCENT_TERRACOTTA};
                color: #FFFFFF;
                border-color: {ACCENT_MAHOGANY};
            }}
            QPushButton:pressed {{
                background-color: {ACCENT_PRESSED};
            }}
        """)
        self.btn_close.clicked.connect(self.close_node)
        self.header_layout.addWidget(self.btn_close)

        self._main_layout.addWidget(self.header_widget)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        rect = QRectF(1.0, 1.0, self.width() - 2.0, self.height() - 2.0)
        radius = 8.0

        # Atmospheric Sage-to-Sand Gradient
        grad = create_atmospheric_gradient(rect)
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(COLOR_BORDER_CAPSULE, 1.5))
        painter.drawRoundedRect(rect, radius, radius)

        # Soft 1px inner mist highlight top-left
        inner_rect = rect.adjusted(1.5, 1.5, -1.5, -1.5)
        painter.setPen(QPen(QColor(255, 255, 255, 120), 1.0))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(inner_rect, max(2.0, radius - 1.5), max(2.0, radius - 1.5))

    def mousePressEvent(self, event: QMouseEvent):
        # Right-click hold anywhere OR Left-click on header area enables free-roam drag
        if event.button() == Qt.RightButton or (event.button() == Qt.LeftButton and event.position().y() <= 38):
            self._is_dragging = True
            self._drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_dragging:
            new_pos = event.globalPosition().toPoint() - self._drag_start_pos
            # Minimal screen boundary clamping so header stays reachable
            screen = QGuiApplication.primaryScreen()
            if screen:
                geom = screen.availableGeometry()
                new_pos.setX(max(geom.left() - self.width() + 60, min(geom.right() - 60, new_pos.x())))
                new_pos.setY(max(geom.top() + 8, min(geom.bottom() - 40, new_pos.y())))
            self.move(new_pos)
            self.windowMoved.emit()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._is_dragging:
            self._is_dragging = False
            self.windowMoved.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def close_node(self):
        self.hide()
        self.closed.emit()

    def close_window(self):
        self.close_node()

    def get_anchor_point(self, reference_pt: QPointF) -> QPointF:
        """
        Dynamically returns the best edge anchor point (top-center, bottom-center,
        or side) relative to the main Dynamic Island reference point.
        """
        geo = self.geometry()
        top_center = QPointF(geo.x() + geo.width() / 2.0, geo.y())
        bottom_center = QPointF(geo.x() + geo.width() / 2.0, geo.y() + geo.height())

        # If window is below island, tether attaches to top-center
        if geo.y() >= reference_pt.y():
            return top_center
        # If window is dragged above island, tether attaches to bottom-center
        return bottom_center


# =========================================================================
# Left Window: NP (Quick Notepad Editor)
# =========================================================================

class NotepadNodeWindow(FloatingNodeWindow):
    """
    Left Node: Quick Notepad Editor (310px × 412px, +30% scaled area).
    Distraction-free text editing with live word/character counters,
    one-click copy and clear actions, and auto-saving to local disk.
    """
    def __init__(self, parent=None):
        super().__init__(node_id="NP", title="Quick Notepad", width=310, height=412, parent=parent)
        self.notes_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "workspace_np_notes.txt"
        )

        # Header Action Icons
        btn_copy = GlassButton(icon_text="📋", parent=self.header_widget, is_pill=False, size_override=(22, 22))
        btn_copy.setToolTip("Copy all text to clipboard")
        btn_copy.clicked.connect(self._copy_all)
        self.header_layout.insertWidget(self.header_layout.count() - 1, btn_copy)

        btn_clear = GlassButton(icon_text="🧹", parent=self.header_widget, is_pill=False, size_override=(22, 22))
        btn_clear.setToolTip("Clear notepad")
        btn_clear.clicked.connect(self._clear_text)
        self.header_layout.insertWidget(self.header_layout.count() - 1, btn_clear)

        # Archival Editor Area
        self.editor = QPlainTextEdit(self)
        self.editor.setFont(get_body_font(size=9.2, weight=QFont.Normal, mono=True))
        self.editor.setStyleSheet(PARCHMENT_TEXTEDIT_QSS)
        self.editor.setPlaceholderText("Jot down quick thoughts, lecture notes, or paste code snippets here...")
        self.editor.textChanged.connect(self._on_text_changed)
        self._main_layout.addWidget(self.editor, stretch=1)

        # Bottom Counter & Status Bar
        bot_bar = QHBoxLayout()
        bot_bar.setContentsMargins(2, 0, 2, 0)

        self.lbl_counter = QLabel("0 words • 0 chars", self)
        self.lbl_counter.setFont(get_body_font(size=8.2, weight=QFont.Medium))
        self.lbl_counter.setStyleSheet(f"color: {TEXT_MUTED};")
        bot_bar.addWidget(self.lbl_counter)
        bot_bar.addStretch(1)

        btn_time = GlassButton(icon_text="🕒 Time", parent=self, is_pill=True)
        btn_time.setFixedHeight(22)
        btn_time.setFont(get_nav_pill_font(size=7.5, weight=QFont.Bold))
        btn_time.clicked.connect(self._insert_timestamp)
        bot_bar.addWidget(btn_time)

        self._main_layout.addLayout(bot_bar)

        # Load existing notes
        self._load_saved_notes()

    def _on_text_changed(self):
        text = self.editor.toPlainText()
        words = len(text.split()) if text.strip() else 0
        chars = len(text)
        self.lbl_counter.setText(f"{words} words • {chars} chars")
        try:
            with open(self.notes_file, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception:
            pass

    def _load_saved_notes(self):
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, "r", encoding="utf-8") as f:
                    self.editor.setPlainText(f.read())
            except Exception:
                pass

    def _copy_all(self):
        txt = self.editor.toPlainText()
        if txt:
            QGuiApplication.clipboard().setText(txt)
            self.lbl_counter.setText("Copied to clipboard!")
            QTimer.singleShot(1400, self._on_text_changed)

    def _clear_text(self):
        self.editor.clear()

    def _insert_timestamp(self):
        ts = time.strftime("[%I:%M %p] ")
        self.editor.insertPlainText(ts)


# =========================================================================
# Center Window: AI (OpenRouter Neural Chat Studio)
# =========================================================================

class AIChatNodeWindow(FloatingNodeWindow):
    """
    Center Node: OpenRouter Neural Chat Studio (436px × 504px, +30% scaled area).
    Focal window with structured Node-Stream Chat cards (cyan prompt cards,
    violet response cards), code copy buttons, and model selector.
    """
    def __init__(self, parent=None):
        super().__init__(node_id="AI", title="Neural Chat Studio", width=436, height=504, parent=parent)
        self._chat_worker = None

        # Model Selector Pill in Header - Misty Sage Styling
        self.model_combo = QComboBox(self.header_widget)
        self.model_combo.addItems(["openai/gpt-4o-mini", "anthropic/claude-3.5-sonnet", "google/gemini-2.0-flash-001"])
        self.model_combo.setFixedHeight(22)
        self.model_combo.setFont(get_nav_pill_font(size=7.5, weight=QFont.Bold, wide_spacing=False))
        self.model_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {BG_PARCHMENT};
                color: {TEXT_CHARCOAL};
                border: 1.2px solid {BORDER_MUTED};
                border-radius: 4px;
                padding: 1px 6px;
                font-weight: 700;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {BG_PARCHMENT};
                color: {TEXT_CHARCOAL};
                selection-background-color: {ACCENT_TERRACOTTA};
                selection-color: #FFFFFF;
                border: 1.2px solid {BORDER_MUTED};
            }}
        """)
        self.header_layout.insertWidget(self.header_layout.count() - 1, self.model_combo)

        # Clear Chat Button
        btn_clear = GlassButton(icon_text="🧹", parent=self.header_widget, is_pill=False, size_override=(22, 22))
        btn_clear.setToolTip("Clear chat messages")
        btn_clear.clicked.connect(self._clear_chat)
        self.header_layout.insertWidget(self.header_layout.count() - 1, btn_clear)

        # Scrollable Chat Stream Container
        self.stream_container = QWidget(self)
        self.stream_layout = QVBoxLayout(self.stream_container)
        self.stream_layout.setContentsMargins(2, 4, 2, 4)
        self.stream_layout.setSpacing(8)
        self.stream_layout.setAlignment(Qt.AlignTop)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.stream_container)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(MISTY_SCROLL_QSS)
        self._main_layout.addWidget(self.scroll_area, stretch=1)

        # Bottom Input Row
        in_row = QHBoxLayout()
        in_row.setSpacing(6)

        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Ask neural assistant anything...")
        self.input_field.setFont(get_body_font(size=9.2, weight=QFont.Normal))
        self.input_field.setStyleSheet(PARCHMENT_INPUT_QSS)
        self.input_field.returnPressed.connect(self._send_prompt)
        in_row.addWidget(self.input_field, stretch=1)

        self.btn_send = GlassButton(icon_text="⚡ ASK", parent=self, is_pill=True, is_accent=True)
        self.btn_send.setFixedSize(62, 28)
        self.btn_send.clicked.connect(self._send_prompt)
        in_row.addWidget(self.btn_send)

        self._main_layout.addLayout(in_row)

        # Welcome Card
        self._add_ai_card("👋 Welcome to the **Neural Chat Studio**. Ask questions, debug code, or brainstorm ideas with real-time streaming.")

    def _send_prompt(self):
        prompt = self.input_field.text().strip()
        if not prompt:
            return
        self.input_field.clear()

        # Add user prompt card (Terracotta Rust left accent bar)
        self._add_user_card(prompt)

        # Prepare AI response card (Pine Slate left accent bar)
        ai_card = self._add_ai_card("Thinking...")

        # Start OpenRouter worker
        model_name = self.model_combo.currentText()
        self._chat_worker = OpenRouterChatWorker(
            question=prompt,
            model_name=model_name,
            api_key=DEFAULT_OPENROUTER_KEY,
            stream=True,
            parent=self
        )
        self._chat_worker.chunk_received.connect(lambda text, card=ai_card: self._update_ai_card(card, text))
        self._chat_worker.finished.connect(lambda text, success, card=ai_card: self._finish_ai_card(card, text, success))
        self._chat_worker.start()

    def _add_user_card(self, text: str):
        card = QFrame(self.stream_container)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_WHITE};
                border: 1.2px solid {BORDER_MUTED};
                border-left: 3.5px solid {ACCENT_TERRACOTTA};
                border-radius: 4px;
                padding: 4px;
            }}
        """)
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(8, 6, 8, 6)

        lbl = QLabel(text, card)
        lbl.setWordWrap(True)
        lbl.setFont(get_display_font(size=9.2, weight=QFont.Bold))
        lbl.setStyleSheet(f"color: {TEXT_CHARCOAL}; border: none; background: transparent;")
        c_lay.addWidget(lbl)

        self.stream_layout.addWidget(card)
        self._scroll_to_bottom()
        return card

    def _add_ai_card(self, initial_text: str):
        card = QFrame(self.stream_container)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_PARCHMENT};
                border: 1.2px solid {BORDER_MUTED};
                border-left: 3.5px solid {BORDER_DARK};
                border-radius: 4px;
                padding: 4px;
            }}
        """)
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(8, 6, 8, 6)
        c_lay.setSpacing(4)

        lbl = QLabel(initial_text, card)
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lbl.setFont(get_body_font(size=9.0, weight=QFont.Normal))
        lbl.setStyleSheet(f"color: {TEXT_CHARCOAL}; border: none; background: transparent; line-height: 1.35;")
        c_lay.addWidget(lbl)

        # Action row with Copy Code / Copy Response
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_copy = GlassButton(icon_text="📋 Copy", parent=card, is_pill=True)
        btn_copy.setFixedHeight(20)
        btn_copy.setFont(get_nav_pill_font(size=7.5, weight=QFont.Bold))
        btn_copy.clicked.connect(lambda: QGuiApplication.clipboard().setText(lbl.text()))
        btn_row.addWidget(btn_copy)
        c_lay.addLayout(btn_row)

        card.lbl_content = lbl
        self.stream_layout.addWidget(card)
        self._scroll_to_bottom()
        return card

    def _update_ai_card(self, card, text: str):
        if hasattr(card, "lbl_content"):
            card.lbl_content.setText(text)
            self._scroll_to_bottom()

    def _finish_ai_card(self, card, text: str, success: bool):
        if hasattr(card, "lbl_content"):
            card.lbl_content.setText(text if success else f"Error: {text}")
            self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        QTimer.singleShot(20, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))

    def _clear_chat(self):
        while self.stream_layout.count():
            item = self.stream_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._add_ai_card("👋 Chat cleared. Ready for your next query.")


# =========================================================================
# Right Window: OpenRouter Live Telemetry Dashboard
# =========================================================================

class TokenSplitBar(QWidget):
    """
    Visual horizontal split progress bar showing Prompt Tokens (Warm Amber #E88D5A)
    vs Completion Tokens (Terracotta Rust #B83B24) encased in a subtle border.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.prompt_ratio = 0.65

    def set_tokens(self, p_tok: int, c_tok: int):
        total = p_tok + c_tok
        if total > 0:
            self.prompt_ratio = p_tok / float(total)
        else:
            self.prompt_ratio = 0.65
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        w = float(self.width())
        h = float(self.height())

        # Background track in Parchment
        painter.setBrush(QBrush(COLOR_PARCHMENT))
        painter.setPen(QPen(COLOR_BORDER_MUTED, 1.2))
        painter.drawRect(QRectF(0, 0, w - 1.0, h - 1.0))

        if self.prompt_ratio > 0.0:
            pw = max(4.0, (w - 1.0) * self.prompt_ratio)
            painter.setBrush(QBrush(COLOR_AMBER))
            painter.setPen(Qt.NoPen)
            painter.drawRect(QRectF(0.5, 0.5, pw, h - 1.0))

        if self.prompt_ratio < 1.0:
            cw = (w - 1.0) * (1.0 - self.prompt_ratio)
            cx = (w - 1.0) - cw
            painter.setBrush(QBrush(COLOR_TERRACOTTA))
            painter.setPen(Qt.NoPen)
            painter.drawRect(QRectF(cx, 0.5, cw, h - 1.0))


class OpenRouterDashboardWindow(FloatingNodeWindow):
    """
    Right Node: OpenRouter Live Telemetry Dashboard (310px × 412px, +30% scaled area).
    Symmetrical to NP. Real-time API monitoring hub:
    - Live Token & Cost Tracking (Prompt vs. Completion, USD cost, wallet balance)
    - Performance Metrics (Average latency in ms, Requests-Per-Minute RPM)
    - Model Status Toggles (Operational status, latency, context window, active toggles)
    """
    def __init__(self, parent=None):
        super().__init__(node_id="DASH", title="Live Telemetry", width=310, height=412, parent=parent)
        self._key_worker = None

        # Style DASH badge with Forest Sage
        self.badge_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {ACCENT_SAGE};
                color: #FFFFFF;
                border: 1px solid {BORDER_MUTED};
                border-radius: 3px;
                padding: 1px 6px;
            }}
        """)

        # Header action buttons: Refresh live stats
        btn_refresh = GlassButton(icon_text="🔄", parent=self.header_widget, is_pill=False, size_override=(22, 22))
        btn_refresh.setToolTip("Sync live balance & metrics from OpenRouter")
        btn_refresh.clicked.connect(self.refresh_telemetry)
        self.header_layout.insertWidget(self.header_layout.count() - 1, btn_refresh)

        # Scroll Area for clean structured cards layout
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(MISTY_SCROLL_QSS)

        self.dash_container = QWidget(self)
        self.dash_layout = QVBoxLayout(self.dash_container)
        self.dash_layout.setContentsMargins(0, 2, 4, 2)
        self.dash_layout.setSpacing(7)

        # -------------------------------------------------------------
        # Card 1: Wallet & Spend Card (Deep Pine-Slate Plate #3E4A45)
        # -------------------------------------------------------------
        card_wallet = QFrame(self.dash_container)
        card_wallet.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_PINE_PLATE};
                border: 1.2px solid {BORDER_MUTED};
                border-radius: 4px;
                padding: 4px;
            }}
        """)
        w_lay = QVBoxLayout(card_wallet)
        w_lay.setContentsMargins(8, 6, 8, 6)
        w_lay.setSpacing(4)

        w_header = QHBoxLayout()
        lbl_w_title = QLabel("💳 OpenRouter Wallet & Cost", card_wallet)
        lbl_w_title.setFont(get_display_font(size=8.8, weight=QFont.Bold))
        lbl_w_title.setStyleSheet("color: #FFFFFF; border: none; background: transparent;")
        w_header.addWidget(lbl_w_title)
        w_header.addStretch(1)

        self.lbl_wallet_tier = QLabel("Free Tier Active", card_wallet)
        self.lbl_wallet_tier.setFont(get_nav_pill_font(size=7.2, weight=QFont.Bold))
        self.lbl_wallet_tier.setStyleSheet("color: #CBD2C4; border: none; background: transparent;")
        w_header.addWidget(self.lbl_wallet_tier)
        w_lay.addLayout(w_header)

        # Wallet stats row
        w_stats_row = QHBoxLayout()
        w_stats_row.setSpacing(6)

        col_rem = QVBoxLayout()
        col_rem.setSpacing(1)
        self.lbl_balance_val = QLabel("$999.97", card_wallet)
        self.lbl_balance_val.setFont(get_display_font(size=13.0, weight=QFont.Black))
        self.lbl_balance_val.setStyleSheet(f"color: {ACCENT_TERRACOTTA}; border: none; background: transparent;")
        col_rem.addWidget(self.lbl_balance_val)

        lbl_balance_sub = QLabel("Remaining Balance", card_wallet)
        lbl_balance_sub.setFont(get_body_font(size=7.2, weight=QFont.Medium))
        lbl_balance_sub.setStyleSheet("color: #CBD2C4; border: none; background: transparent;")
        col_rem.addWidget(lbl_balance_sub)
        w_stats_row.addLayout(col_rem, stretch=1)

        col_cost = QVBoxLayout()
        col_cost.setSpacing(1)
        self.lbl_cost_val = QLabel("$0.0000", card_wallet)
        self.lbl_cost_val.setFont(get_display_font(size=13.0, weight=QFont.Black))
        self.lbl_cost_val.setStyleSheet("color: #FFFFFF; border: none; background: transparent;")
        col_cost.addWidget(self.lbl_cost_val)

        lbl_cost_sub = QLabel("Session Est. Cost", card_wallet)
        lbl_cost_sub.setFont(get_body_font(size=7.2, weight=QFont.Medium))
        lbl_cost_sub.setStyleSheet("color: #CBD2C4; border: none; background: transparent;")
        col_cost.addWidget(lbl_cost_sub)
        w_stats_row.addLayout(col_cost, stretch=1)

        w_lay.addLayout(w_stats_row)

        self.lbl_spend_alltime = QLabel("Total Spend: $0.0336 • Today: $0.0047", card_wallet)
        self.lbl_spend_alltime.setFont(get_body_font(size=7.3, weight=QFont.Medium))
        self.lbl_spend_alltime.setStyleSheet("color: #CBD2C4; border: none; background: transparent;")
        w_lay.addWidget(self.lbl_spend_alltime)

        self.dash_layout.addWidget(card_wallet)

        # -------------------------------------------------------------
        # Card 2: Live Token Tracking (Prompt vs Completion)
        # -------------------------------------------------------------
        card_tokens = QFrame(self.dash_container)
        card_tokens.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_PARCHMENT};
                border: 1.2px solid {BORDER_MUTED};
                border-radius: 4px;
                padding: 4px;
            }}
        """)
        t_lay = QVBoxLayout(card_tokens)
        t_lay.setContentsMargins(8, 6, 8, 6)
        t_lay.setSpacing(5)

        t_header = QHBoxLayout()
        lbl_t_title = QLabel("📊 Token Tracking (Session)", card_tokens)
        lbl_t_title.setFont(get_display_font(size=8.8, weight=QFont.Bold))
        lbl_t_title.setStyleSheet(f"color: {TEXT_CHARCOAL}; border: none; background: transparent;")
        t_header.addWidget(lbl_t_title)
        t_header.addStretch(1)

        self.lbl_total_tokens = QLabel("0 Total", card_tokens)
        self.lbl_total_tokens.setFont(get_nav_pill_font(size=7.8, weight=QFont.Bold))
        self.lbl_total_tokens.setStyleSheet(f"color: {TEXT_CHARCOAL}; border: none; background: transparent;")
        t_header.addWidget(self.lbl_total_tokens)
        t_lay.addLayout(t_header)

        # Prompt vs Completion row
        tok_row = QHBoxLayout()
        tok_row.setSpacing(6)

        self.lbl_prompt_tokens = QLabel("Prompt: 0", card_tokens)
        self.lbl_prompt_tokens.setFont(get_nav_pill_font(size=7.6, weight=QFont.Bold))
        self.lbl_prompt_tokens.setStyleSheet(f"""
            background-color: {ACCENT_AMBER};
            color: #FFFFFF;
            border: 1px solid {BORDER_MUTED};
            border-radius: 3px;
            padding: 2px 6px;
        """)
        tok_row.addWidget(self.lbl_prompt_tokens, stretch=1)

        self.lbl_comp_tokens = QLabel("Completion: 0", card_tokens)
        self.lbl_comp_tokens.setFont(get_nav_pill_font(size=7.6, weight=QFont.Bold))
        self.lbl_comp_tokens.setStyleSheet(f"""
            background-color: {ACCENT_TERRACOTTA};
            color: #FFFFFF;
            border: 1px solid {BORDER_MUTED};
            border-radius: 3px;
            padding: 2px 6px;
        """)
        tok_row.addWidget(self.lbl_comp_tokens, stretch=1)
        t_lay.addLayout(tok_row)

        self.token_split_bar = TokenSplitBar(card_tokens)
        self.token_split_bar.setFixedHeight(8)
        t_lay.addWidget(self.token_split_bar)

        self.dash_layout.addWidget(card_tokens)

        # -------------------------------------------------------------
        # Card 3: Performance Metrics (Latency & RPM)
        # -------------------------------------------------------------
        card_perf = QFrame(self.dash_container)
        card_perf.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_PARCHMENT};
                border: 1.2px solid {BORDER_MUTED};
                border-radius: 4px;
                padding: 4px;
            }}
        """)
        p_lay = QVBoxLayout(card_perf)
        p_lay.setContentsMargins(8, 6, 8, 6)
        p_lay.setSpacing(4)

        p_header = QHBoxLayout()
        lbl_p_title = QLabel("⚡ Performance Metrics", card_perf)
        lbl_p_title.setFont(get_display_font(size=8.8, weight=QFont.Bold))
        lbl_p_title.setStyleSheet(f"color: {TEXT_CHARCOAL}; border: none; background: transparent;")
        p_header.addWidget(lbl_p_title)
        p_header.addStretch(1)

        self.lbl_success_rate = QLabel("100% OK", card_perf)
        self.lbl_success_rate.setFont(get_nav_pill_font(size=7.4, weight=QFont.Bold))
        self.lbl_success_rate.setStyleSheet(f"color: {ACCENT_SAGE}; border: none; background: transparent;")
        p_header.addWidget(self.lbl_success_rate)
        p_lay.addLayout(p_header)

        # Values row
        p_stats_row = QHBoxLayout()
        p_stats_row.setSpacing(6)

        col_lat = QVBoxLayout()
        col_lat.setSpacing(1)
        self.lbl_latency_val = QLabel("0 ms", card_perf)
        self.lbl_latency_val.setFont(get_display_font(size=12.0, weight=QFont.Black))
        self.lbl_latency_val.setStyleSheet(f"color: {ACCENT_SAGE}; border: none; background: transparent;")
        col_lat.addWidget(self.lbl_latency_val)

        lbl_lat_sub = QLabel("Avg Latency", card_perf)
        lbl_lat_sub.setFont(get_body_font(size=7.2, weight=QFont.Medium))
        lbl_lat_sub.setStyleSheet(f"color: {TEXT_MUTED}; border: none; background: transparent;")
        col_lat.addWidget(lbl_lat_sub)
        p_stats_row.addLayout(col_lat, stretch=1)

        col_rpm = QVBoxLayout()
        col_rpm.setSpacing(1)
        self.lbl_rpm_val = QLabel("0.0 RPM", card_perf)
        self.lbl_rpm_val.setFont(get_display_font(size=12.0, weight=QFont.Black))
        self.lbl_rpm_val.setStyleSheet(f"color: {ACCENT_TERRACOTTA}; border: none; background: transparent;")
        col_rpm.addWidget(self.lbl_rpm_val)

        lbl_rpm_sub = QLabel("Requests / Min", card_perf)
        lbl_rpm_sub.setFont(get_body_font(size=7.2, weight=QFont.Medium))
        lbl_rpm_sub.setStyleSheet(f"color: {TEXT_MUTED}; border: none; background: transparent;")
        col_rpm.addWidget(lbl_rpm_sub)
        p_stats_row.addLayout(col_rpm, stretch=1)

        p_lay.addLayout(p_stats_row)
        self.dash_layout.addWidget(card_perf)

        # -------------------------------------------------------------
        # Card 4: Model Status Toggles
        # -------------------------------------------------------------
        card_models = QFrame(self.dash_container)
        card_models.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_PARCHMENT};
                border: 1.2px solid {BORDER_MUTED};
                border-radius: 4px;
                padding: 4px;
            }}
        """)
        m_lay = QVBoxLayout(card_models)
        m_lay.setContentsMargins(8, 6, 8, 6)
        m_lay.setSpacing(4)

        m_header = QHBoxLayout()
        lbl_m_title = QLabel("🌐 Model Engine Status", card_models)
        lbl_m_title.setFont(get_display_font(size=8.8, weight=QFont.Bold))
        lbl_m_title.setStyleSheet(f"color: {TEXT_CHARCOAL}; border: none; background: transparent;")
        m_header.addWidget(lbl_m_title)
        m_header.addStretch(1)

        lbl_m_active = QLabel("6 Available", card_models)
        lbl_m_active.setFont(get_body_font(size=7.2, weight=QFont.Medium))
        lbl_m_active.setStyleSheet(f"color: {TEXT_MUTED}; border: none; background: transparent;")
        m_header.addWidget(lbl_m_active)
        m_lay.addLayout(m_header)

        # List of models
        self.model_entries = [
            {"id": "openai/gpt-4o-mini", "name": "GPT-4o Mini", "specs": "~240ms • 128k", "enabled": True},
            {"id": "anthropic/claude-3.5-sonnet", "name": "Claude 3.5 Sonnet", "specs": "~480ms • 200k", "enabled": True},
            {"id": "google/gemini-2.0-flash-001", "name": "Gemini 2.0 Flash", "specs": "~290ms • 1M", "enabled": True},
            {"id": "openai/gpt-4o", "name": "GPT-4o Omnimodel", "specs": "~430ms • 128k", "enabled": True},
            {"id": "meta-llama/llama-3.3-70b-instruct", "name": "Llama 3.3 70B", "specs": "~380ms • 128k", "enabled": True},
            {"id": "deepseek/deepseek-chat", "name": "DeepSeek V3", "specs": "~410ms • 64k", "enabled": True},
        ]

        for m_info in self.model_entries:
            row_widget = QWidget(card_models)
            row_widget.setFixedHeight(22)
            r_lay = QHBoxLayout(row_widget)
            r_lay.setContentsMargins(0, 0, 0, 0)
            r_lay.setSpacing(5)

            dot = QLabel("●", row_widget)
            dot.setFont(QFont("Segoe UI", 8))
            dot.setStyleSheet(f"color: {ACCENT_SAGE}; border: none; background: transparent;")
            r_lay.addWidget(dot)

            name_lbl = QLabel(m_info["name"], row_widget)
            name_lbl.setFont(get_display_font(size=8.0, weight=QFont.Bold))
            name_lbl.setStyleSheet(f"color: {TEXT_CHARCOAL}; border: none; background: transparent;")
            r_lay.addWidget(name_lbl, stretch=1)

            spec_lbl = QLabel(m_info["specs"], row_widget)
            spec_lbl.setFont(get_body_font(size=7.0, weight=QFont.Medium))
            spec_lbl.setStyleSheet(f"color: {TEXT_MUTED}; border: none; background: transparent;")
            r_lay.addWidget(spec_lbl)

            btn_toggle = GlassButton(icon_text="ON", parent=row_widget, is_pill=True)
            btn_toggle.setFixedSize(32, 18)
            btn_toggle.setFont(get_nav_pill_font(size=6.8, weight=QFont.Bold))
            btn_toggle.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ACCENT_SAGE};
                    border: 1px solid {BORDER_MUTED};
                    border-radius: 3px;
                    color: #FFFFFF;
                }}
            """)

            def make_toggle(btn=btn_toggle, info=m_info):
                def toggle():
                    info["enabled"] = not info["enabled"]
                    if info["enabled"]:
                        btn.setText("ON")
                        btn.setStyleSheet(f"background-color: {ACCENT_SAGE}; border: 1px solid {BORDER_MUTED}; border-radius: 3px; color: #FFFFFF;")
                    else:
                        btn.setText("OFF")
                        btn.setStyleSheet(f"background-color: {BG_PARCHMENT_LIGHT}; border: 1px solid {BORDER_MUTED}; border-radius: 3px; color: {TEXT_MUTED};")
                return toggle

            btn_toggle.clicked.connect(make_toggle())
            r_lay.addWidget(btn_toggle)
            m_lay.addWidget(row_widget)

        self.dash_layout.addWidget(card_models)

        self.scroll_area.setWidget(self.dash_container)
        self._main_layout.addWidget(self.scroll_area, stretch=1)

        # Connect live telemetry tracker
        OpenRouterTelemetryTracker.get_instance().updated.connect(self._update_telemetry_ui)

        # Initial UI update and background sync
        self._update_telemetry_ui()
        self.refresh_telemetry()

    def _update_telemetry_ui(self):
        tracker = OpenRouterTelemetryTracker.get_instance()

        # 1. Wallet & Spend
        self.lbl_balance_val.setText(f"${tracker.wallet_remaining:.2f}")
        self.lbl_cost_val.setText(f"${tracker.session_cost_usd:.4f}")
        self.lbl_spend_alltime.setText(f"Total Spend: ${tracker.wallet_usage:.4f} • Today: ${tracker.wallet_daily:.4f}")

        # 2. Token metrics
        tot = tracker.session_prompt_tokens + tracker.session_completion_tokens
        self.lbl_total_tokens.setText(f"{tot:,} Total")
        self.lbl_prompt_tokens.setText(f"Prompt: {tracker.session_prompt_tokens:,}")
        self.lbl_comp_tokens.setText(f"Completion: {tracker.session_completion_tokens:,}")
        self.token_split_bar.set_tokens(tracker.session_prompt_tokens, tracker.session_completion_tokens)

        # 3. Performance
        avg_lat = tracker.get_avg_latency_ms()
        self.lbl_latency_val.setText(f"{int(avg_lat)} ms")
        if avg_lat < 500:
            self.lbl_latency_val.setStyleSheet(f"color: {ACCENT_SAGE}; border: none; background: transparent;")
        else:
            self.lbl_latency_val.setStyleSheet(f"color: {ACCENT_AMBER}; border: none; background: transparent;")

        rpm = tracker.get_rpm()
        self.lbl_rpm_val.setText(f"{rpm:.1f} RPM")

        reqs = tracker.session_requests
        errs = tracker.session_errors
        succ_rate = 100 if reqs == 0 else int(((reqs - errs) / reqs) * 100)
        self.lbl_success_rate.setText(f"{succ_rate}% OK ({reqs} calls)")

    def refresh_telemetry(self):
        if self._key_worker and self._key_worker.isRunning():
            return
        self._key_worker = OpenRouterKeyInfoWorker(parent=self)
        self._key_worker.start()

    def close_node(self):
        if self._key_worker and self._key_worker.isRunning():
            self._key_worker.wait(3000)
        super().close_node()


# Backward compatibility alias
VaultNodeWindow = OpenRouterDashboardWindow


# =========================================================================
# Built-in Interactive Calculator Widget (Illustrated Editorial Styling)
# =========================================================================

class InteractiveCalcWidget(QWidget):
    """
    Illustrated Editorial Calculator Widget (Misty Sage & Terracotta styling).
    Features high-precision keypad, expression history, error handling,
    and responsive keypad clicks.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._expr_str = ""
        self._cur_val = "0"
        self._pending_op = None
        self._acc_val = 0.0
        self._reset_input = True

        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(5)

        # Display screen plate in Deep Pine-Slate
        disp_card = QFrame(self)
        disp_card.setFixedHeight(54)
        disp_card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_PINE_PLATE};
                border: 1.2px solid {BORDER_MUTED};
                border-radius: 6px;
                padding: 4px 8px;
            }}
        """)
        d_lay = QVBoxLayout(disp_card)
        d_lay.setContentsMargins(6, 2, 6, 2)
        d_lay.setSpacing(0)

        self.lbl_expr = QLabel("", disp_card)
        self.lbl_expr.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lbl_expr.setFont(get_body_font(size=7.5, weight=QFont.Medium))
        self.lbl_expr.setStyleSheet("color: #CBD2C4; border: none; background: transparent;")
        d_lay.addWidget(self.lbl_expr)

        self.lbl_val = QLabel("0", disp_card)
        self.lbl_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lbl_val.setFont(get_display_font(size=16.0, weight=QFont.Black))
        self.lbl_val.setStyleSheet("color: #FFFFFF; border: none; background: transparent;")
        d_lay.addWidget(self.lbl_val)
        lay.addWidget(disp_card)

        # Buttons Grid
        grid = QGridLayout()
        grid.setSpacing(4)

        buttons = [
            ("C", 0, 0, "clear"), ("⌫", 0, 1, "back"), ("%", 0, 2, "op"), ("÷", 0, 3, "op"),
            ("7", 1, 0, "num"),   ("8", 1, 1, "num"),  ("9", 1, 2, "num"), ("×", 1, 3, "op"),
            ("4", 2, 0, "num"),   ("5", 2, 1, "num"),  ("6", 2, 2, "num"), ("-", 2, 3, "op"),
            ("1", 3, 0, "num"),   ("2", 3, 1, "num"),  ("3", 3, 2, "num"), ("+", 3, 3, "op"),
            ("±", 4, 0, "pm"),    ("0", 4, 1, "num"),  (".", 4, 2, "num"), ("=", 4, 3, "eq"),
        ]

        for text, r, c, b_type in buttons:
            btn = QPushButton(text, self)
            btn.setFixedHeight(28)
            btn.setCursor(Qt.PointingHandCursor)
            
            if b_type == "num":
                btn.setFont(get_display_font(size=9.5, weight=QFont.Bold))
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {BG_PARCHMENT};
                        color: {TEXT_CHARCOAL};
                        border: 1.2px solid {BORDER_MUTED};
                        border-radius: 4px;
                    }}
                    QPushButton:hover {{
                        background-color: #FAF8F2;
                        border-color: {ACCENT_TERRACOTTA};
                    }}
                    QPushButton:pressed {{
                        background-color: #DDD8CB;
                    }}
                """)
                btn.clicked.connect(lambda _, t=text: self._on_digit(t))
            elif b_type == "op":
                btn.setFont(get_display_font(size=10.5, weight=QFont.Black))
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {BG_PINE_PLATE};
                        color: #FFFFFF;
                        border: 1.2px solid {BORDER_MUTED};
                        border-radius: 4px;
                    }}
                    QPushButton:hover {{
                        background-color: {BG_PINE_SLATE};
                    }}
                    QPushButton:pressed {{
                        background-color: #2E3A35;
                    }}
                """)
                btn.clicked.connect(lambda _, t=text: self._on_op(t))
            elif b_type == "eq":
                btn.setFont(get_display_font(size=11.5, weight=QFont.Black))
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {ACCENT_TERRACOTTA};
                        color: #FFFFFF;
                        border: 1.2px solid {ACCENT_MAHOGANY};
                        border-radius: 4px;
                    }}
                    QPushButton:hover {{
                        background-color: {ACCENT_SIENNA};
                    }}
                    QPushButton:pressed {{
                        background-color: {ACCENT_PRESSED};
                    }}
                """)
                btn.clicked.connect(self._on_equals)
            elif b_type == "clear":
                btn.setFont(get_display_font(size=9.5, weight=QFont.Black))
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {ACCENT_AMBER};
                        color: #FFFFFF;
                        border: 1.2px solid {BORDER_MUTED};
                        border-radius: 4px;
                    }}
                    QPushButton:hover {{
                        background-color: #F4A261;
                    }}
                """)
                btn.clicked.connect(self._on_clear)
            elif b_type == "back":
                btn.setFont(get_display_font(size=9.5, weight=QFont.Black))
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {BG_PARCHMENT};
                        color: {TEXT_CHARCOAL};
                        border: 1.2px solid {BORDER_MUTED};
                        border-radius: 4px;
                    }}
                    QPushButton:hover {{
                        background-color: #FAF8F2;
                    }}
                """)
                btn.clicked.connect(self._on_backspace)
            elif b_type == "pm":
                btn.setFont(get_display_font(size=9.5, weight=QFont.Bold))
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {BG_PARCHMENT};
                        color: {TEXT_CHARCOAL};
                        border: 1.2px solid {BORDER_MUTED};
                        border-radius: 4px;
                    }}
                    QPushButton:hover {{
                        background-color: #FAF8F2;
                    }}
                """)
                btn.clicked.connect(self._on_plus_minus)

            grid.addWidget(btn, r, c)

        lay.addLayout(grid)

    def _on_digit(self, d: str):
        if self._reset_input:
            self._cur_val = d if d != "." else "0."
            self._reset_input = False
        else:
            if d == "." and "." in self._cur_val:
                return
            if self._cur_val == "0" and d != ".":
                self._cur_val = d
            else:
                self._cur_val += d
        self.lbl_val.setText(self._cur_val)

    def _on_op(self, op: str):
        try:
            curr = float(self._cur_val)
        except Exception:
            curr = 0.0

        if op == "%":
            curr = curr / 100.0
            self._cur_val = self._fmt(curr)
            self.lbl_val.setText(self._cur_val)
            return

        if self._pending_op and not self._reset_input:
            self._compute()

        self._acc_val = float(self._cur_val)
        self._pending_op = op
        self._expr_str = f"{self._fmt(self._acc_val)} {op}"
        self.lbl_expr.setText(self._expr_str)
        self._reset_input = True

    def _on_equals(self):
        if self._pending_op:
            self._expr_str = f"{self._fmt(self._acc_val)} {self._pending_op} {self._cur_val} ="
            self.lbl_expr.setText(self._expr_str)
            self._compute()
            self._pending_op = None
            self._reset_input = True

    def _compute(self):
        try:
            b = float(self._cur_val)
            a = self._acc_val
            if self._pending_op == "+":
                res = a + b
            elif self._pending_op == "-":
                res = a - b
            elif self._pending_op == "×":
                res = a * b
            elif self._pending_op == "÷":
                res = a / b if b != 0 else float("nan")
            else:
                res = b
            self._cur_val = "Error" if math.isnan(res) else self._fmt(res)
        except Exception:
            self._cur_val = "Error"
        self.lbl_val.setText(self._cur_val)

    def _on_clear(self):
        self._cur_val = "0"
        self._expr_str = ""
        self._pending_op = None
        self._acc_val = 0.0
        self._reset_input = True
        self.lbl_expr.setText("")
        self.lbl_val.setText("0")

    def _on_backspace(self):
        if not self._reset_input and len(self._cur_val) > 0:
            self._cur_val = self._cur_val[:-1]
            if not self._cur_val or self._cur_val == "-":
                self._cur_val = "0"
            self.lbl_val.setText(self._cur_val)

    def _on_plus_minus(self):
        try:
            val = float(self._cur_val) * -1
            self._cur_val = self._fmt(val)
            self.lbl_val.setText(self._cur_val)
        except Exception:
            pass

    def _fmt(self, num: float) -> str:
        if num.is_integer():
            return str(int(num))
        return f"{num:.6f}".rstrip("0").rstrip(".")


# =========================================================================
# Built-in Interactive Terminal / PowerShell Command Runner
# =========================================================================

class InteractiveTerminalWidget(QWidget):
    """
    Interactive Terminal / PowerShell console widget for running shell commands.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self._on_stdout)
        self.process.readyReadStandardError.connect(self._on_stderr)
        self.process.finished.connect(self._on_finished)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(5)

        # Output console
        self.txt_out = QPlainTextEdit(self)
        self.txt_out.setReadOnly(True)
        self.txt_out.setFont(QFont("Consolas", 8.5))
        self.txt_out.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1A201D;
                color: #A3E635;
                border: 1.2px solid #5E6F68;
                border-radius: 4px;
                padding: 6px;
            }
        """)
        self.txt_out.appendPlainText("PS Windows Dynamic Island [Console v11.0]\nType a command below or click a preset:\n")
        lay.addWidget(self.txt_out, stretch=1)

        # Preset chips
        presets_row = QHBoxLayout()
        presets_row.setSpacing(4)
        for cmd in ["dir", "ping 8.8.8.8 -n 2", "python --version", "cls"]:
            btn_p = QPushButton(cmd, self)
            btn_p.setFixedHeight(18)
            btn_p.setCursor(Qt.PointingHandCursor)
            btn_p.setFont(get_nav_pill_font(size=6.8, weight=QFont.Bold))
            btn_p.setStyleSheet(f"""
                QPushButton {{
                    background-color: {BG_PARCHMENT};
                    color: {TEXT_CHARCOAL};
                    border: 1px solid {BORDER_MUTED};
                    border-radius: 3px;
                    padding: 0 4px;
                }}
                QPushButton:hover {{
                    background-color: #FAF8F2;
                    color: {ACCENT_TERRACOTTA};
                }}
            """)
            btn_p.clicked.connect(lambda _, c=cmd: self._run_preset(c))
            presets_row.addWidget(btn_p)
        presets_row.addStretch(1)
        lay.addLayout(presets_row)

        # Input row
        in_row = QHBoxLayout()
        in_row.setSpacing(4)

        lbl_prompt = QLabel("PS >", self)
        lbl_prompt.setFont(get_display_font(size=8.5, weight=QFont.Bold))
        lbl_prompt.setStyleSheet(f"color: {ACCENT_TERRACOTTA};")
        in_row.addWidget(lbl_prompt)

        self.input_cmd = QLineEdit(self)
        self.input_cmd.setFont(QFont("Consolas", 8.8))
        self.input_cmd.setStyleSheet(PARCHMENT_INPUT_QSS)
        self.input_cmd.setPlaceholderText("Enter command...")
        self.input_cmd.returnPressed.connect(self._run_cmd)
        in_row.addWidget(self.input_cmd, stretch=1)

        self.btn_run = GlassButton(icon_text="⚡ RUN", parent=self, is_pill=True, is_accent=True)
        self.btn_run.setFixedSize(54, 24)
        self.btn_run.clicked.connect(self._run_cmd)
        in_row.addWidget(self.btn_run)

        lay.addLayout(in_row)

    def _run_preset(self, cmd: str):
        if cmd == "cls":
            self.txt_out.clear()
            return
        self.input_cmd.setText(cmd)
        self._run_cmd()

    def _run_cmd(self):
        cmd = self.input_cmd.text().strip()
        if not cmd:
            return
        self.input_cmd.clear()
        if cmd.lower() in ("cls", "clear"):
            self.txt_out.clear()
            return
        self.txt_out.appendPlainText(f"\nPS > {cmd}")
        self.process.start("cmd.exe", ["/c", cmd])

    def _on_stdout(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self.txt_out.appendPlainText(data)
        self._scroll_to_bottom()

    def _on_stderr(self):
        data = self.process.readAllStandardError().data().decode("utf-8", errors="replace")
        self.txt_out.appendPlainText(data)
        self._scroll_to_bottom()

    def _on_finished(self):
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        sb = self.txt_out.verticalScrollBar()
        sb.setValue(sb.maximum())


# =========================================================================
# Custom Extensible Floating App Window (Any App / Drag & Drop / Calibrated)
# =========================================================================

class CustomAppNodeWindow(FloatingNodeWindow):
    """
    Extensible Floating App Host Node (up to 6 extension windows total).
    Supports:
    1. Text input to open/launch any app (e.g. calc, notepad, cmd, or system path).
    2. Drag & Drop any application executable (.exe), shortcut (.lnk), script, or document.
    3. Perfectly calibrated embedding into the window using Win32 createWindowContainer,
       stripping outer borders and auto-resizing on resizeEvent.
    4. Built-in interactive companions (illustrated calculator, terminal console).
    5. Calibration control bar at bottom ([⛶ Fit/Calibrate], [🔄 Reload], [🧹 Change App]).
    """
    title_changed = Signal(int, str)

    def __init__(self, tab_index: int = 4, title: str = "App Host", parent=None):
        super().__init__(node_id=f"APP {tab_index}", title=title, width=330, height=430, parent=parent)
        self.tab_index = tab_index
        self._app_name = "App Host"
        self._embedded_hwnd = None
        self._win_container = None
        self._proc = None
        self._before_hwnds = set()
        self._embed_attempts = 0

        # Enable Drag and Drop
        self.setAcceptDrops(True)

        # Style node badge with dedicated accent color
        accents = {4: "#2563EB", 5: "#EA580C", 6: "#7C3AED"}
        badge_color = accents.get(tab_index, "#2563EB")
        self.badge_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {badge_color};
                color: #FFFFFF;
                border: 1px solid {BORDER_MUTED};
                border-radius: 3px;
                padding: 1px 6px;
            }}
        """)

        # Clear App button in header
        btn_clear = GlassButton(icon_text="🧹", parent=self.header_widget, is_pill=False, size_override=(22, 22))
        btn_clear.setToolTip("Unload active app and return to search/drop view")
        btn_clear.clicked.connect(self.set_view_drop_zone)
        self.header_layout.insertWidget(self.header_layout.count() - 2, btn_clear)

        # -------------------------------------------------------------
        # Top App Input & Quick Suggestion Row
        # -------------------------------------------------------------
        in_row = QHBoxLayout()
        in_row.setSpacing(5)

        self.input_app = QLineEdit(self)
        self.input_app.setPlaceholderText("Type app (calc, notepad, cmd) or drop here...")
        self.input_app.setFont(get_body_font(size=8.8, weight=QFont.Normal))
        self.input_app.setStyleSheet(PARCHMENT_INPUT_QSS)
        self.input_app.returnPressed.connect(self._on_launch_input)
        in_row.addWidget(self.input_app, stretch=1)

        self.btn_open = GlassButton(icon_text="⚡ OPEN", parent=self, is_pill=True, is_accent=True)
        self.btn_open.setFixedSize(62, 26)
        self.btn_open.clicked.connect(self._on_launch_input)
        in_row.addWidget(self.btn_open)

        self._main_layout.addLayout(in_row)

        # Quick chips row
        chips_row = QHBoxLayout()
        chips_row.setSpacing(4)
        quick_chips = [
            ("🔢 Calc", "calc"),
            ("📝 Notepad", "notepad"),
            ("💻 Terminal", "cmd"),
            ("🎨 Paint", "mspaint"),
            ("🌐 Web", "https://google.com"),
        ]
        for label, cmd in quick_chips:
            btn_c = QPushButton(label, self)
            btn_c.setFixedHeight(20)
            btn_c.setCursor(Qt.PointingHandCursor)
            btn_c.setFont(get_nav_pill_font(size=7.2, weight=QFont.Bold))
            btn_c.setStyleSheet(f"""
                QPushButton {{
                    background-color: {BG_PARCHMENT};
                    color: {TEXT_CHARCOAL};
                    border: 1px solid {BORDER_MUTED};
                    border-radius: 3px;
                    padding: 1px 6px;
                }}
                QPushButton:hover {{
                    background-color: #FAF8F2;
                    border-color: {ACCENT_TERRACOTTA};
                    color: {ACCENT_TERRACOTTA};
                }}
            """)
            btn_c.clicked.connect(lambda _, c=cmd: self.load_app(c))
            chips_row.addWidget(btn_c)
        chips_row.addStretch(1)
        self._main_layout.addLayout(chips_row)

        # -------------------------------------------------------------
        # Content Stacked Widget (Pages 0 to 4)
        # -------------------------------------------------------------
        self.stack = QStackedWidget(self)

        # Page 0: Drop Zone View (Empty state)
        self.drop_card = QFrame(self.stack)
        self.drop_card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_WELL_PINE};
                border: 1.5px dashed {BORDER_MUTED};
                border-radius: 6px;
            }}
        """)
        dc_lay = QVBoxLayout(self.drop_card)
        dc_lay.setAlignment(Qt.AlignCenter)
        dc_lay.setSpacing(6)

        lbl_icon = QLabel("📂", self.drop_card)
        lbl_icon.setFont(QFont("Segoe UI Emoji", 24))
        lbl_icon.setAlignment(Qt.AlignCenter)
        lbl_icon.setStyleSheet("border: none; background: transparent;")
        dc_lay.addWidget(lbl_icon)

        lbl_drop_title = QLabel("Drag & Drop Any App or Shortcut Here", self.drop_card)
        lbl_drop_title.setFont(get_display_font(size=9.5, weight=QFont.Bold))
        lbl_drop_title.setAlignment(Qt.AlignCenter)
        lbl_drop_title.setStyleSheet(f"color: {TEXT_CHARCOAL}; border: none; background: transparent;")
        dc_lay.addWidget(lbl_drop_title)

        lbl_drop_sub = QLabel("Supports .exe, .lnk shortcuts, scripts, documents, or type any Windows app above.", self.drop_card)
        lbl_drop_sub.setWordWrap(True)
        lbl_drop_sub.setFont(get_body_font(size=7.8, weight=QFont.Medium))
        lbl_drop_sub.setAlignment(Qt.AlignCenter)
        lbl_drop_sub.setStyleSheet(f"color: {TEXT_MUTED}; border: none; background: transparent;")
        dc_lay.addWidget(lbl_drop_sub)
        self.stack.addWidget(self.drop_card)

        # Page 1: Embedded Win32 Container
        self.container_host = QWidget(self.stack)
        self.container_layout = QVBoxLayout(self.container_host)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)
        self.stack.addWidget(self.container_host)

        # Page 2: Native Illustrated Calculator
        self.calc_widget = InteractiveCalcWidget(self.stack)
        self.stack.addWidget(self.calc_widget)

        # Page 3: Native Interactive Terminal
        self.terminal_widget = InteractiveTerminalWidget(self.stack)
        self.stack.addWidget(self.terminal_widget)

        # Page 4: Process Running Telemetry Card
        self.proc_card = QFrame(self.stack)
        self.proc_card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_PINE_PLATE};
                border: 1.2px solid {BORDER_MUTED};
                border-radius: 6px;
            }}
        """)
        p_lay = QVBoxLayout(self.proc_card)
        p_lay.setAlignment(Qt.AlignCenter)
        p_lay.setSpacing(8)

        self.lbl_proc_info = QLabel("App Running Externally", self.proc_card)
        self.lbl_proc_info.setFont(get_display_font(size=10.5, weight=QFont.Bold))
        self.lbl_proc_info.setStyleSheet("color: #FFFFFF; border: none; background: transparent;")
        p_lay.addWidget(self.lbl_proc_info)

        self.lbl_proc_sub = QLabel("Process is running. Click below to bring window to front.", self.proc_card)
        self.lbl_proc_sub.setFont(get_body_font(size=8.0, weight=QFont.Medium))
        self.lbl_proc_sub.setStyleSheet("color: #CBD2C4; border: none; background: transparent;")
        p_lay.addWidget(self.lbl_proc_sub)

        act_row = QHBoxLayout()
        act_row.setAlignment(Qt.AlignCenter)
        btn_focus = GlassButton(icon_text="🔍 Bring to Front", parent=self.proc_card, is_pill=True)
        btn_focus.clicked.connect(self._focus_proc_window)
        act_row.addWidget(btn_focus)

        btn_term = GlassButton(icon_text="⏹ Terminate", parent=self.proc_card, is_pill=True, is_accent=True)
        btn_term.clicked.connect(self._terminate_proc)
        act_row.addWidget(btn_term)
        p_lay.addLayout(act_row)

        self.stack.addWidget(self.proc_card)
        self._main_layout.addWidget(self.stack, stretch=1)

        # -------------------------------------------------------------
        # Bottom Status & Calibration Bar
        # -------------------------------------------------------------
        bot_bar = QHBoxLayout()
        bot_bar.setContentsMargins(2, 0, 2, 0)
        bot_bar.setSpacing(6)

        self.lbl_status = QLabel("● App Host Ready", self)
        self.lbl_status.setFont(get_body_font(size=7.6, weight=QFont.Medium))
        self.lbl_status.setStyleSheet(f"color: {TEXT_MUTED};")
        bot_bar.addWidget(self.lbl_status, stretch=1)

        btn_fit = GlassButton(icon_text="⛶ Fit", parent=self, is_pill=True)
        btn_fit.setFixedHeight(20)
        btn_fit.setFont(get_nav_pill_font(size=7.2, weight=QFont.Bold))
        btn_fit.setToolTip("Re-calibrate and fit embedded app to window dimensions")
        btn_fit.clicked.connect(self.recalibrate_embedding)
        bot_bar.addWidget(btn_fit)

        btn_change = GlassButton(icon_text="🧹 Change", parent=self, is_pill=True)
        btn_change.setFixedHeight(20)
        btn_change.setFont(get_nav_pill_font(size=7.2, weight=QFont.Bold))
        btn_change.setToolTip("Unload app and return to search/drop area")
        btn_change.clicked.connect(self.set_view_drop_zone)
        bot_bar.addWidget(btn_change)

        self._main_layout.addLayout(bot_bar)

        self._embed_timer = QTimer(self)
        self._embed_timer.setInterval(100)
        self._embed_timer.timeout.connect(self._check_for_embed_window)

    def get_app_display_name(self) -> str:
        return self._app_name

    def set_view_drop_zone(self):
        self._clean_active_app()
        self.stack.setCurrentIndex(0)
        self._app_name = "App Host"
        self.title_lbl.setText(f"APP {self.tab_index}")
        self.lbl_status.setText("● App Host Ready")
        self.title_changed.emit(self.tab_index, self._app_name)

    def _on_launch_input(self):
        txt = self.input_app.text().strip()
        if txt:
            self.load_app(txt)
            self.input_app.clear()

    def load_app(self, target_str: str):
        target = target_str.strip()
        if not target:
            return

        # 1. Native Calculator
        if target.lower() in ("calc", "calculator", "math"):
            self._app_name = "Calculator"
            self.title_lbl.setText(f"APP {self.tab_index}: {self._app_name}")
            self.stack.setCurrentIndex(2)
            self.lbl_status.setText("● Active: Illustrated Calculator")
            self.title_changed.emit(self.tab_index, self._app_name)
            return

        # 2. Native Terminal
        if target.lower() in ("cmd", "terminal", "powershell", "shell", "bash"):
            self._app_name = "Terminal"
            self.title_lbl.setText(f"APP {self.tab_index}: {self._app_name}")
            self.stack.setCurrentIndex(3)
            self.lbl_status.setText("● Active: PowerShell / Command Runner")
            self.title_changed.emit(self.tab_index, self._app_name)
            return

        # 3. Web URL
        if target.lower().startswith("http://") or target.lower().startswith("https://"):
            import webbrowser
            webbrowser.open(target)
            self._app_name = "Web Link"
            self.title_lbl.setText(f"APP {self.tab_index}: {self._app_name}")
            self.lbl_status.setText(f"● Opened browser: {target}")
            self.title_changed.emit(self.tab_index, self._app_name)
            return

        # 4. External Application via Window Embedding
        self.launch_external_app(target)

    def launch_external_app(self, app_path: str):
        self._clean_active_app()
        self._before_hwnds = self._get_visible_hwnds()

        clean_cmd = app_path.strip()
        if clean_cmd.lower().endswith(".lnk"):
            resolved = self._resolve_shortcut(clean_cmd)
            clean_cmd = resolved if resolved else clean_cmd

        base = os.path.basename(clean_cmd).replace(".exe", "").capitalize()
        self._app_name = base if base else "Application"
        self.title_lbl.setText(f"APP {self.tab_index}: {self._app_name}")
        self.lbl_status.setText(f"● Launching {self._app_name}...")
        self.title_changed.emit(self.tab_index, self._app_name)

        try:
            self._proc = subprocess.Popen(clean_cmd, shell=True)
        except Exception as e:
            self.lbl_status.setText(f"Error launching: {e}")
            return

        self._embed_attempts = 0
        self._embed_timer.start()

    def _resolve_shortcut(self, lnk_path: str) -> str:
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            return shell.CreateShortCut(lnk_path).Targetpath
        except Exception:
            return lnk_path

    def _get_visible_hwnds(self) -> set:
        s = set()
        user32 = ctypes.windll.user32
        def cb(hwnd, _):
            if user32.IsWindowVisible(hwnd) and user32.GetWindowTextLengthW(hwnd) > 0:
                s.add(hwnd)
            return True
        WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(cb), 0)
        return s

    def _check_for_embed_window(self):
        self._embed_attempts += 1
        after = self._get_visible_hwnds()
        diff = after - self._before_hwnds
        user32 = ctypes.windll.user32

        target_hwnd = None
        for hwnd in diff:
            if hwnd != int(self.winId()):
                target_hwnd = hwnd
                break

        if target_hwnd:
            self._embed_timer.stop()
            self._embed_hwnd(target_hwnd)
            return

        if self._embed_attempts >= 25:
            self._embed_timer.stop()
            self.set_view_process_card()

    def _embed_hwnd(self, hwnd: int):
        self._embedded_hwnd = hwnd
        user32 = ctypes.windll.user32

        try:
            # Strip outer window frames for clean embedding
            style = user32.GetWindowLongW(hwnd, -16) # GWL_STYLE
            new_style = (style & ~0x00C00000 & ~0x00040000 & ~0x00020000 & ~0x00010000) | 0x40000000 # WS_CHILD
            user32.SetWindowLongW(hwnd, -16, new_style)

            # Create container
            qwin = QWindow.fromWinId(hwnd)
            self._win_container = QWidget.createWindowContainer(qwin, self.container_host)

            while self.container_layout.count():
                item = self.container_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            self.container_layout.addWidget(self._win_container)
            self.stack.setCurrentIndex(1) # Switch to container view
            self.recalibrate_embedding()
            self.lbl_status.setText(f"● Embedded: {self._app_name}")
        except Exception as e:
            logger.error(f"Failed to embed HWND {hwnd}: {e}")
            self.set_view_process_card()

    def set_view_process_card(self):
        self.stack.setCurrentIndex(4)
        pid_str = f"(PID {self._proc.pid})" if self._proc else ""
        self.lbl_proc_info.setText(f"{self._app_name} Running {pid_str}")
        self.lbl_status.setText(f"● Running externally: {self._app_name}")

    def recalibrate_embedding(self):
        if self._embedded_hwnd and ctypes.windll.user32.IsWindow(self._embedded_hwnd):
            w = max(10, self.container_host.width())
            h = max(10, self.container_host.height())
            ctypes.windll.user32.MoveWindow(self._embedded_hwnd, 0, 0, w, h, True)
            if self._win_container:
                self._win_container.resize(w, h)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.recalibrate_embedding()

    def _focus_proc_window(self):
        if self._embedded_hwnd and ctypes.windll.user32.IsWindow(self._embedded_hwnd):
            ctypes.windll.user32.SetForegroundWindow(self._embedded_hwnd)

    def _terminate_proc(self):
        if self._proc:
            try:
                self._proc.terminate()
            except Exception:
                pass
        self.set_view_drop_zone()

    def _clean_active_app(self):
        if self._embed_timer.isActive():
            self._embed_timer.stop()
        if self._embedded_hwnd and ctypes.windll.user32.IsWindow(self._embedded_hwnd):
            try:
                ctypes.windll.user32.PostMessageW(self._embedded_hwnd, 0x0010, 0, 0)
            except Exception:
                pass
            self._embedded_hwnd = None
        if self._win_container:
            try:
                self._win_container.deleteLater()
            except Exception:
                pass
            self._win_container = None
        self._proc = None

    def close_node(self):
        self._clean_active_app()
        super().close_node()

    # -------------------------------------------------------------
    # Drag and Drop Handlers
    # -------------------------------------------------------------
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()
            self.drop_card.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(184, 59, 36, 0.12);
                    border: 2px dashed {ACCENT_TERRACOTTA};
                    border-radius: 6px;
                }}
            """)
        else:
            super().dragEnterEvent(event)

    def dragLeaveEvent(self, event):
        self.drop_card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_WELL_PINE};
                border: 1.5px dashed {BORDER_MUTED};
                border-radius: 6px;
            }}
        """)
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent):
        self.drop_card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_WELL_PINE};
                border: 1.5px dashed {BORDER_MUTED};
                border-radius: 6px;
            }}
        """)
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            for url in event.mimeData().urls():
                fp = url.toLocalFile()
                if fp:
                    self.load_app(fp)
                    break
        elif event.mimeData().hasText():
            event.acceptProposedAction()
            txt = event.mimeData().text().strip()
            if txt:
                self.load_app(txt)
        else:
            super().dropEvent(event)


# =========================================================================
# Full-Screen Transparent Neural Tether Overlay (Static Solid Black Tethers)
# =========================================================================

class NeuralOverlayCanvas(QWidget):
    """
    Full-screen transparent click-through canvas spanning the primary screen.
    Renders solid, grounded, high-contrast Jet Black neural tethers (#0F1115, 2.2px stroke)
    with Signal Vermilion Red (#E63946) terminal node circles (6px diameter / 3.0px radius)
    at both connection endpoints between Dynamic Island (BOT) and the three floating windows (NP, AI, DASH).
    Frame-by-frame timer animation is disabled (0% idle CPU polling).
    """
    def __init__(self, island_window, parent=None):
        super().__init__(parent)
        self.island = island_window
        self.nodes = []  # list of (window, color_hex, offset_x)

        # Window Flags & Attributes for completely click-through transparent canvas
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self._update_canvas_geometry()

    def _update_canvas_geometry(self):
        screen = QGuiApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.virtualGeometry())

    def set_nodes(self, node_tuples: list):
        """
        Takes list of (FloatingNodeWindow, color_hex, offset_x_on_bot)
        """
        self.nodes = node_tuples
        for item in self.nodes:
            win = item[0]
            win.windowMoved.connect(self.update)
            win.closed.connect(self._check_active_nodes)

    def start_animation(self):
        self._update_canvas_geometry()
        self.show()
        self.update()

    def stop_animation(self):
        self.hide()

    def _check_active_nodes(self):
        active_count = sum(1 for item in self.nodes if item[0].isVisible())
        if active_count == 0:
            self.stop_animation()
        else:
            self.update()

    def get_bot_anchor(self, off_x: float = 0.0) -> QPointF:
        """Returns the dynamic anchor point on the bottom-center of the Dynamic Island."""
        geo = self.island.geometry()
        return QPointF(geo.x() + geo.width() / 2.0 + off_x, geo.y() + geo.height() - 2.0)

    def paintEvent(self, event):
        # Render static solid black neural tethers for all visible windows
        visible_nodes = [item for item in self.nodes if item[0].isVisible()]
        if not visible_nodes:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # Grounded solid Charcoal/Black pen: COLOR_TETHER_BLACK (#141816), 2.2px stroke
        black_pen = QPen(COLOR_TETHER_BLACK, 2.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

        for item in visible_nodes:
            win = item[0]
            off_x = item[2] if len(item) > 2 else 0.0

            # Start point spaced slightly across BOT pill
            start_pt = self.get_bot_anchor(off_x)

            # End point dynamically anchored to window
            end_pt = win.get_anchor_point(start_pt)

            # Cubic Bezier Control Points Math
            dy = abs(end_pt.y() - start_pt.y()) * 0.52
            if end_pt.y() >= start_pt.y():
                # Target is below island
                ctrl1 = QPointF(start_pt.x() + (off_x * 0.4), start_pt.y() + dy)
                ctrl2 = QPointF(end_pt.x(), end_pt.y() - dy)
            else:
                # Target is above island
                ctrl1 = QPointF(start_pt.x() + (off_x * 0.4), start_pt.y() - dy)
                ctrl2 = QPointF(end_pt.x(), end_pt.y() + dy)

            path = QPainterPath()
            path.moveTo(start_pt)
            path.cubicTo(ctrl1, ctrl2, end_pt)

            painter.setPen(black_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)

            # Terracotta Rust terminal anchor nodes (6px diameter / 3.0px radius) at both connection endpoints
            painter.setBrush(QBrush(COLOR_TERRACOTTA))
            painter.setPen(QPen(COLOR_TETHER_BLACK, 1.2))
            painter.drawEllipse(start_pt, 3.0, 3.0)
            painter.drawEllipse(end_pt, 3.0, 3.0)


# =========================================================================
# Workspace Manager (Coordinates Spawning & Lifecycle)
# =========================================================================

class WorkspaceManager(QObject):
    """
    Manages the lifecycle, placement, and tethering of the floating
    workspace windows (NP, AI, DASH, and up to 3 custom app windows: APP 4, APP 5, APP 6).
    """
    tabs_updated = Signal(list)

    def __init__(self, island_window):
        super().__init__()
        self.island = island_window

        # 3 Default floating windows scaled by +30% area
        self.np_window = NotepadNodeWindow()
        self.ai_window = AIChatNodeWindow()
        self.dash_window = OpenRouterDashboardWindow()
        self.any_window = self.dash_window  # Backward compatibility alias

        # Connect [+] buttons in default window headers
        self.np_window.plusClicked.connect(lambda: self.add_custom_tab())
        self.ai_window.plusClicked.connect(lambda: self.add_custom_tab())
        self.dash_window.plusClicked.connect(lambda: self.add_custom_tab())

        # Up to 3 custom app windows (for total 6 windows)
        self.custom_windows = []

        # Neural overlay canvas with static solid black tethers
        self.overlay = NeuralOverlayCanvas(self.island)
        self._update_overlay_nodes()

    def _update_overlay_nodes(self):
        all_wins = [self.np_window, self.ai_window, self.dash_window] + self.custom_windows
        n = len(all_wins)
        offsets = [-35.0 + i * (70.0 / (n - 1)) for i in range(n)] if n > 1 else [0.0]
        nodes_list = []
        for i, win in enumerate(all_wins):
            nodes_list.append((win, "#000000", offsets[i]))
        self.overlay.set_nodes(nodes_list)

    def get_tabs_data(self) -> list:
        tabs = [
            {"index": 0, "code": "NP", "name": "Quick Notepad", "accent": ACCENT_AMBER, "can_remove": False},
            {"index": 1, "code": "AI", "name": "Neural Studio", "accent": ACCENT_TERRACOTTA, "can_remove": False},
            {"index": 2, "code": "DASH", "name": "Live Telemetry", "accent": ACCENT_SAGE, "can_remove": False},
        ]
        accents = {4: "#2563EB", 5: "#EA580C", 6: "#7C3AED"}
        for i, win in enumerate(self.custom_windows):
            tab_num = i + 4
            tabs.append({
                "index": i + 3,
                "code": f"APP {tab_num}",
                "name": win.get_app_display_name(),
                "accent": accents.get(tab_num, "#2563EB"),
                "can_remove": True,
            })
        return tabs

    def add_custom_tab(self, app_target: str = None):
        if len(self.custom_windows) >= 3:
            logger.info("Maximum 6 extension tabs reached.")
            return None

        tab_num = len(self.custom_windows) + 4
        win = CustomAppNodeWindow(tab_index=tab_num)
        win.plusClicked.connect(lambda: self.add_custom_tab())
        win.closed.connect(self._on_window_closed)
        win.title_changed.connect(self._on_title_changed)

        self.custom_windows.append(win)
        self._update_overlay_nodes()

        if app_target:
            win.load_app(app_target)

        # If workspace is already open on desktop, spawn and show this new window immediately
        if any(w.isVisible() for w in [self.np_window, self.ai_window, self.dash_window]):
            self._position_single_window(win, len(self.custom_windows) + 2)
            win.show()
            self.overlay.start_animation()

        self.tabs_updated.emit(self.get_tabs_data())
        logger.info(f"Extension tab added: APP {tab_num} (Total tabs: {len(self.get_tabs_data())})")
        return win

    def remove_custom_tab(self, tab_idx: int):
        custom_idx = tab_idx - 3
        if 0 <= custom_idx < len(self.custom_windows):
            win = self.custom_windows.pop(custom_idx)
            win.close_node()
            # Re-index remaining custom windows
            for i, w in enumerate(self.custom_windows):
                w.tab_index = i + 4
                w.badge_lbl.setText(f"APP {i+4}")
            self._update_overlay_nodes()
            self.tabs_updated.emit(self.get_tabs_data())
            logger.info(f"Extension tab removed: index {tab_idx} (Total tabs: {len(self.get_tabs_data())})")

    def _on_window_closed(self):
        self._update_overlay_nodes()

    def _on_title_changed(self, tab_idx: int, title: str):
        self.tabs_updated.emit(self.get_tabs_data())

    def _position_single_window(self, win, idx: int):
        screen = QGuiApplication.primaryScreen()
        if not screen:
            return
        avail = screen.availableGeometry()
        center_x = avail.x() + avail.width() / 2.0
        island_bottom = self.island.y() + self.island.height()

        if idx == 3: # APP 4
            x = int(center_x + 560.0 - win.width() / 2.0)
            y = int(island_bottom + 68.0)
        elif idx == 4: # APP 5
            x = int(center_x - 560.0 - win.width() / 2.0)
            y = int(island_bottom + 68.0)
        else: # APP 6
            x = int(center_x - win.width() / 2.0)
            y = int(island_bottom + 260.0)

        x = max(avail.left() + 20, min(avail.right() - win.width() - 20, x))
        y = max(avail.top() + 60, min(avail.bottom() - win.height() - 20, y))
        win.move(x, y)

    def spawn_workspace(self):
        screen = QGuiApplication.primaryScreen()
        if not screen:
            return
        avail = screen.availableGeometry()

        center_x = avail.x() + avail.width() / 2.0
        island_bottom = self.island.y() + self.island.height()
        n = 3 + len(self.custom_windows)

        # 1. Position Base Windows
        if n == 3:
            self.ai_window.move(int(center_x - 218.0), int(island_bottom + 48.0))
            self.np_window.move(int(center_x - 400.0 - 155.0), int(island_bottom + 68.0))
            self.dash_window.move(int(center_x + 400.0 - 155.0), int(island_bottom + 68.0))
        elif n == 4:
            self.np_window.move(int(center_x - 580.0), int(island_bottom + 68.0))
            self.ai_window.move(int(center_x - 218.0), int(island_bottom + 48.0))
            self.dash_window.move(int(center_x + 230.0), int(island_bottom + 68.0))
            if len(self.custom_windows) >= 1:
                self.custom_windows[0].move(int(center_x + 560.0), int(island_bottom + 68.0))
        elif n == 5:
            self.np_window.move(int(center_x - 520.0), int(island_bottom + 48.0))
            self.ai_window.move(int(center_x - 218.0), int(island_bottom + 48.0))
            self.dash_window.move(int(center_x + 220.0), int(island_bottom + 48.0))
            if len(self.custom_windows) >= 1:
                self.custom_windows[0].move(int(center_x - 380.0), int(island_bottom + 270.0))
            if len(self.custom_windows) >= 2:
                self.custom_windows[1].move(int(center_x + 60.0), int(island_bottom + 270.0))
        else: # n == 6
            self.np_window.move(int(center_x - 540.0), int(island_bottom + 48.0))
            self.ai_window.move(int(center_x - 218.0), int(island_bottom + 48.0))
            self.dash_window.move(int(center_x + 230.0), int(island_bottom + 48.0))
            if len(self.custom_windows) >= 1:
                self.custom_windows[0].move(int(center_x - 540.0), int(island_bottom + 280.0))
            if len(self.custom_windows) >= 2:
                self.custom_windows[1].move(int(center_x - 165.0), int(island_bottom + 280.0))
            if len(self.custom_windows) >= 3:
                self.custom_windows[2].move(int(center_x + 230.0), int(island_bottom + 280.0))

        # Clamp all window positions within screen bounds
        all_wins = [self.np_window, self.ai_window, self.dash_window] + self.custom_windows
        for w in all_wins:
            cur_x = max(avail.left() + 20, min(avail.right() - w.width() - 20, w.x()))
            cur_y = max(avail.top() + 60, min(avail.bottom() - w.height() - 20, w.y()))
            w.move(cur_x, cur_y)
            w.show()

        self.dash_window.refresh_telemetry()
        self._update_overlay_nodes()
        self.overlay.start_animation()
        logger.info(f"Neural Workspace extended: {n} active nodes spawned with grounded neural tethers.")

    def focus_tab(self, tab_idx: int):
        all_wins = [self.np_window, self.ai_window, self.dash_window] + self.custom_windows
        if 0 <= tab_idx < len(all_wins):
            w = all_wins[tab_idx]
            w.show()
            w.raise_()
            w.activateWindow()

    def close_all(self):
        self.np_window.close_node()
        self.ai_window.close_node()
        self.dash_window.close_node()
        for w in self.custom_windows:
            w.close_node()
        self.overlay.stop_animation()
