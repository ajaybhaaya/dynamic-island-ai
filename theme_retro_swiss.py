"""
theme_retro_swiss.py - Retro-Swiss Italic Bold Unified Design System
Windows 11 Dynamic Island Desktop Companion + Neural Workspace Expansion

Merges the Retro 90s Pixel OS tactile bevel aesthetic with Swiss Art Style
(International Typographic Style) and Heavy Italic Bold Editorial Typography.
"""

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (
    QFont,
    QColor,
    QBrush,
    QPen,
    QPainter,
    QPainterPath,
    QLinearGradient,
)

# =========================================================================
# 1. Color Palette Tokens (Strict Swiss-Retro Palette)
# =========================================================================

# Surfaces
BG_CANVAS = "#F4F1EA"       # Warm Swiss Archival Off-White (Primary Window Surface)
BG_BEIGE = "#E6E1D6"        # Classic Retro Slate-Beige (Secondary / Shelf / Controls)
BG_WELL = "#EAE5DA"         # Recessed Retro Drop-Well / Panel Surface
BG_CARD = "#FAF8F5"         # Clean Archival Off-White Card Fill
BG_WHITE = "#FFFFFF"        # Crisp Pure White (Inputs & Highlight Cards)
BOT_BG = "#050507"          # 100% Pitch-Black for AI Bot Avatar pod

# Inks & Borders
INK_BLACK = "#0F1115"       # Deep Jet Black (Primary structural gridlines & text)
INK_DARK = "#1E2229"        # Dark structural ink
INK_MUTED = "#5A5D64"       # Editorial muted secondary text
INK_FAINT = "#8A8D94"       # Micro-metadata / placeholders
BORDER_STRUCT = "#0F1115"   # 1.5px - 2px Hard structural gridline

# Retro Bevel Shading
BEVEL_LIGHT = "#FFFFFF"     # 1px Retro inner bevel top-left highlight
BEVEL_DARK = "#A39E93"      # 1px Retro inner bevel bottom-right shadow
BEVEL_DEPRESSED = "#C4BEB2" # Pressed well shade

# Swiss Signature & Technical Accents
ACCENT_RED = "#E63946"      # Swiss Vermilion / Signal Red (Primary CTA, active states, alerts)
ACCENT_RED_HOVER = "#D62839"
ACCENT_RED_PRESSED = "#BA1826"
ACCENT_BLUE = "#1D4ED8"     # Cobalt Pixel Blue (Technical gauges & badges)
ACCENT_GREEN = "#15803D"    # Emerald Terminal Green (Status & operational badges)
ACCENT_AMBER = "#D97706"    # Warm Amber for caution/medium latency

# QColor equivalents for QPainter operations
COLOR_BG_CANVAS = QColor(BG_CANVAS)
COLOR_BG_BEIGE = QColor(BG_BEIGE)
COLOR_BG_WELL = QColor(BG_WELL)
COLOR_BG_CARD = QColor(BG_CARD)
COLOR_BG_WHITE = QColor(BG_WHITE)
COLOR_BOT_BG = QColor(BOT_BG)
COLOR_INK_BLACK = QColor(INK_BLACK)
COLOR_INK_MUTED = QColor(INK_MUTED)
COLOR_ACCENT_RED = QColor(ACCENT_RED)
COLOR_ACCENT_BLUE = QColor(ACCENT_BLUE)
COLOR_ACCENT_GREEN = QColor(ACCENT_GREEN)
COLOR_BEVEL_LIGHT = QColor(BEVEL_LIGHT)
COLOR_BEVEL_DARK = QColor(BEVEL_DARK)


# =========================================================================
# 2. Typography System (Italic Bold Swiss Editorial)
# =========================================================================

def get_retro_swiss_font(
    size: float = 10.0,
    weight: QFont.Weight = QFont.Bold,
    italic: bool = True,
    mono: bool = False
) -> QFont:
    """
    Returns an Italic Bold Swiss editorial font or monospace terminal font:
    - Primary: Segoe UI Variable Display / Arial Black / Helvetica Neue
    - Monospace: Consolas / JetBrains Mono
    """
    if mono:
        font = QFont("Consolas")
        font.setStyleHint(QFont.Monospace)
    else:
        font = QFont("Segoe UI Variable Display")
        font.setStyleHint(QFont.SansSerif)

    font.setPointSizeF(size)
    font.setWeight(weight)
    font.setItalic(italic)
    font.setLetterSpacing(QFont.AbsoluteSpacing, -0.35)
    return font

# Drop-in compatible alias for existing files
get_editorial_font = get_retro_swiss_font


# =========================================================================
# 3. Reusable QSS Stylesheets
# =========================================================================

# Primary CTA Button (Vermilion Red #E63946 with Jet Black border & bevel)
SWISS_BTN_RED_QSS = f"""
QPushButton {{
    background-color: {ACCENT_RED};
    color: #FFFFFF;
    border: 1.8px solid {INK_BLACK};
    border-radius: 4px;
    padding: 3px 12px;
    font-weight: 800;
    font-style: italic;
}}
QPushButton:hover {{
    background-color: {ACCENT_RED_HOVER};
}}
QPushButton:pressed {{
    background-color: {ACCENT_RED_PRESSED};
    padding-top: 4px;
    padding-left: 13px;
}}
QPushButton:disabled {{
    background-color: #D1A3A7;
    color: #F4F1EA;
    border-color: #8A8D94;
}}
"""

