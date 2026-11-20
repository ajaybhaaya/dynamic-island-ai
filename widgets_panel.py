"""
widgets_panel.py - Misty Sage & Terracotta Illustrated Editorial Theme
Windows 11 Dynamic Island Desktop Companion

Strictly extracted from the reference artwork:
- Atmospheric Gradient: Muted Sage-Teal Mist (#9CAFAA) -> Soft Fog Cream-Green (#CBD2C4) -> Warm Dry-Grass Sand (#D6CEB8)
- Recessed Wells / Inner Cards: Deep Forest Pine Slate (#5E6F68) & Warm Parchment (#EAE6DA)
- Primary CTA Accent: Rich Terracotta Rust (#B83B24) -> Warm Burnt Sienna (#D15238)
- Micro-Accents: Warm Amber-Peach (#E88D5A), Mahogany Bark (#6E2214), Forest Sage (#4A6B5D)
- Mandatory: AI Bot Avatar container stays 100% Pitch-Black (#050507)
- Typography: Heavy Display Headers (#FFFFFF bold), Wide-Tracked Nav Pills (letter-spacing: 1.8px),
  Clean Charcoal-Pine body text (#2B3531).
- 60 FPS Anti-Choppy Rendering: Anti-aliasing, TextAntiAliasing, SmoothPixmapTransform globally.
"""

import os
import sys
import ctypes
import time
import math
from collections import deque
import psutil
from network_worker import format_speed, get_ping_health_color
from PySide6.QtCore import (
    Qt,
    QTimer,
    QRectF,
    QPointF,
    Signal,
    Property,
    QPropertyAnimation,
    QEasingCurve,
    QVariantAnimation,
    QAbstractAnimation,
)
from PySide6.QtGui import (
    QPainter,
    QColor,
    QBrush,
    QPen,
    QFont,
    QFontMetrics,
    QPixmap,
    QCursor,
    QPainterPath,
    QGuiApplication,
    QLinearGradient,
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QFrame,
    QGraphicsDropShadowEffect,
    QTextEdit,
    QPlainTextEdit,
)

from avatar_widget import AvatarWidget, BotState
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
    BORDER_CHIP,
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
    get_editorial_font,
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
    INK_DARK,
    INK_MUTED,
    INK_FAINT,
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
    COLOR_BG_BEIGE,
    COLOR_BG_WELL,
    COLOR_BG_CARD,
    COLOR_BG_WHITE,
    COLOR_INK_BLACK,
    COLOR_INK_MUTED,
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
    draw_swiss_capsule,
    draw_retro_bevel,
)


# Windows Media Key Constants
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3
KEYEVENTF_KEYUP = 0x0002


def send_media_key(vk_code: int):
    """Dispatches a Windows Media virtual key press and release event."""
    try:
        ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
        ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)
    except Exception as e:
        print(f"Error dispatching media key: {e}")


def detect_file_type(filepath: str) -> tuple:
    """
    Detects document category, icon emoji, and theme color based on file extension.
    Returns: (type_name, icon_emoji, badge_color)
    """
    ext = os.path.splitext(filepath)[1].lower()
    mapping = {
        ".pdf": ("PDF Document", "📕", "#DC2626"),
        ".docx": ("Word Document", "📘", "#2563EB"),
        ".doc": ("Word Document", "📘", "#2563EB"),
        ".xlsx": ("Excel Spreadsheet", "📊", "#16A34A"),
        ".xls": ("Excel Spreadsheet", "📊", "#16A34A"),
        ".csv": ("CSV Spreadsheet", "📊", "#16A34A"),
        ".pptx": ("PowerPoint Presentation", "📙", "#EA580C"),
        ".ppt": ("PowerPoint Presentation", "📙", "#EA580C"),
        ".txt": ("Text Document", "📝", "#4B5563"),
        ".md": ("Markdown Document", "📝", "#4B5563"),
        ".rtf": ("Rich Text Document", "📝", "#4B5563"),
        ".py": ("Python Code", "🐍", "#0284C7"),
        ".js": ("JavaScript Code", "💻", "#CA8A04"),
        ".ts": ("TypeScript Code", "💻", "#0284C7"),
        ".html": ("HTML Document", "🌐", "#EA580C"),
        ".css": ("CSS Stylesheet", "🎨", "#2563EB"),
        ".json": ("JSON Data", "⚙️", "#7C3AED"),
        ".cpp": ("C++ Code", "💻", "#4F46E5"),
        ".c": ("C Code", "💻", "#4F46E5"),
        ".java": ("Java Code", "☕", "#EA580C"),
        ".zip": ("Zip Archive", "📦", "#CA8A04"),
        ".rar": ("RAR Archive", "📦", "#CA8A04"),
        ".7z": ("7-Zip Archive", "📦", "#CA8A04"),
        ".png": ("PNG Image", "🖼️", "#DB2777"),
        ".jpg": ("JPEG Image", "🖼️", "#DB2777"),
        ".jpeg": ("JPEG Image", "🖼️", "#DB2777"),
        ".gif": ("GIF Animation", "🖼️", "#DB2777"),
        ".svg": ("SVG Graphic", "🖼️", "#DB2777"),
        ".mp3": ("MP3 Audio", "🎵", "#0891B2"),
        ".wav": ("WAV Audio", "🎵", "#0891B2"),
        ".mp4": ("MP4 Video", "🎬", "#9333EA"),
        ".mkv": ("MKV Video", "🎬", "#9333EA"),
    }
    return mapping.get(ext, ("Document", "📄", "#4B5563"))


# =========================================================================
# Tactile Misty Sage & Terracotta Button
# =========================================================================

class GlassButton(QPushButton):
    """
    Tactile pill button in the Misty Sage & Terracotta illustrated editorial aesthetic.
    - Normal: Warm Parchment (#EAE6DA) fill with subtle #7A8B84 border and Deep Charcoal-Pine (#2B3531) text.
    - Active / Accent: Rich Terracotta Rust (#B83B24) fill with Mahogany Bark (#6E2214) border and pure white text.
    - Smooth 70ms micro-spring press deformation with 60 FPS anti-aliased rendering.
    """

    def __init__(
        self,
        text: str = "",
        icon_text: str = "",
        parent=None,
        is_pill: bool = False,
        size_override: tuple = None,
        is_accent: bool = False,
    ):
        super().__init__(text, parent)
        self.icon_text = icon_text
        self.is_pill = is_pill
        self.is_accent = is_accent
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)

        self._is_pressed = False
        self._is_hovered = False
        self._is_toggled = False
        self._press_scale = 1.0

        # Press animation (1.0 -> 0.95 -> 1.0 over 70ms)
        self._press_anim = QPropertyAnimation(self, b"press_scale")
        self._press_anim.setDuration(70)
        self._press_anim.setEasingCurve(QEasingCurve.OutQuad)

        if size_override:
            self.setFixedSize(size_override[0], size_override[1])
        elif is_pill:
            self.setFixedHeight(28)
            self.setMinimumWidth(54)
        else:
            self.setFixedSize(32, 32)

    def set_toggled_active(self, active: bool):
        self._is_toggled = active
        self.update()

    def get_press_scale(self) -> float:
        return self._press_scale

    def set_press_scale(self, val: float):
        self._press_scale = float(val)
        self.update()

    press_scale = Property(float, get_press_scale, set_press_scale)

    def enterEvent(self, event):
        self._is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._is_hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self._is_pressed = True
        self._press_anim.stop()
        self._press_anim.setStartValue(self._press_scale)
        self._press_anim.setEndValue(0.95)
        self._press_anim.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._is_pressed = False
        self._press_anim.stop()
        self._press_anim.setStartValue(self._press_scale)
        self._press_anim.setEndValue(1.0)
        self._press_anim.start()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        w = self.width()
        h = self.height()
        radius = (h / 2.0) if self.is_pill else 5.0

        painter.save()
        painter.translate(w / 2.0, h / 2.0)
        painter.scale(self._press_scale, self._press_scale)
        painter.translate(-w / 2.0, -h / 2.0)

        rect = QRectF(1.0, 1.0, w - 2.0, h - 2.0)
        is_active = self.is_accent or self._is_toggled

        if is_active:
            # Terracotta CTA fill
            if self._is_pressed:
                bg_color = QColor(ACCENT_PRESSED)
            elif self._is_hovered:
                bg_color = QColor(ACCENT_SIENNA)
            else:
                bg_color = QColor(ACCENT_TERRACOTTA)

            text_color = QColor("#FFFFFF")
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(QColor(ACCENT_MAHOGANY), 1.4))
            painter.drawRoundedRect(rect, radius, radius)

            # Soft 1px top highlight
            if not self._is_pressed:
                painter.setPen(QPen(QColor(255, 255, 255, 110), 1.0))
                painter.drawLine(int(rect.left() + 2), int(rect.top() + 1), int(rect.right() - 2), int(rect.top() + 1))
        else:
            # Warm Parchment Tactile Pill
            if self._is_pressed:
                bg_color = QColor("#DDD8CB")
            elif self._is_hovered:
                bg_color = QColor("#FAF8F2")
            else:
                bg_color = QColor(BG_PARCHMENT)

            text_color = COLOR_TEXT_CHARCOAL
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(COLOR_BORDER_MUTED, 1.2))
            painter.drawRoundedRect(rect, radius, radius)

            # Soft top bevel
            if not self._is_pressed:
                painter.setPen(QPen(QColor(255, 255, 255, 140), 1.0))
                painter.drawLine(int(rect.left() + 2), int(rect.top() + 1), int(rect.right() - 2), int(rect.top() + 1))

        # Button Label / Icon in Nav Pill font
        painter.setPen(text_color)
        font = get_nav_pill_font(size=8.4, weight=QFont.Bold, wide_spacing=True)
        painter.setFont(font)

        display_str = self.icon_text if self.icon_text else self.text()
        text_y_offset = 1.0 if self._is_pressed else 0.0
        draw_rect = rect.adjusted(0, text_y_offset, 0, text_y_offset)
        painter.drawText(draw_rect, Qt.AlignCenter, display_str)

        painter.restore()


# Backwards compatibility alias
TactileButton = GlassButton


# =========================================================================
# Misty Sage & Terracotta Liquid Sphere Gauge (Zero Glitches, Pure Fluid Motion)
# =========================================================================

class LiquidSphereGauge(QWidget):
    """
    Smooth spherical liquid-fill gauge displaying RAM %, CPU %, and CACHE (GB) in
    oversized display numerals inside Warm Parchment (#EAE6DA) rings and fluid
    dynamic wave fills in:
    - RAM: Terracotta Rust (#B83B24)
    - CPU: Warm Amber-Peach (#E88D5A)
    - CACHE: Forest Sage (#4A6B5D)
    Zero rectangular artifact bar glitches, silky smooth float interpolation (* 0.15) at 60 FPS!
    """

    def __init__(
        self,
        title: str,
        theme_type: str = "ram",
        parent=None,
    ):
        super().__init__(parent)
        self.title = title.upper()
        self.theme_type = theme_type.lower()
        self.setFixedSize(102, 102)
        self.setFocusPolicy(Qt.NoFocus)

        self._target_ratio = 0.0
        self._current_ratio = 0.0
        self._display_value = "0%"

        # Liquid color palettes strictly matching reference
        if self.theme_type == "ram":
            self.liquid_color = QColor(ACCENT_TERRACOTTA)    # Rich Terracotta Rust #B83B24
            self.liquid_crest = QColor(ACCENT_SIENNA)        # Warm Burnt Sienna #D15238
        elif self.theme_type == "cpu":
            self.liquid_color = QColor(ACCENT_AMBER)         # Warm Amber-Peach #E88D5A
            self.liquid_crest = QColor("#F4A261")
        else:
            self.liquid_color = QColor(ACCENT_SAGE)          # Forest Sage #4A6B5D
            self.liquid_crest = QColor("#6B8F80")

        # 60 FPS animation timer (16ms)
        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._on_frame)
        self._timer.start()

    def set_data(self, ratio: float, display_str: str):
        self._target_ratio = max(0.0, min(1.0, float(ratio)))
        self._display_value = display_str

    def _on_frame(self):
        # Smooth float lerp interpolation (* 0.15)
        diff = self._target_ratio - self._current_ratio
        if abs(diff) > 0.001:
            self._current_ratio += diff * 0.15
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        w = float(self.width())
        h = float(self.height())

        # 1. Top Title (e.g. RAM, CPU, CACHE) in Wide-Tracked Nav Pill font
        painter.setFont(get_nav_pill_font(size=7.6, weight=QFont.Bold, wide_spacing=True))
        painter.setPen(COLOR_TEXT_CHARCOAL)
        title_rect = QRectF(0, 1, w, 14)
        painter.drawText(title_rect, Qt.AlignCenter, self.title)

        # 2. Sphere Geometry (Diameter = 58px)
        diam = 58.0
        cx = w / 2.0
        cy = 15.0 + diam / 2.0
        sphere_rect = QRectF(cx - diam / 2.0, cy - diam / 2.0, diam, diam)

        # 3. Outer Sphere Ring in Warm Parchment (#EAE6DA) & subtle border (#7A8B84)
        painter.setBrush(QBrush(QColor(94, 111, 104, 50)))  # Recessed Pine Well Fill
        painter.setPen(QPen(COLOR_BORDER_MUTED, 1.4))
        painter.drawEllipse(sphere_rect)

        # 4. Animated Fluid Wave Fill clipped inside circular path
        clip_path = QPainterPath()
        clip_path.addEllipse(sphere_rect.adjusted(1.5, 1.5, -1.5, -1.5))
        painter.save()
        painter.setClipPath(clip_path)

        # Wave math
        t = time.time() * 3.5
        fill_ratio = max(0.04, min(0.96, self._current_ratio))
        base_water_y = sphere_rect.bottom() - (sphere_rect.height() * fill_ratio)
        wave_amp = 3.0 * (1.0 - abs(fill_ratio - 0.5) * 1.4)  # Flatten near full/empty

        # Back Wave (Crest)
        back_wave = QPainterPath()
        back_wave.moveTo(sphere_rect.left() - 4, sphere_rect.bottom() + 4)
        for x_step in range(int(sphere_rect.left() - 4), int(sphere_rect.right() + 8), 3):
            rel_x = x_step - sphere_rect.left()
            wy = base_water_y + math.sin(t + rel_x * 0.12) * wave_amp
            back_wave.lineTo(x_step, wy)
        back_wave.lineTo(sphere_rect.right() + 4, sphere_rect.bottom() + 4)
        back_wave.closeSubpath()

        painter.setBrush(QBrush(self.liquid_crest))
        painter.setPen(Qt.NoPen)
        painter.drawPath(back_wave)

        # Front Wave (Main Liquid)
        front_wave = QPainterPath()
        front_wave.moveTo(sphere_rect.left() - 4, sphere_rect.bottom() + 4)
        for x_step in range(int(sphere_rect.left() - 4), int(sphere_rect.right() + 8), 3):
            rel_x = x_step - sphere_rect.left()
            wy = base_water_y + math.sin(t * 1.2 + rel_x * 0.14 + 1.6) * wave_amp
            front_wave.lineTo(x_step, wy)
        front_wave.lineTo(sphere_rect.right() + 4, sphere_rect.bottom() + 4)
        front_wave.closeSubpath()

        painter.setBrush(QBrush(self.liquid_color))
        painter.drawPath(front_wave)

        # Specular top gloss reflection arc inside sphere
        spec_rect = sphere_rect.adjusted(4.0, 3.0, -4.0, -diam * 0.45)
        spec_grad = QLinearGradient(0, spec_rect.top(), 0, spec_rect.bottom())
        spec_grad.setColorAt(0.0, QColor(255, 255, 255, 100))
        spec_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(spec_grad))
        painter.drawEllipse(spec_rect)

        painter.restore()

        # 5. Inner Parchment Ring Edge
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(234, 230, 218, 200), 1.8))
        painter.drawEllipse(sphere_rect.adjusted(1.0, 1.0, -1.0, -1.0))

        # 6. Big Display Readout in Pure Chalk White with soft drop shadow
        num_font = get_display_font(size=11.2, weight=QFont.Black)
        painter.setFont(num_font)

        # Soft drop shadow for crisp readability against any liquid height
        shadow_rect = QRectF(sphere_rect.left(), sphere_rect.top() + 1.2, sphere_rect.width(), sphere_rect.height())
        painter.setPen(QColor(43, 53, 49, 160))
        painter.drawText(shadow_rect, Qt.AlignCenter, self._display_value)

        # Foreground White text
        painter.setPen(COLOR_TEXT_WHITE)
        painter.drawText(sphere_rect, Qt.AlignCenter, self._display_value)

        # 7. Bottom Status Subtext (e.g. 48% LOAD or AVAIL)
        painter.setFont(get_body_font(size=7.0, weight=QFont.DemiBold))
        painter.setPen(QColor(TEXT_MUTED))
        sub_text = f"{int(self._current_ratio * 100)}% LOAD" if self.theme_type != "cache" else "AVAILABLE"
        sub_rect = QRectF(0, sphere_rect.bottom() + 2, w, 13)
        painter.drawText(sub_rect, Qt.AlignCenter, sub_text)


# Compatibility aliases
SwissSegmentedGauge = LiquidSphereGauge
CircularGaugeWidget = LiquidSphereGauge


# =========================================================================
# Page 1: AI Companion & Screen-Aware Vision Hub (Misty Sage Edition)
# =========================================================================

class Page1Companion(QWidget):
    """
    Page 1: Pitch-black 66x66 avatar pod, warm parchment input with #7A8B84 border,
    Rich Terracotta Rust 'Sum' CTA button, tactile mic toggle, and archival output card.
    """
    request_screen_summary = Signal(str)
    request_voice_toggle = Signal()
    request_open_chat = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(14)

        # Avatar on the left: strictly 100% Pitch-Black container (#050507)
        self.avatar = AvatarWidget(size=66, parent=self)
        layout.addWidget(self.avatar, alignment=Qt.AlignVCenter)

        # Right column: Input row, buttons, and archival output card
        right_col = QVBoxLayout()
        right_col.setSpacing(8)
        right_col.setContentsMargins(0, 0, 0, 0)

        # Input & action buttons row
        top_row = QHBoxLayout()
        top_row.setSpacing(6)

        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Ask about screen or click Sum...")
        self.input_field.setFont(get_body_font(size=9.4, weight=QFont.Medium))
        self.input_field.setStyleSheet(PARCHMENT_INPUT_QSS)
        self.input_field.returnPressed.connect(self._on_submit)
        top_row.addWidget(self.input_field, stretch=1)

        # Primary Terracotta Red CTA Button
        self.btn_summary = GlassButton(icon_text="✨ SUM", parent=self, is_pill=True, is_accent=True)
        self.btn_summary.setFixedWidth(58)
        self.btn_summary.setToolTip("Analyze active screen via OpenRouter Vision")
        self.btn_summary.clicked.connect(self._on_submit)
        top_row.addWidget(self.btn_summary)

        self.btn_chat = GlassButton(icon_text="💬 CHAT", parent=self, is_pill=True)
        self.btn_chat.setFixedWidth(56)
        self.btn_chat.setToolTip("Follow-up in AI Chat with this screen analysis context")
        self.btn_chat.clicked.connect(self.request_open_chat.emit)
        top_row.addWidget(self.btn_chat)

        self.btn_voice = GlassButton(icon_text="🎙️", parent=self, is_pill=False)
        self.btn_voice.setToolTip("Toggle faster-whisper background voice commands")
        self.btn_voice.clicked.connect(self.request_voice_toggle.emit)
        top_row.addWidget(self.btn_voice)

        right_col.addLayout(top_row)

        # Archival Output Card with Terracotta structural top rule
        self.output_card = QLabel(self)
        self.output_card.setWordWrap(True)
        self.output_card.setFont(get_body_font(size=9.2, weight=QFont.Normal))
        self.output_card.setStyleSheet(f"""
            QLabel {{
                background-color: {BG_PARCHMENT};
                border: 1.2px solid {BORDER_MUTED};
                border-top: 2.8px solid {ACCENT_TERRACOTTA};
                border-radius: 5px;
                color: {TEXT_CHARCOAL};
                padding: 6px 10px;
                line-height: 1.35;
            }}
        """)
        self.output_card.setText("Ready. Click ✨ SUM or press Enter to analyze the active desktop.")

        scroll = QScrollArea(self)
        scroll.setWidget(self.output_card)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(82)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(MISTY_SCROLL_QSS)
        right_col.addWidget(scroll)

        layout.addLayout(right_col, stretch=1)

    def _on_submit(self):
        prompt = self.input_field.text().strip()
        self.output_card.setText("Analyzing active screen via OpenRouter Vision...")
        self.request_screen_summary.emit(prompt)

    def set_output_text(self, text: str, is_success: bool = True):
        self.output_card.setText(text)
        if is_success:
            self.avatar.set_state(BotState.HAPPY, duration_ms=1400)

    def set_voice_active(self, active: bool):
        self.btn_voice.set_toggled_active(active)
        if active:
            self.btn_voice.icon_text = "🔴"
        else:
            self.btn_voice.icon_text = "🎙️"
        self.btn_voice.update()