# Retro Slate-Beige Tactile Button (#E6E1D6 with classic 90s bevel edges)
SWISS_BTN_BEIGE_QSS = f"""
QPushButton {{
    background-color: {BG_BEIGE};
    color: {INK_BLACK};
    border-top: 1.5px solid {BEVEL_LIGHT};
    border-left: 1.5px solid {BEVEL_LIGHT};
    border-right: 1.8px solid {INK_BLACK};
    border-bottom: 1.8px solid {INK_BLACK};
    border-radius: 3px;
    padding: 3px 8px;
    font-weight: 800;
    font-style: italic;
}}
QPushButton:hover {{
    background-color: {BG_CANVAS};
}}
QPushButton:pressed {{
    background-color: {BEVEL_DEPRESSED};
    border-top: 1.8px solid {INK_BLACK};
    border-left: 1.8px solid {INK_BLACK};
    border-right: 1.5px solid {BEVEL_LIGHT};
    border-bottom: 1.5px solid {BEVEL_LIGHT};
    padding-top: 4px;
    padding-left: 9px;
}}
"""

# Crisp Archival Input Fields (#FFFFFF fill with 1.5px #0F1115 border)
SWISS_INPUT_QSS = f"""
QLineEdit {{
    background-color: {BG_WHITE};
    color: {INK_BLACK};
    border: 1.5px solid {INK_BLACK};
    border-radius: 4px;
    padding: 4px 8px;
    selection-background-color: {ACCENT_RED};
    selection-color: #FFFFFF;
}}
QLineEdit:focus {{
    border: 2px solid {ACCENT_RED};
    background-color: #FFFFFF;
}}
"""

# Crisp Archival Multi-line Editor / TextEdit
SWISS_TEXTEDIT_QSS = f"""
QTextEdit, QPlainTextEdit {{
    background-color: {BG_CARD};
    color: {INK_BLACK};
    border: 1.5px solid {INK_BLACK};
    border-radius: 4px;
    padding: 6px;
    selection-background-color: {ACCENT_RED};
    selection-color: #FFFFFF;
}}
QTextEdit:focus, QPlainTextEdit:focus {{
    border: 2px solid {ACCENT_RED};
}}
"""

# Clean Minimalist Retro Scrollbar
SWISS_SCROLL_QSS = f"""
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollBar:vertical {{
    border: 1px solid {INK_BLACK};
    background: {BG_BEIGE};
    width: 8px;
    margin: 0px;
    border-radius: 0px;
}}
QScrollBar::handle:vertical {{
    background: {INK_BLACK};
    min-height: 16px;
}}
QScrollBar::handle:vertical:hover {{
    background: {ACCENT_RED};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    height: 0px;
}}
"""

# High-contrast Retro-Swiss Menu
SWISS_MENU_QSS = f"""
QMenu {{
    background-color: {BG_CANVAS};
    color: {INK_BLACK};
    border: 2px solid {INK_BLACK};
    border-radius: 0px;
    padding: 4px;
    font-weight: 700;
    font-style: italic;
}}
QMenu::item {{
    padding: 6px 20px;
    background-color: transparent;
    color: {INK_BLACK};
    border-radius: 2px;
}}
QMenu::item:selected {{
    background-color: {ACCENT_RED};
    color: #FFFFFF;
}}
QMenu::separator {{
    height: 1.5px;
    background: {INK_BLACK};
    margin: 4px 6px;
}}
"""


# =========================================================================
# 4. QPainter Retro Bevel & Grid Drawing Helpers
# =========================================================================

def draw_retro_bevel(painter: QPainter, rect: QRectF, raised: bool = True, line_w: float = 1.0):
    """Draws classic 90s dual-tone bevel highlight & shadow edges."""
    painter.save()
    top_left_col = COLOR_BEVEL_LIGHT if raised else COLOR_INK_BLACK
    bot_right_col = COLOR_INK_BLACK if raised else COLOR_BEVEL_LIGHT

    pen_tl = QPen(top_left_col, line_w)
    painter.setPen(pen_tl)
    # Top edge
    painter.drawLine(int(rect.left()), int(rect.top()), int(rect.right()), int(rect.top()))
    # Left edge
    painter.drawLine(int(rect.left()), int(rect.top()), int(rect.left()), int(rect.bottom()))

    pen_br = QPen(bot_right_col, line_w)
    painter.setPen(pen_br)
    # Bottom edge
    painter.drawLine(int(rect.left()), int(rect.bottom()), int(rect.right()), int(rect.bottom()))
    # Right edge
    painter.drawLine(int(rect.right()), int(rect.top()), int(rect.right()), int(rect.bottom()))
    painter.restore()


def draw_swiss_capsule(painter: QPainter, rect: QRectF, r: float):
    """
    Renders the main Dynamic Island capsule in the Retro-Swiss aesthetic:
    - Base fill: Warm Swiss Archival Off-White (#F4F1EA)
    - Border: Hard Jet Black (#0F1115), 2.0px stroke
    - Inner 1px bevel highlight on top-left, shadow on bottom-right
    """
    painter.save()
    painter.setRenderHint(QPainter.Antialiasing, True)

    # 1. Base Fill
    painter.setBrush(QBrush(COLOR_BG_CANVAS))
    # 2. Structural Jet Black 2px Border
    painter.setPen(QPen(COLOR_INK_BLACK, 2.0))
    painter.drawRoundedRect(rect, r, r)

    # 3. Inner 1px Retro Bevel Accent Line
    inner_rect = rect.adjusted(1.5, 1.5, -1.5, -1.5)
    inner_r = max(2.0, r - 1.5)

    # Top highlight line
    high_pen = QPen(QColor(255, 255, 255, 180), 1.0)
    painter.setPen(high_pen)
    painter.setBrush(Qt.NoBrush)
    painter.drawRoundedRect(inner_rect, inner_r, inner_r)

    painter.restore()