# =========================================================================
# Page 2: Media Playback Controller (Misty Sage Edition)
# =========================================================================

class MediaEqualizerWidget(QWidget):
    """5-bar animated frequency visualizer with high-contrast Terracotta / Pine Slate bars."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(62, 26)
        self._is_playing = False
        self._bars = [0.3, 0.6, 0.9, 0.5, 0.4]

        self._timer = QTimer(self)
        self._timer.setInterval(45)
        self._timer.timeout.connect(self._animate_bars)
        self._timer.start()

    def set_playing(self, playing: bool):
        self._is_playing = playing
        self.update()

    def _animate_bars(self):
        if self._is_playing:
            t = time.time() * 9.0
            self._bars = [
                0.2 + 0.7 * abs(math.sin(t + 0.3)),
                0.2 + 0.8 * abs(math.sin(t * 1.3 + 1.2)),
                0.3 + 0.7 * abs(math.cos(t * 0.9 + 2.1)),
                0.2 + 0.75 * abs(math.sin(t * 1.5 + 0.7)),
                0.15 + 0.65 * abs(math.cos(t * 1.1 + 3.0)),
            ]
        else:
            self._bars = [0.18, 0.18, 0.18, 0.18, 0.18]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        w = self.width()
        h = self.height()
        bar_w = 4.5
        gap = 4.0
        total_w = len(self._bars) * bar_w + (len(self._bars) - 1) * gap
        start_x = (w - total_w) / 2.0

        for i, val in enumerate(self._bars):
            bar_h = max(3.0, val * (h - 4.0))
            x = start_x + i * (bar_w + gap)
            y = h - 2.0 - bar_h

            if self._is_playing:
                painter.setBrush(QBrush(COLOR_TERRACOTTA))
            else:
                painter.setBrush(QBrush(COLOR_PINE_SLATE))

            painter.setPen(QPen(COLOR_BORDER_MUTED, 1.0))
            painter.drawRoundedRect(QRectF(x, y, bar_w, bar_h), 1.5, 1.5)


class Page2Media(QWidget):
    """
    Page 2: Deep Pine-Slate Plate (#3E4A45), Heavy Display title in Chalk White (#FFFFFF),
    and prominent Terracotta Play/Pause CTA.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_playing = True

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        # Deep Pine-Slate Header Plate (#3E4A45)
        header_plate = QFrame(self)
        header_plate.setFixedHeight(48)
        header_plate.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_PINE_PLATE};
                border: 1.2px solid {BORDER_MUTED};
                border-radius: 6px;
            }}
        """)
        h_lay = QHBoxLayout(header_plate)
        h_lay.setContentsMargins(10, 4, 10, 4)
        h_lay.setSpacing(10)

        info_col = QVBoxLayout()
        info_col.setSpacing(1)

        self.lbl_title = QLabel("Windows Media Session", header_plate)
        self.lbl_title.setFont(get_display_font(size=11.0, weight=QFont.Black))
        self.lbl_title.setStyleSheet("color: #FFFFFF; border: none; background: transparent;")

        self.lbl_artist = QLabel("System Audio Stream • Playing", header_plate)
        self.lbl_artist.setFont(get_body_font(size=8.5, weight=QFont.Medium))
        self.lbl_artist.setStyleSheet("color: #CBD2C4; border: none; background: transparent;")

        info_col.addWidget(self.lbl_title)
        info_col.addWidget(self.lbl_artist)
        h_lay.addLayout(info_col, stretch=1)

        # Equalizer
        self.equalizer = MediaEqualizerWidget(header_plate)
        self.equalizer.set_playing(self._is_playing)
        h_lay.addWidget(self.equalizer, alignment=Qt.AlignVCenter)

        layout.addWidget(header_plate)

        # Playback controls row with tactile buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)
        btn_row.setAlignment(Qt.AlignCenter)

        self.btn_prev = GlassButton(icon_text="⏮", parent=self, is_pill=False, size_override=(34, 34))
        self.btn_prev.setToolTip("Previous Track")
        self.btn_prev.clicked.connect(self._on_prev)

        # Prominent Terracotta Play/Pause CTA
        self.btn_play = GlassButton(
            icon_text="⏸" if self._is_playing else "▶",
            parent=self,
            is_pill=False,
            size_override=(42, 42),
            is_accent=True,
        )
        self.btn_play.setToolTip("Play / Pause")
        self.btn_play.clicked.connect(self._on_toggle_play)

        self.btn_next = GlassButton(icon_text="⏭", parent=self, is_pill=False, size_override=(34, 34))
        self.btn_next.setToolTip("Next Track")
        self.btn_next.clicked.connect(self._on_next)

        btn_row.addWidget(self.btn_prev)
        btn_row.addWidget(self.btn_play)
        btn_row.addWidget(self.btn_next)

        layout.addLayout(btn_row)

        # Periodic check for active windows playing media
        self._media_poll_timer = QTimer(self)
        self._media_poll_timer.setInterval(2500)
        self._media_poll_timer.timeout.connect(self._detect_media_titles)
        self._media_poll_timer.start()

    def _on_prev(self):
        send_media_key(VK_MEDIA_PREV_TRACK)

    def _on_next(self):
        send_media_key(VK_MEDIA_NEXT_TRACK)

    def _on_toggle_play(self):
        send_media_key(VK_MEDIA_PLAY_PAUSE)
        self._is_playing = not self._is_playing
        self.btn_play.icon_text = "⏸" if self._is_playing else "▶"
        self.btn_play.update()
        self.equalizer.set_playing(self._is_playing)
        status_str = "Playing" if self._is_playing else "Paused"
        self.lbl_artist.setText(f"System Audio Stream • {status_str}")

    def _detect_media_titles(self):
        try:
            titles = []

            def enum_cb(hwnd, lparam):
                if ctypes.windll.user32.IsWindowVisible(hwnd):
                    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buff = ctypes.create_unicode_buffer(length + 1)
                        ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                        title = buff.value
                        if any(k in title.lower() for k in ["spotify", "youtube", "music", "vlc", "soundcloud"]):
                            titles.append(title)
                return True

            cb_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
            ctypes.windll.user32.EnumWindows(cb_type(enum_cb), 0)

            if titles:
                t = titles[0]
                if " - " in t:
                    parts = t.split(" - ")
                    self.lbl_title.setText(parts[0][:26])
                    self.lbl_artist.setText(parts[1][:30])
                else:
                    self.lbl_title.setText(t[:28])
        except Exception:
            pass


# =========================================================================
# Connection Health Status Dot & Network Sparkline
# =========================================================================

class StatusDotWidget(QWidget):
    """
    Crisp 6px anti-aliased connection health status dot.
    - Healthy (< 70ms): Forest Sage Green (#22C55E / #4A6B5D)
    - Moderate (70ms - 160ms): Warm Amber (#E88D5A)
    - High Latency / Offline (> 160ms or offline): Terracotta Rust (#B83B24)
    """
    def __init__(self, size: int = 6, parent=None):
        super().__init__(parent)
        self.dot_size = size
        self.setFixedSize(size + 2, size + 2)
        self._color = QColor("#4A6B5D")

    def set_status(self, ping_ms: int, is_online: bool):
        hex_color = get_ping_health_color(ping_ms, is_online)
        self._color = QColor(hex_color)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        cx = self.width() / 2.0
        cy = self.height() / 2.0
        r = self.dot_size / 2.0

        painter.setBrush(QBrush(self._color))
        painter.setPen(QPen(QColor(15, 23, 42, 100), 0.8))
        painter.drawEllipse(QRectF(cx - r, cy - r, self.dot_size, self.dot_size))


class NetworkSparkline(QWidget):
    """
    Lightweight 30-point rolling sparkline graph for Page 3 System Telemetry.
    Terracotta Rust (#B83B24) download stroke and Forest Sage (#4A6B5D) upload stroke.
    Renders with anti-aliasing in < 0.1ms.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setMinimumWidth(130)
        self.dl_history = deque([0.0] * 30, maxlen=30)
        self.ul_history = deque([0.0] * 30, maxlen=30)

    def add_sample(self, dl_bps: float, ul_bps: float):
        self.dl_history.append(float(dl_bps))
        self.ul_history.append(float(ul_bps))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        w = float(self.width())
        h = float(self.height())
        rect = QRectF(1.0, 1.0, w - 2.0, h - 2.0)

        # Background well with subtle border
        painter.setBrush(QBrush(QColor(94, 111, 104, 30)))
        painter.setPen(QPen(QColor(122, 139, 132, 90), 1.0))
        painter.drawRoundedRect(rect, 4.0, 4.0)

        # Calculate max scale across both histories (min 50 KB/s floor)
        max_val = max(max(self.dl_history), max(self.ul_history), 50.0 * 1024.0)

        inner_w = w - 8.0
        inner_h = h - 6.0
        base_y = h - 3.0
        n = len(self.dl_history)
        if n < 2:
            return

        dx = inner_w / (n - 1)

        # 1. Download Path (Terracotta Rust #B83B24)
        dl_path = QPainterPath()
        dl_points = []
        for i, val in enumerate(self.dl_history):
            px = 4.0 + i * dx
            norm = min(1.0, val / max_val)
            py = base_y - (norm * (inner_h - 2.0))
            dl_points.append(QPointF(px, py))

        dl_path.moveTo(dl_points[0])
        for pt in dl_points[1:]:
            dl_path.lineTo(pt)

        # Download gradient fill under line
        dl_fill = QPainterPath(dl_path)
        dl_fill.lineTo(dl_points[-1].x(), base_y)
        dl_fill.lineTo(dl_points[0].x(), base_y)
        dl_fill.closeSubpath()

        grad = QLinearGradient(0, 3, 0, base_y)
        grad.setColorAt(0.0, QColor(184, 59, 36, 65))
        grad.setColorAt(1.0, QColor(184, 59, 36, 5))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.NoPen)
        painter.drawPath(dl_fill)

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(184, 59, 36), 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawPath(dl_path)

        # 2. Upload Path (Pine Sage #4A6B5D)
        ul_path = QPainterPath()
        ul_points = []
        for i, val in enumerate(self.ul_history):
            px = 4.0 + i * dx
            norm = min(1.0, val / max_val)
            py = base_y - (norm * (inner_h - 2.0))
            ul_points.append(QPointF(px, py))

        ul_path.moveTo(ul_points[0])
        for pt in ul_points[1:]:
            ul_path.lineTo(pt)

        painter.setPen(QPen(QColor(74, 107, 93), 1.3, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawPath(ul_path)


# =========================================================================
# Page 3: System Telemetry (Liquid Spheres & Live Network Latency Strip)
# =========================================================================

class Page3Telemetry(QWidget):
    """
    Page 3: Live RAM usage, CPU load, and Available memory rendered via
    3 smooth spherical liquid gauges, plus a real-time Live Network & Latency Strip:
    - Left: Live Download (↓), Upload (↑), and Ping (ms) in bold tabular numerals.
    - Center: 30-point rolling NetworkSparkline with Terracotta download & Pine upload curves.
    - Right: NET / API ping target toggle and Hide/Show pill ticker switch.
    """
    ping_target_changed = Signal(str)
    toggle_pill_ticker = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.NoFocus)
        self._target_is_api = False
        self._ticker_visible = True
        self._peak_dl_bps = 0.0

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 3, 12, 5)
        main_layout.setSpacing(3)
        main_layout.setAlignment(Qt.AlignCenter)

        # Top row: 3 Liquid Spherical Gauges (RAM: Terracotta, CPU: Amber, Cache: Forest Sage)
        gauges_row = QHBoxLayout()
        gauges_row.setContentsMargins(0, 0, 0, 0)
        gauges_row.setSpacing(14)
        gauges_row.setAlignment(Qt.AlignCenter)

        self.gauge_ram = LiquidSphereGauge("RAM", theme_type="ram", parent=self)
        self.gauge_cpu = LiquidSphereGauge("CPU", theme_type="cpu", parent=self)
        self.gauge_cache = LiquidSphereGauge("CACHE", theme_type="cache", parent=self)

        gauges_row.addWidget(self.gauge_ram)
        gauges_row.addWidget(self.gauge_cpu)
        gauges_row.addWidget(self.gauge_cache)
        main_layout.addLayout(gauges_row)

        # Bottom row: Recessed Live Network & API Latency Strip Card
        self.net_strip = QFrame(self)
        self.net_strip.setFixedHeight(40)
        self.net_strip.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_WELL_PINE};
                border: 1px solid {BORDER_MUTED};
                border-radius: 8px;
            }}
        """)
        strip_lay = QHBoxLayout(self.net_strip)
        strip_lay.setContentsMargins(10, 2, 10, 2)
        strip_lay.setSpacing(10)

        # Left Column: Speeds & Ping
        left_col = QVBoxLayout()
        left_col.setSpacing(1)
        left_col.setAlignment(Qt.AlignVCenter)

        row_speeds = QHBoxLayout()
        row_speeds.setSpacing(6)
        row_speeds.setContentsMargins(0, 0, 0, 0)

        lbl_dl_arr = QLabel("↓", self.net_strip)
        lbl_dl_arr.setFont(QFont("Consolas", 9, QFont.Bold))
        lbl_dl_arr.setStyleSheet("color: #B83B24; border: none; background: transparent;")

        self.lbl_dl_val = QLabel("0K", self.net_strip)
        self.lbl_dl_val.setFont(QFont("Consolas", 8, QFont.Bold))
        self.lbl_dl_val.setStyleSheet(f"color: {TEXT_CHARCOAL}; border: none; background: transparent;")

        lbl_ul_arr = QLabel("↑", self.net_strip)
        lbl_ul_arr.setFont(QFont("Consolas", 9, QFont.Bold))
        lbl_ul_arr.setStyleSheet("color: #4A6B5D; border: none; background: transparent;")

        self.lbl_ul_val = QLabel("0K", self.net_strip)
        self.lbl_ul_val.setFont(QFont("Consolas", 8, QFont.Bold))
        self.lbl_ul_val.setStyleSheet(f"color: {TEXT_CHARCOAL}; border: none; background: transparent;")

        row_speeds.addWidget(lbl_dl_arr)
        row_speeds.addWidget(self.lbl_dl_val)
        row_speeds.addWidget(lbl_ul_arr)
        row_speeds.addWidget(self.lbl_ul_val)
        row_speeds.addStretch(1)

        row_ping = QHBoxLayout()
        row_ping.setSpacing(4)
        row_ping.setContentsMargins(0, 0, 0, 0)

        self.dot_strip = StatusDotWidget(size=6, parent=self.net_strip)
        self.lbl_ping_val = QLabel("--ms", self.net_strip)
        self.lbl_ping_val.setFont(QFont("Consolas", 8, QFont.Bold))
        self.lbl_ping_val.setStyleSheet(f"color: {TEXT_CHARCOAL}; border: none; background: transparent;")

        self.lbl_peak_val = QLabel("Peak: 0K", self.net_strip)
        self.lbl_peak_val.setFont(get_body_font(size=7.2, weight=QFont.Medium))
        self.lbl_peak_val.setStyleSheet(f"color: {TEXT_MUTED}; border: none; background: transparent;")

        row_ping.addWidget(self.dot_strip, alignment=Qt.AlignVCenter)
        row_ping.addWidget(self.lbl_ping_val, alignment=Qt.AlignVCenter)
        row_ping.addSpacing(3)
        row_ping.addWidget(self.lbl_peak_val, alignment=Qt.AlignVCenter)
        row_ping.addStretch(1)

        left_col.addLayout(row_speeds)
        left_col.addLayout(row_ping)
        strip_lay.addLayout(left_col)

        # Center: NetworkSparkline
        self.sparkline = NetworkSparkline(self.net_strip)
        strip_lay.addWidget(self.sparkline, stretch=1)

        # Right Column: Controls (Ping Target & Ticker Visibility Toggle)
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(5)
        ctrl_row.setAlignment(Qt.AlignVCenter)

        self.btn_ping_target = QPushButton("NET", self.net_strip)
        self.btn_ping_target.setFixedSize(38, 22)
        self.btn_ping_target.setCursor(Qt.PointingHandCursor)
        self.btn_ping_target.setFont(get_nav_pill_font(size=7.2, weight=QFont.Bold))
        self.btn_ping_target.setToolTip("Click to toggle ping target: NET (1.1.1.1) ⇄ API (openrouter.ai)")
        self.btn_ping_target.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_PARCHMENT};
                color: {TEXT_CHARCOAL};
                border: 1px solid {BORDER_MUTED};
                border-radius: 4px;
                padding: 1px 4px;
            }}
            QPushButton:hover {{
                background-color: #FAF8F2;
                border-color: {ACCENT_TERRACOTTA};
                color: {ACCENT_TERRACOTTA};
            }}
            QPushButton:pressed {{
                background-color: {ACCENT_PRESSED};
                color: #FFFFFF;
            }}
        """)
        self.btn_ping_target.clicked.connect(self._toggle_ping_target)
        ctrl_row.addWidget(self.btn_ping_target)

        self.btn_toggle_pill = QPushButton("👁", self.net_strip)
        self.btn_toggle_pill.setFixedSize(22, 22)
        self.btn_toggle_pill.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_pill.setFont(get_nav_pill_font(size=8.5, weight=QFont.Bold))
        self.btn_toggle_pill.setToolTip("Toggle live network ticker visibility in collapsed pill")
        self.btn_toggle_pill.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_PARCHMENT};
                color: {TEXT_CHARCOAL};
                border: 1px solid {BORDER_MUTED};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #FAF8F2;
                border-color: {ACCENT_TERRACOTTA};
                color: {ACCENT_TERRACOTTA};
            }}
            QPushButton:pressed {{
                background-color: {ACCENT_PRESSED};
                color: #FFFFFF;
            }}
        """)
        self.btn_toggle_pill.clicked.connect(self._toggle_pill_visibility)
        ctrl_row.addWidget(self.btn_toggle_pill)

        strip_lay.addLayout(ctrl_row)
        main_layout.addWidget(self.net_strip)

        # 1000ms polling timer for CPU/RAM/Cache
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._poll_telemetry)
        self._timer.start()

        self._poll_telemetry()

    def _toggle_ping_target(self):
        self._target_is_api = not self._target_is_api
        if self._target_is_api:
            self.btn_ping_target.setText("API")
            self.btn_ping_target.setToolTip("Target: openrouter.ai (Click to switch to NET)")
            self.ping_target_changed.emit("openrouter.ai")
        else:
            self.btn_ping_target.setText("NET")
            self.btn_ping_target.setToolTip("Target: 1.1.1.1 (Click to switch to API)")
            self.ping_target_changed.emit("1.1.1.1")

    def _toggle_pill_visibility(self):
        self._ticker_visible = not self._ticker_visible
        self.btn_toggle_pill.setText("👁" if self._ticker_visible else "✕")
        self.toggle_pill_ticker.emit(self._ticker_visible)

    def update_network_data(self, dl_bps: float, ul_bps: float, ping_ms: int, is_online: bool):
        self._peak_dl_bps = max(self._peak_dl_bps, dl_bps)
        self.lbl_dl_val.setText(format_speed(dl_bps))
        self.lbl_ul_val.setText(format_speed(ul_bps))
        self.lbl_ping_val.setText(f"{ping_ms}ms" if is_online and ping_ms >= 0 else "--ms")
        self.lbl_peak_val.setText(f"Peak: {format_speed(self._peak_dl_bps)}")
        self.dot_strip.set_status(ping_ms, is_online)
        self.sparkline.add_sample(dl_bps, ul_bps)

    def _poll_telemetry(self):
        try:
            mem = psutil.virtual_memory()
            avail_gb = mem.available / (1024 ** 3)
            ram_ratio = mem.percent / 100.0

            cpu_pct = psutil.cpu_percent()
            cpu_ratio = cpu_pct / 100.0

            total_gb = mem.total / (1024 ** 3)
            cache_ratio = max(0.0, min(1.0, avail_gb / (total_gb if total_gb > 0 else 16.0)))

            self.gauge_ram.set_data(ram_ratio, f"{int(mem.percent)}%")
            self.gauge_cpu.set_data(cpu_ratio, f"{int(cpu_pct)}%")
            self.gauge_cache.set_data(cache_ratio, f"{avail_gb:.1f}G")
        except Exception as e:
            print(f"Telemetry error: {e}")


# =========================================================================
# Page 4: Document Shelf - Misty Sage Chip Launcher
# =========================================================================

def get_file_icon(filepath: str, size: int = 20) -> QPixmap:
    """Dynamically renders the standard application badge based on file extension."""
    ext = os.path.splitext(filepath)[1].lower()

    def make_badge(bg_color: str, symbol: str) -> QPixmap:
        pix = QPixmap(size, size)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.TextAntialiasing, True)
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)
        p.setBrush(QColor(bg_color))
        p.setPen(QPen(COLOR_BORDER_MUTED, 1.0))
        p.drawRoundedRect(QRectF(1, 1, size - 2, size - 2), 3, 3)
        p.setPen(QColor("#FFFFFF"))
        font = get_nav_pill_font(size=6.8, weight=QFont.Bold, wide_spacing=False)
        p.setFont(font)
        p.drawText(QRectF(1, 1, size - 2, size - 2), Qt.AlignCenter, symbol)
        p.end()
        return pix

    if ext == ".pdf":
        return make_badge("#B83B24", "PDF")
    elif ext in (".docx", ".doc"):
        return make_badge("#3B687C", "DOC")
    elif ext in (".xlsx", ".xls", ".csv"):
        return make_badge("#4A6B5D", "XLS")
    elif ext in (".pptx", ".ppt"):
        return make_badge("#E88D5A", "PPT")
    elif ext in (".py", ".js", ".ts", ".cpp", ".java", ".json", ".html", ".css"):
        return make_badge("#5E6F68", "</>")
    elif ext in (".zip", ".rar", ".7z"):
        return make_badge("#C28B47", "ZIP")
    elif ext in (".png", ".jpg", ".jpeg", ".svg", ".gif"):
        return make_badge("#A6564B", "IMG")

    return make_badge("#6B7C75", "DOC")


class FileChip(QFrame):
    """
    Parchment-bordered interactive document chip (#EAE6DA fill, 1.2px #7A8B84 border,
    truncated bold filename, click-to-open via os.startfile).
    """
    file_clicked = Signal(str)

    def __init__(self, filepath: str, parent=None):
        super().__init__(parent)
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.setFixedHeight(30)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(f"Click to open:\n{self.filepath}")

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_PARCHMENT};
                border: 1.2px solid {BORDER_MUTED};
                border-radius: 5px;
            }}
            QFrame:hover {{
                background-color: #FAF8F2;
                border: 1.4px solid {ACCENT_TERRACOTTA};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 10, 0)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignVCenter)

        # Standard application icon badge
        self.lbl_icon = QLabel(self)
        self.lbl_icon.setFixedSize(20, 20)
        self.lbl_icon.setStyleSheet("border: none; background: transparent;")
        self.lbl_icon.setPixmap(get_file_icon(self.filepath, 18))
        layout.addWidget(self.lbl_icon)

        # Truncated bold filename in Deep Charcoal
        font = get_body_font(size=9.2, weight=QFont.Bold)
        fm = QFontMetrics(font)
        elided_name = fm.elidedText(self.filename, Qt.ElideRight, 136)

        self.lbl_name = QLabel(elided_name, self)
        self.lbl_name.setFont(font)
        self.lbl_name.setStyleSheet(f"color: {TEXT_CHARCOAL}; border: none; background: transparent;")
        layout.addWidget(self.lbl_name)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            try:
                os.startfile(self.filepath)
            except Exception:
                QGuiApplication.clipboard().setText(self.filepath)
            self.file_clicked.emit(self.filepath)
        super().mouseReleaseEvent(event)


class Page4Shelf(QWidget):
    """
    Page 4: Clean, icon-centric interactive File Chip Shelf with recessed Pine drop-well.
    """
    file_opened = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dropped_files = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(6)

        # Header Row
        top_row = QHBoxLayout()
        lbl_head = QLabel("Recent Document Shelf", self)
        lbl_head.setFont(get_display_font(size=10.5, weight=QFont.Black))
        lbl_head.setStyleSheet(f"color: {TEXT_CHARCOAL};")
        top_row.addWidget(lbl_head)
        top_row.addStretch(1)

        # Clear Shelf Button
        self.btn_clear = GlassButton(icon_text="✖ CLEAR", parent=self, is_pill=True)
        self.btn_clear.setFixedSize(68, 22)
        self.btn_clear.setToolTip("Clear all documents from shelf")
        self.btn_clear.clicked.connect(self._clear_shelf)
        top_row.addWidget(self.btn_clear)

        layout.addLayout(top_row)

        # Recessed Pine Drop-Well (rgba(94, 111, 104, 0.20) with dashed 1.5px border)
        self.shelf_well = QFrame(self)
        self.shelf_well.setFixedHeight(74)
        self.shelf_well.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(94, 111, 104, 0.20);
                border: 1.5px dashed {BORDER_MUTED};
                border-radius: 6px;
            }}
        """)
        self.shelf_layout = QGridLayout(self.shelf_well)
        self.shelf_layout.setContentsMargins(6, 6, 6, 6)
        self.shelf_layout.setSpacing(6)
        layout.addWidget(self.shelf_well)

        self._render_shelf()

        # Archival notification / quote bar
        self.lbl_quote = QLabel(self)
        self.lbl_quote.setFont(get_body_font(size=8.5, weight=QFont.Medium))
        self.lbl_quote.setStyleSheet(f"""
            QLabel {{
                background-color: {BG_PARCHMENT_LIGHT};
                border: 1.2px solid {BORDER_MUTED};
                border-radius: 5px;
                color: {TEXT_MUTED};
                padding: 4px 8px;
            }}
        """)
        self.quotes = [
            "💡 Click any document chip to open it instantly in its default program.",
            "📂 Drag & drop files onto the Dynamic Island to pin them (up to 4 items).",
            "⚡ Press Ctrl+Shift+H to immediately minimize all other windows.",
            "✨ Press F5 or refresh to make your AI companion bounce happily."
        ]
        self._quote_idx = 0
        self.lbl_quote.setText(self.quotes[0])
        layout.addWidget(self.lbl_quote)

        # Quote rotation timer
        self._quote_timer = QTimer(self)
        self._quote_timer.setInterval(7000)
        self._quote_timer.timeout.connect(self._rotate_quote)
        self._quote_timer.start()

    def add_file(self, filepath: str):
        if filepath:
            if filepath in self.dropped_files:
                self.dropped_files.remove(filepath)
            self.dropped_files.insert(0, filepath)
            if len(self.dropped_files) > 4:
                self.dropped_files = self.dropped_files[:4]
            self._render_shelf()

    def _render_shelf(self):
        while self.shelf_layout.count():
            item = self.shelf_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not self.dropped_files:
            empty_lbl = QLabel("Drop files onto capsule to pin (PDF, DOCX, Code • Max 4)", self.shelf_well)
            empty_lbl.setFont(get_body_font(size=8.8, weight=QFont.Medium))
            empty_lbl.setStyleSheet(f"color: {TEXT_MUTED}; border: none; background: transparent;")
            empty_lbl.setAlignment(Qt.AlignCenter)
            self.shelf_layout.addWidget(empty_lbl, 0, 0, 1, 2)
            return

        for i, filepath in enumerate(self.dropped_files):
            row = i // 2
            col = i % 2
            chip = FileChip(filepath, self.shelf_well)
            chip.file_clicked.connect(self.file_opened.emit)
            self.shelf_layout.addWidget(chip, row, col)

    def _clear_shelf(self):
        self.dropped_files.clear()
        self._render_shelf()

    def _rotate_quote(self):
        self._quote_idx = (self._quote_idx + 1) % len(self.quotes)
        self.lbl_quote.setText(self.quotes[self._quote_idx])


# =========================================================================
# Page 5: Quick AI Assistant (Direct OpenRouter Q&A, Misty Sage Edition)
# =========================================================================

class Page5Chat(QWidget):
    """
    Page 5: Direct quick Q&A with the AI Agent powered by OpenRouter API.
    - Model badge in clean Chalk White (#FFFFFF) with #2B3531 text.
    - Response card in Warm Parchment (#EAE6DA) with Terracotta accent bar.
    - Rich Terracotta Rust CTA 'Ask' button.
    """
    request_chat_question = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(6)

        # Header Row
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        self.lbl_header = QLabel("⚡ Quick AI Assistant", self)
        self.lbl_header.setFont(get_display_font(size=10.5, weight=QFont.Black))
        self.lbl_header.setStyleSheet(f"color: {TEXT_CHARCOAL};")

        self.lbl_model_badge = QLabel("GPT-4O-MINI", self)
        self.lbl_model_badge.setFont(get_nav_pill_font(size=7.5, weight=QFont.Bold))
        self.lbl_model_badge.setStyleSheet(f"""
            QLabel {{
                background-color: #FFFFFF;
                border: 1.2px solid {BORDER_MUTED};
                border-radius: 4px;
                color: {TEXT_CHARCOAL};
                padding: 1px 7px;
                letter-spacing: 1.0px;
            }}
        """)

        self.lbl_status = QLabel("Ready", self)
        self.lbl_status.setFont(get_body_font(size=8.5, weight=QFont.Medium))
        self.lbl_status.setStyleSheet(f"color: {TEXT_MUTED};")

        self.lbl_screen_badge = QLabel("👁️ Screen Aware", self)
        self.lbl_screen_badge.setFont(get_nav_pill_font(size=7.5, weight=QFont.Bold, wide_spacing=False))
        self.lbl_screen_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {ACCENT_SAGE};
                border: 1.2px solid {BORDER_MUTED};
                border-radius: 4px;
                color: #FFFFFF;
                padding: 1px 7px;
            }}
        """)
        self.lbl_screen_badge.setVisible(False)

        top_row.addWidget(self.lbl_header)
        top_row.addWidget(self.lbl_model_badge)
        top_row.addWidget(self.lbl_screen_badge)
        top_row.addWidget(self.lbl_status)
        top_row.addStretch(1)

        # Action buttons
        self.btn_copy = GlassButton(icon_text="📋", parent=self, is_pill=False, size_override=(24, 24))
        self.btn_copy.setToolTip("Copy response to clipboard")
        self.btn_copy.clicked.connect(self._copy_response)
        top_row.addWidget(self.btn_copy)

        self.btn_clear = GlassButton(icon_text="🧹", parent=self, is_pill=False, size_override=(24, 24))
        self.btn_clear.setToolTip("Clear conversation")
        self.btn_clear.clicked.connect(self._clear_conversation)
        top_row.addWidget(self.btn_clear)

        layout.addLayout(top_row)

        # Archival Response Card
        self.output_card = QLabel(self)
        self.output_card.setWordWrap(True)
        self.output_card.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.output_card.setFont(get_body_font(size=9.2, weight=QFont.Normal))
        self.output_card.setStyleSheet(f"""
            QLabel {{
                background-color: {BG_PARCHMENT};
                border: 1.2px solid {BORDER_MUTED};
                border-top: 2.8px solid {ACCENT_TERRACOTTA};
                border-radius: 5px;
                color: {TEXT_CHARCOAL};
                padding: 8px 10px;
                line-height: 1.35;
            }}
        """)
        self.output_card.setText("👋 Hello! Ask me any question directly and I'll answer right away via OpenRouter.")

        self.scroll = QScrollArea(self)
        self.scroll.setWidget(self.output_card)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(78)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(MISTY_SCROLL_QSS)
        layout.addWidget(self.scroll)

        # Input & Send Row
        input_row = QHBoxLayout()
        input_row.setSpacing(6)

        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Ask your AI assistant anything...")
        self.input_field.setFont(get_body_font(size=9.2, weight=QFont.Normal))
        self.input_field.setStyleSheet(PARCHMENT_INPUT_QSS)
        self.input_field.returnPressed.connect(self._on_send)
        input_row.addWidget(self.input_field, stretch=1)

        # Rich Terracotta 'Ask' Button
        self.btn_send = GlassButton(text="ASK", icon_text="⚡ ASK", parent=self, is_pill=True, is_accent=True)
        self.btn_send.setFixedWidth(58)
        self.btn_send.setToolTip("Send question to OpenRouter AI")
        self.btn_send.clicked.connect(self._on_send)
        input_row.addWidget(self.btn_send)

        layout.addLayout(input_row)

    def _on_send(self):
        text = self.input_field.text().strip()
        if not text:
            return
        self.lbl_status.setText("Thinking...")
        self.output_card.setText(f"🤔 Thinking: \"{text}\"...")
        self.request_chat_question.emit(text)
        self.input_field.clear()

    def set_reply_text(self, text: str, is_success: bool = True):
        self.lbl_status.setText("Ready" if is_success else "Error")
        self.output_card.setText(text)

    def set_screen_context_active(self, active: bool):
        self.lbl_screen_badge.setVisible(active)

    def _copy_response(self):
        txt = self.output_card.text()
        if txt:
            QGuiApplication.clipboard().setText(txt)
            self.lbl_status.setText("Copied!")
            QTimer.singleShot(1500, lambda: self.lbl_status.setText("Ready"))

    def _clear_conversation(self):
        self.output_card.setText("👋 Ask me any question directly via OpenRouter.")
        self.lbl_status.setText("Ready")


# =========================================================================
# Page 6: Focus & Sprint Pomodoro Studio (Misty Sage Edition)
# =========================================================================

class Page6FocusTimer(QWidget):
    """
    Page 6: Digital countdown timer inside Deep Pine-Slate Plate (#3E4A45)
    with oversized Chalk White digits (25:00), preset pills, and sprint tasks.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.total_seconds = 25 * 60
        self.remaining_seconds = self.total_seconds
        self.is_running = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(14)

        # Left Column: Big Timer Display & Presets
        left_col = QVBoxLayout()
        left_col.setSpacing(4)
        left_col.setAlignment(Qt.AlignCenter)

        # Preset Buttons Row
        preset_row = QHBoxLayout()
        preset_row.setSpacing(4)

        for label, mins in [("25M FOCUS", 25), ("50M DEEP", 50), ("5M BREAK", 5), ("15M REST", 15)]:
            btn = GlassButton(text=label, parent=self, is_pill=True)
            btn.setFixedHeight(22)
            btn.setFont(get_nav_pill_font(size=7.4, weight=QFont.Bold, wide_spacing=False))
            btn.clicked.connect(lambda checked=False, m=mins: self.set_duration(m))
            preset_row.addWidget(btn)

        left_col.addLayout(preset_row)

        # Deep Pine-Slate Plate (#3E4A45) for Digital Countdown
        time_plate = QFrame(self)
        time_plate.setFixedHeight(48)
        time_plate.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_PINE_PLATE};
                border: 1.2px solid {BORDER_MUTED};
                border-radius: 6px;
            }}
        """)
        t_lay = QVBoxLayout(time_plate)
        t_lay.setContentsMargins(0, 0, 0, 0)
        t_lay.setAlignment(Qt.AlignCenter)

        self.lbl_time = QLabel("25:00", time_plate)
        self.lbl_time.setFont(get_display_font(size=24.0, weight=QFont.Black))
        self.lbl_time.setStyleSheet("color: #FFFFFF; border: none; background: transparent;")
        self.lbl_time.setAlignment(Qt.AlignCenter)
        t_lay.addWidget(self.lbl_time)
        left_col.addWidget(time_plate)

        # Timer Controls: Start/Pause, Reset
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(8)
        ctrl_row.setAlignment(Qt.AlignCenter)

        self.btn_toggle = GlassButton(icon_text="▶ START", parent=self, is_pill=True, is_accent=True)
        self.btn_toggle.setFixedSize(72, 26)
        self.btn_toggle.clicked.connect(self._toggle_timer)
        ctrl_row.addWidget(self.btn_toggle)

        self.btn_reset = GlassButton(icon_text="🔄 RESET", parent=self, is_pill=True)
        self.btn_reset.setFixedSize(72, 26)
        self.btn_reset.clicked.connect(self._reset_timer)
        ctrl_row.addWidget(self.btn_reset)

        left_col.addLayout(ctrl_row)
        layout.addLayout(left_col, stretch=1)

        # Right Column: Quick Sprint Checklist
        right_col = QVBoxLayout()
        right_col.setSpacing(4)

        lbl_sprint = QLabel("🎯 Focus Sprint Tasks", self)
        lbl_sprint.setFont(get_display_font(size=9.5, weight=QFont.Black))
        lbl_sprint.setStyleSheet(f"color: {TEXT_CHARCOAL};")
        right_col.addWidget(lbl_sprint)

        # Tasks Container
        self.tasks_widget = QWidget(self)
        self.tasks_layout = QVBoxLayout(self.tasks_widget)
        self.tasks_layout.setContentsMargins(0, 0, 0, 0)
        self.tasks_layout.setSpacing(3)

        tasks_scroll = QScrollArea(self)
        tasks_scroll.setWidget(self.tasks_widget)
        tasks_scroll.setWidgetResizable(True)
        tasks_scroll.setFixedHeight(68)
        tasks_scroll.setStyleSheet(MISTY_SCROLL_QSS)
        right_col.addWidget(tasks_scroll)

        # Add Task Row
        task_in_row = QHBoxLayout()
        task_in_row.setSpacing(4)
        self.input_task = QLineEdit(self)
        self.input_task.setPlaceholderText("Add sprint task...")
        self.input_task.setFont(get_body_font(size=8.5, weight=QFont.Normal))
        self.input_task.setStyleSheet(PARCHMENT_INPUT_QSS)
        self.input_task.returnPressed.connect(self._add_task)
        task_in_row.addWidget(self.input_task, stretch=1)

        btn_add = GlassButton(icon_text="+", parent=self, is_pill=False, size_override=(22, 22), is_accent=True)
        btn_add.clicked.connect(self._add_task)
        task_in_row.addWidget(btn_add)
        right_col.addLayout(task_in_row)

        layout.addLayout(right_col, stretch=1)

        # 1-second countdown timer
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._on_tick)

        # Initial demo tasks
        self._add_task_item("Review active project materials", False)
        self._add_task_item("Complete 25m deep-work sprint", False)

    def set_duration(self, minutes: int):
        self._timer.stop()
        self.is_running = False
        self.btn_toggle.icon_text = "▶ Start"
        self.btn_toggle.update()
        self.total_seconds = minutes * 60
        self.remaining_seconds = self.total_seconds
        self._update_display()

    def _toggle_timer(self):
        if self.is_running:
            self._timer.stop()
            self.is_running = False
            self.btn_toggle.icon_text = "▶ Start"
        else:
            self._timer.start()
            self.is_running = True
            self.btn_toggle.icon_text = "⏸ Pause"
        self.btn_toggle.update()

    def _reset_timer(self):
        self._timer.stop()
        self.is_running = False
        self.btn_toggle.icon_text = "▶ Start"
        self.btn_toggle.update()
        self.remaining_seconds = self.total_seconds
        self._update_display()

    def _on_tick(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self._update_display()
        else:
            self._timer.stop()
            self.is_running = False
            self.btn_toggle.icon_text = "▶ Done"
            self.btn_toggle.update()
            self.lbl_time.setText("00:00")

    def _update_display(self):
        m = self.remaining_seconds // 60
        s = self.remaining_seconds % 60
        self.lbl_time.setText(f"{m:02d}:{s:02d}")

    def _add_task(self):
        txt = self.input_task.text().strip()
        if txt:
            self._add_task_item(txt, False)
            self.input_task.clear()

    def _add_task_item(self, text: str, checked: bool = False):
        item_w = QWidget(self.tasks_widget)
        item_w.setFixedHeight(22)
        i_lay = QHBoxLayout(item_w)
        i_lay.setContentsMargins(2, 0, 2, 0)
        i_lay.setSpacing(4)

        btn_chk = GlassButton(icon_text="✓" if checked else "○", parent=item_w, is_pill=False, size_override=(18, 18))
        btn_chk.setFont(get_retro_swiss_font(size=7.5, weight=QFont.Bold))

        lbl = QLabel(text, item_w)
        lbl.setFont(get_retro_swiss_font(size=8.5, weight=QFont.Medium, italic=checked))
        lbl.setStyleSheet(f"color: {'#8A8D94' if checked else INK_BLACK};")

        def toggle_check():
            is_c = (btn_chk.icon_text == "✓")
            btn_chk.icon_text = "○" if is_c else "✓"
            btn_chk.update()
            lbl.setStyleSheet(f"color: {'#0F1115' if is_c else '#8A8D94'};")

        btn_chk.clicked.connect(toggle_check)
        i_lay.addWidget(btn_chk)
        i_lay.addWidget(lbl, stretch=1)

        btn_del = GlassButton(icon_text="×", parent=item_w, is_pill=False, size_override=(16, 16))
        btn_del.clicked.connect(lambda: item_w.deleteLater())
        i_lay.addWidget(btn_del)

        self.tasks_layout.addWidget(item_w)


# =========================================================================
# Page 7: Developer & Student Transform Studio (Misty Sage Edition)
# =========================================================================

class Page7DevTools(QWidget):
    """
    Page 7: Instant developer & student utility toolbox:
    - 🧮 Math / Python Expression Evaluator
    - ⚙️ JSON Beautifier & Minifier
    - 🔐 Base64 Encoder/Decoder & SHA-256 Hash generator
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mode = "math"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(5)

        # Header with Mode Pills
        top_row = QHBoxLayout()
        top_row.setSpacing(6)

        lbl_head = QLabel("🛠️ Dev & Math Studio", self)
        lbl_head.setFont(get_display_font(size=10.5, weight=QFont.Black))
        lbl_head.setStyleSheet(f"color: {TEXT_CHARCOAL};")
        top_row.addWidget(lbl_head)
        top_row.addStretch(1)

        self.mode_buttons = {}
        for m_key, m_lbl in [("math", "🧮 MATH"), ("json", "⚙️ JSON"), ("b64", "🔐 B64/HASH")]:
            btn = GlassButton(text=m_lbl, parent=self, is_pill=True)
            btn.setFixedHeight(22)
            btn.setFont(get_nav_pill_font(size=7.4, weight=QFont.Bold, wide_spacing=False))
            btn.clicked.connect(lambda checked=False, k=m_key: self.set_mode(k))
            top_row.addWidget(btn)
            self.mode_buttons[m_key] = btn

        layout.addLayout(top_row)
        self._update_mode_buttons()

        # Input Row
        in_row = QHBoxLayout()
        in_row.setSpacing(6)

        self.input_code = QLineEdit(self)
        self.input_code.setPlaceholderText("Enter math expression (e.g. 2**16, math.sqrt(256), hex(1024))...")
        self.input_code.setFont(get_body_font(size=9.2, weight=QFont.Normal, mono=True))
        self.input_code.setStyleSheet(PARCHMENT_INPUT_QSS)
        self.input_code.returnPressed.connect(self._run_tool)
        in_row.addWidget(self.input_code, stretch=1)

        self.btn_run = GlassButton(text="RUN", icon_text="⚡ RUN", parent=self, is_pill=True, is_accent=True)
        self.btn_run.setFixedWidth(58)
        self.btn_run.clicked.connect(self._run_tool)
        in_row.addWidget(self.btn_run)

        layout.addLayout(in_row)

        # Recessed Monospace Result Display Row
        out_row = QHBoxLayout()
        out_row.setSpacing(6)

        self.output_result = QLineEdit(self)
        self.output_result.setReadOnly(True)
        self.output_result.setFont(get_body_font(size=9.2, weight=QFont.Bold, mono=True))
        self.output_result.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_PARCHMENT_LIGHT};
                border: 1.2px solid {BORDER_MUTED};
                border-radius: 5px;
                color: {ACCENT_TERRACOTTA};
                padding: 4px 8px;
            }}
        """)
        self.output_result.setText("Result will appear here...")
        out_row.addWidget(self.output_result, stretch=1)

        self.btn_copy_res = GlassButton(icon_text="📋", parent=self, is_pill=False, size_override=(26, 26))
        self.btn_copy_res.setToolTip("Copy result to clipboard")
        self.btn_copy_res.clicked.connect(lambda: QGuiApplication.clipboard().setText(self.output_result.text()))
        out_row.addWidget(self.btn_copy_res)

        layout.addLayout(out_row)

    def set_mode(self, mode: str):
        self.current_mode = mode
        self._update_mode_buttons()
        if mode == "math":
            self.input_code.setPlaceholderText("Enter math (e.g. 2**16, math.sqrt(144)*10, hex(255))...")
        elif mode == "json":
            self.input_code.setPlaceholderText('Paste JSON string to format (e.g. {"name":"DynamicIsland","active":true})...')
        else:
            self.input_code.setPlaceholderText("Enter text to encode Base64 & generate SHA-256 hash...")

    def _update_mode_buttons(self):
        for k, btn in self.mode_buttons.items():
            btn.set_toggled_active(k == self.current_mode)

    def _run_tool(self):
        import base64
        import hashlib
        import json

        txt = self.input_code.text().strip()
        if not txt:
            return

        try:
            if self.current_mode == "math":
                safe_dict = {
                    "math": math,
                    "abs": abs,
                    "round": round,
                    "min": min,
                    "max": max,
                    "sum": sum,
                    "pow": pow,
                    "hex": hex,
                    "bin": bin,
                    "oct": oct,
                    "int": int,
                    "float": float,
                    "pi": math.pi,
                    "e": math.e,
                }
                res = eval(txt, {"__builtins__": {}}, safe_dict)
                self.output_result.setText(str(res))

            elif self.current_mode == "json":
                parsed = json.loads(txt)
                self.output_result.setText(json.dumps(parsed, separators=(',', ':')))

            elif self.current_mode == "b64":
                raw_bytes = txt.encode("utf-8")
                b64_str = base64.b64encode(raw_bytes).decode("utf-8")
                sha256_str = hashlib.sha256(raw_bytes).hexdigest()[:16]
                self.output_result.setText(f"B64: {b64_str} • SHA: {sha256_str}...")

        except Exception as e:
            self.output_result.setText(f"Error: {str(e)}")


# =========================================================================
# Page 8: Persistent Scratchpad & Notes (Misty Sage Edition)
# =========================================================================

class Page8Scratchpad(QWidget):
    """
    Page 8: Archival Warm Parchment editor with live word & character counters,
    timestamp insertion, and auto-save.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.notes_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "scratchpad_notes.txt"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(5)

        # Header Row
        top_row = QHBoxLayout()
        top_row.setSpacing(6)

        lbl_head = QLabel("📝 Clip Notes & Scratchpad", self)
        lbl_head.setFont(get_display_font(size=10.5, weight=QFont.Black))
        lbl_head.setStyleSheet(f"color: {TEXT_CHARCOAL};")
        top_row.addWidget(lbl_head)
        top_row.addStretch(1)

        self.lbl_counter = QLabel("0 words • 0 chars", self)
        self.lbl_counter.setFont(get_body_font(size=8.2, weight=QFont.Medium))
        self.lbl_counter.setStyleSheet(f"color: {TEXT_MUTED};")
        top_row.addWidget(self.lbl_counter)

        # Actions
        btn_time = GlassButton(icon_text="🕒", parent=self, is_pill=False, size_override=(24, 22))
        btn_time.setToolTip("Insert current timestamp")
        btn_time.clicked.connect(self._insert_timestamp)
        top_row.addWidget(btn_time)

        btn_copy = GlassButton(icon_text="📋", parent=self, is_pill=False, size_override=(24, 22))
        btn_copy.setToolTip("Copy all notes")
        btn_copy.clicked.connect(self._copy_all)
        top_row.addWidget(btn_copy)

        btn_clr = GlassButton(icon_text="🧹", parent=self, is_pill=False, size_override=(24, 22))
        btn_clr.setToolTip("Clear scratchpad")
        btn_clr.clicked.connect(self._clear_notes)
        top_row.addWidget(btn_clr)

        layout.addLayout(top_row)

        # Archival Text Editor
        self.editor = QTextEdit(self)
        self.editor.setFont(get_body_font(size=9.2, weight=QFont.Normal, mono=True))
        self.editor.setStyleSheet(PARCHMENT_TEXTEDIT_QSS)
        self.editor.setPlaceholderText("Type quick lecture takeaways, meeting notes, or paste code snippets...")
        self.editor.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.editor)

        # Load saved notes if available
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
                    content = f.read()
                    self.editor.setPlainText(content)
            except Exception:
                pass

    def _insert_timestamp(self):
        ts = time.strftime("[%I:%M %p] ")
        self.editor.insertPlainText(ts)

    def _copy_all(self):
        text = self.editor.toPlainText()
        if text:
            QGuiApplication.clipboard().setText(text)
            self.lbl_counter.setText("Copied!")
            QTimer.singleShot(1500, self._on_text_changed)

    def _clear_notes(self):
        self.editor.clear()


# =========================================================================
# Page 9: Neural Workspace Expansion ("Extend" Mode - Misty Sage Edition)
# =========================================================================

class Page9NeuralWorkspace(QWidget):
    """
    Page 9: Neural Workspace Extension ("Extend" Mode) Hub.
    Features:
    - Prominent central '⚡ EXTEND WORKSPACE' CTA.
    - Dynamic Extension Tabs Row (expandable from 3 up to 6 tabs).
    - Tactile [+] button next to EVERY single extension tab to expand tabs.
    - Custom App Nodes (APP 4, APP 5, APP 6) with drag & drop and app hosting.
    """
    request_extend = Signal()
    request_add_tab = Signal(int)
    request_remove_tab = Signal(int)
    request_open_tab = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._plus_buttons = []
        self.tabs_data = [
            {"index": 0, "code": "NP", "name": "Quick Notepad", "accent": ACCENT_AMBER, "can_remove": False},
            {"index": 1, "code": "AI", "name": "Neural Studio", "accent": ACCENT_TERRACOTTA, "can_remove": False},
            {"index": 2, "code": "DASH", "name": "Live Telemetry", "accent": ACCENT_SAGE, "can_remove": False},
        ]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(5)

        # Header Row
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        lbl_head = QLabel("🌐  EXTENSION WORKSPACE", self)
        lbl_head.setFont(get_display_font(size=10.5, weight=QFont.Black))
        lbl_head.setStyleSheet(f"color: {TEXT_CHARCOAL};")
        top_row.addWidget(lbl_head)
        top_row.addStretch(1)

        badge_extend = QLabel("Extend Mode", self)
        badge_extend.setFont(get_nav_pill_font(size=7.5, weight=QFont.Bold, wide_spacing=False))
        badge_extend.setStyleSheet(f"""
            QLabel {{
                background-color: {BG_PARCHMENT};
                border: 1.2px solid {BORDER_MUTED};
                border-radius: 4px;
                color: {TEXT_CHARCOAL};
                padding: 2px 8px;
            }}
        """)
        top_row.addWidget(badge_extend)
        layout.addLayout(top_row)

        self.lbl_sub = QLabel("Active: 3/6 extension tabs (NP, AI, DASH) ready to extend", self)
        self.lbl_sub.setFont(get_body_font(size=8.2, weight=QFont.Medium))
        self.lbl_sub.setStyleSheet(f"color: {TEXT_MUTED};")
        layout.addWidget(self.lbl_sub)

        layout.addSpacing(1)

        # Central Extend Button (Prominent Terracotta Rust CTA)
        center_row = QHBoxLayout()
        center_row.addStretch(1)

        self.btn_extend = QPushButton("⚡  EXTEND WORKSPACE", self)
        self.btn_extend.setFixedHeight(36)
        self.btn_extend.setFixedWidth(260)
        self.btn_extend.setCursor(Qt.PointingHandCursor)
        self.btn_extend.setFont(get_display_font(size=10.5, weight=QFont.Black))
        self.btn_extend.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_TERRACOTTA};
                color: #FFFFFF;
                border: 1.5px solid {ACCENT_MAHOGANY};
                border-radius: 6px;
                padding: 4px 16px;
                letter-spacing: 1.5px;
            }}
            QPushButton:hover {{
                background-color: {ACCENT_SIENNA};
                border-color: {ACCENT_TERRACOTTA};
            }}
            QPushButton:pressed {{
                background-color: {ACCENT_PRESSED};
                padding-top: 6px;
                padding-left: 18px;
            }}
        """)
        self.btn_extend.clicked.connect(self.request_extend.emit)
        center_row.addWidget(self.btn_extend)
        center_row.addStretch(1)
        layout.addLayout(center_row)

        layout.addSpacing(1)

        # Dynamic Extension Tabs Scroll Area (Supports 3 to 6 tabs with [+] next to each)
        self.scroll_tabs = QScrollArea(self)
        self.scroll_tabs.setFixedHeight(34)
        self.scroll_tabs.setWidgetResizable(True)
        self.scroll_tabs.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_tabs.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_tabs.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.tabs_container = QWidget(self.scroll_tabs)
        self.tabs_layout = QHBoxLayout(self.tabs_container)
        self.tabs_layout.setContentsMargins(2, 1, 2, 1)
        self.tabs_layout.setSpacing(5)
        self.scroll_tabs.setWidget(self.tabs_container)

        layout.addWidget(self.scroll_tabs)

        # Populate initial tabs
        self.set_tabs_data(self.tabs_data)

    def set_tabs_data(self, tabs_list: list):
        self.tabs_data = tabs_list
        self._plus_buttons = []

        # Update subtitle
        codes = [t.get("code", "") for t in tabs_list]
        self.lbl_sub.setText(f"Active: {len(tabs_list)}/6 extension tabs ({', '.join(codes)}) ready to extend")

        # Clear existing tabs in layout
        while self.tabs_layout.count():
            item = self.tabs_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        can_add = len(tabs_list) < 6

        # Build each tab pill with a [+] button immediately next to it
        for idx, tab_info in enumerate(tabs_list):
            code = tab_info.get("code", f"T{idx+1}")
            name = tab_info.get("name", "Tab")
            accent = tab_info.get("accent", ACCENT_TERRACOTTA)
            can_rm = tab_info.get("can_remove", False)

            pill = QFrame(self.tabs_container)
            pill.setFixedHeight(26)
            pill.setCursor(Qt.PointingHandCursor)
            pill.setStyleSheet(f"""
                QFrame {{
                    background-color: {BG_PARCHMENT};
                    border: 1.2px solid {BORDER_MUTED};
                    border-radius: 4px;
                }}
                QFrame:hover {{
                    border-color: {ACCENT_TERRACOTTA};
                }}
            """)

            p_lay = QHBoxLayout(pill)
            p_lay.setContentsMargins(5, 1, 6, 1)
            p_lay.setSpacing(4)

            lbl_code = QLabel(code, pill)
            lbl_code.setFont(get_nav_pill_font(size=7.0, weight=QFont.Bold, wide_spacing=False))
            lbl_code.setStyleSheet(f"""
                QLabel {{
                    background-color: {accent};
                    color: #FFFFFF;
                    border: 1px solid {BORDER_MUTED};
                    border-radius: 3px;
                    padding: 1px 4px;
                }}
            """)
            p_lay.addWidget(lbl_code)

            lbl_name = QLabel(name, pill)
            lbl_name.setFont(get_body_font(size=7.8, weight=QFont.Bold))
            lbl_name.setStyleSheet(f"color: {TEXT_CHARCOAL}; border: none; background: transparent;")
            p_lay.addWidget(lbl_name)

            if can_rm:
                btn_rm = QPushButton("×", pill)
                btn_rm.setFixedSize(14, 14)
                btn_rm.setCursor(Qt.PointingHandCursor)
                btn_rm.setFont(get_display_font(size=8.5, weight=QFont.Black))
                btn_rm.setToolTip("Remove this extension tab")
                btn_rm.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {TEXT_MUTED};
                        border: none;
                        padding: 0;
                    }}
                    QPushButton:hover {{
                        color: {ACCENT_TERRACOTTA};
                        font-weight: 800;
                    }}
                """)
                btn_rm.clicked.connect(lambda _, i=idx: self.request_remove_tab.emit(i))
                p_lay.addWidget(btn_rm)

            def make_click(i=idx):
                return lambda event: self.request_open_tab.emit(i)
            pill.mouseReleaseEvent = make_click(idx)

            self.tabs_layout.addWidget(pill)

            # PLUS button (+) placed right next to EVERY single extension tab
            btn_plus = QPushButton("+", self.tabs_container)
            btn_plus.setFixedSize(20, 24)
            btn_plus.setFont(get_display_font(size=11.0, weight=QFont.Black))
            self._plus_buttons.append(btn_plus)

            if can_add:
                btn_plus.setCursor(Qt.PointingHandCursor)
                btn_plus.setToolTip(f"Add new extension tab (currently {len(tabs_list)}/6)")
                btn_plus.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {BG_PARCHMENT};
                        color: {TEXT_CHARCOAL};
                        border: 1.2px solid {BORDER_MUTED};
                        border-radius: 4px;
                        font-weight: 800;
                    }}
                    QPushButton:hover {{
                        background-color: #FAF8F2;
                        border-color: {ACCENT_TERRACOTTA};
                        color: {ACCENT_TERRACOTTA};
                    }}
                    QPushButton:pressed {{
                        background-color: {ACCENT_PRESSED};
                        color: #FFFFFF;
                    }}
                """)
                btn_plus.clicked.connect(lambda _, i=idx: self.request_add_tab.emit(i))
            else:
                btn_plus.setEnabled(False)
                btn_plus.setToolTip("Maximum of 6 extension tabs reached")
                btn_plus.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #D6CEB8;
                        color: {TEXT_MUTED};
                        border: 1px solid {BORDER_MUTED};
                        border-radius: 4px;
                    }}
                """)

            self.tabs_layout.addWidget(btn_plus)

        self.tabs_layout.addStretch(1)
