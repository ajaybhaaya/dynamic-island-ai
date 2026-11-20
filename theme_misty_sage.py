"""
theme_misty_sage.py - "Misty Sage & Terracotta Illustrated Editorial" Theme
Windows 11 Dynamic Island Desktop Companion + Neural Workspace Expansion

Strictly extracted from the reference artwork:
- Atmospheric Gradient: Muted Sage-Teal Mist (#9CAFAA) -> Soft Fog Cream-Green (#CBD2C4) -> Warm Dry-Grass Sand (#D6CEB8)
- Recessed Wells / Inner Cards: Deep Forest Pine Slate (#5E6F68, rgba(94,111,104,0.22)) & Warm Parchment (#EAE6DA)
- Primary CTA Accent: Rich Terracotta Rust (#B83B24) -> Warm Burnt Sienna (#D15238)
- Micro-Accents: Warm Amber-Peach (#E88D5A), Mahogany Bark (#6E2214), Forest Sage (#4A6B5D)
- Mandatory: AI Bot Avatar container stays 100% Pitch-Black (#050507)
- Typography: Heavy Display Headers (#FFFFFF bold), Wide-Tracked Nav Pills (letter-spacing: 1.8px),
  Clean Charcoal-Pine body text (#2B3531).
- 60 FPS Anti-Choppy Rendering: Anti-aliasing, TextAntiAliasing, SmoothPixmapTransform globally.
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
# 1. Color Palette Tokens (Reference Extracted)
# =========================================================================

# Atmospheric Horizon Stops
GRAD_TOP = "#9CAFAA"          # Muted Sage-Teal Mist (0.0)
GRAD_MID = "#CBD2C4"          # Soft Desaturated Fog Cream-Green (0.55)
GRAD_BOT = "#D6CEB8"          # Warm Dry-Grass Sand (1.0)

# Surfaces & Recessed Wells
BG_PARCHMENT = "#EAE6DA"      # Warm Parchment (Inputs, Cards, Inner Plates)
BG_PARCHMENT_LIGHT = "#FAF8F2"# Clean Parchment for Scratchpad Editor
BG_PINE_SLATE = "#5E6F68"     # Deep Forest Pine Slate (Controls, Secondary Fills)
BG_PINE_PLATE = "#3E4A45"     # Deep Pine-Slate Plate for Countdown Timer & Headers
BG_WELL_PINE = "rgba(94, 111, 104, 0.22)" # Drop-zone well
BG_WHITE = "#FFFFFF"          # Pure Chalk White (Pills, Badges, Highlights)
BOT_BG = "#050507"            # 100% Pitch-Black for AI Bot Avatar Pod (MANDATORY)

# Structural Borders
BORDER_MUTED = "#7A8B84"      # Subtle 1.2px borders
BORDER_DARK = "#3E4A45"       # Stronger 1.5px - 2px structural edge
BORDER_CHIP = "rgba(122, 139, 132, 0.45)"
BORDER_CAPSULE = "#6B7C75"    # Clean 1.5px capsule perimeter

# Terracotta & Sienna Brand Accents
ACCENT_TERRACOTTA = "#B83B24" # Rich Terracotta Rust (Primary CTAs, Active States)
ACCENT_SIENNA = "#D15238"     # Warm Burnt Sienna (Hover State)
ACCENT_PRESSED = "#962D1A"    # Deep Terracotta (Pressed State)
ACCENT_AMBER = "#E88D5A"      # Warm Amber-Peach (Secondary Telemetry, Highlights)
ACCENT_MAHOGANY = "#6E2214"   # Mahogany Bark (Tether Anchors, Critical Borders)
ACCENT_SAGE = "#4A6B5D"       # Forest Sage (Cache Telemetry, Operational Badges)

# Text & Inks
TEXT_WHITE = "#FFFFFF"        # Pure Chalk White for Display Headers & Heavy Readouts
TEXT_CHARCOAL = "#2B3531"     # Deep Charcoal-Pine for Body, Labels & Subtitles on Light Fills
TEXT_LIGHT = "#F8FAFC"        # Light Text on Dark / Terracotta Fills
TEXT_MUTED = "#5E6F68"        # Editorial Muted Subtext
TEXT_FAINT = "#7A8B84"        # Micro Metadata & Placeholders
TETHER_BLACK = "#141816"      # Deep Charcoal/Black for Static Neural Tethers (2.2px)

# QColor equivalents for QPainter operations
COLOR_GRAD_TOP = QColor(GRAD_TOP)
COLOR_GRAD_MID = QColor(GRAD_MID)
COLOR_GRAD_BOT = QColor(GRAD_BOT)
COLOR_PARCHMENT = QColor(BG_PARCHMENT)
COLOR_PARCHMENT_LIGHT = QColor(BG_PARCHMENT_LIGHT)
COLOR_PINE_SLATE = QColor(BG_PINE_SLATE)
COLOR_PINE_PLATE = QColor(BG_PINE_PLATE)
COLOR_WHITE = QColor(BG_WHITE)
COLOR_BOT_BG = QColor(BOT_BG)
COLOR_BORDER_MUTED = QColor(BORDER_MUTED)
COLOR_BORDER_CAPSULE = QColor(BORDER_CAPSULE)
COLOR_TERRACOTTA = QColor(ACCENT_TERRACOTTA)
COLOR_SIENNA = QColor(ACCENT_SIENNA)
COLOR_AMBER = QColor(ACCENT_AMBER)
COLOR_MAHOGANY = QColor(ACCENT_MAHOGANY)
COLOR_SAGE = QColor(ACCENT_SAGE)
COLOR_TEXT_CHARCOAL = QColor(TEXT_CHARCOAL)
COLOR_TEXT_WHITE = QColor(TEXT_WHITE)
COLOR_TETHER_BLACK = QColor(TETHER_BLACK)


# =========================================================================
# 2. Typography Hierarchy (Organic Display, Nav Pill & Clean Sans)
# =========================================================================

def get_display_font(
    size: float = 14.0,
    weight: QFont.Weight = QFont.Black,
    italic: bool = False
) -> QFont:
    """
    Bold, organic heavy display style inspired by the 'stand out' brush lettering.
    Used for 25:00 countdown, big telemetry numerals, and floating window titles.
    """
    font = QFont("Segoe UI Variable Display")
    font.setStyleHint(QFont.SansSerif)
    font.setPointSizeF(size)
    font.setWeight(weight)
    font.setItalic(italic)
    font.setLetterSpacing(QFont.AbsoluteSpacing, -0.4)
    return font


def get_nav_pill_font(
    size: float = 10.0,
    weight: QFont.Weight = QFont.Bold,
    wide_spacing: bool = True
) -> QFont:
    """
    Inspired by the 'HOME | ABOUT | WORK' navigation pill bar:
    Uppercase, wide letter-spacing (1.8px), crisp and legible.
    """
    font = QFont("Segoe UI Variable Text")
    font.setStyleHint(QFont.SansSerif)
    font.setPointSizeF(size)
    font.setWeight(weight)
    if wide_spacing:
        font.setLetterSpacing(QFont.AbsoluteSpacing, 1.6)
    return font


def get_body_font(
    size: float = 10.0,
    weight: QFont.Weight = QFont.Medium,
    italic: bool = False,
    mono: bool = False
) -> QFont:
    """
    Clean geometric sans-serif (Segoe UI / Inter) matching the 'in a sea of ordinary...' subtext.
    """
    if mono:
        font = QFont("Consolas")
        font.setStyleHint(QFont.Monospace)
    else:
        font = QFont("Segoe UI Variable Text")
        font.setStyleHint(QFont.SansSerif)

    font.setPointSizeF(size)
    font.setWeight(weight)
    font.setItalic(italic)
    return font

# Drop-in compatibility aliases
get_editorial_font = get_body_font
get_retro_swiss_font = get_body_font


# =========================================================================
# 3. Reusable QSS Stylesheets
# =========================================================================

# Primary CTA Button: Rich Terracotta Rust (#B83B24) with uppercase wide-tracked text
TERRACOTTA_BTN_QSS = f"""
QPushButton {{
    background-color: {ACCENT_TERRACOTTA};
    color: #FFFFFF;
    border: 1.2px solid {ACCENT_MAHOGANY};
    border-radius: 6px;
    padding: 3px 12px;
    font-weight: 700;
    letter-spacing: 1.2px;
}}
QPushButton:hover {{
    background-color: {ACCENT_SIENNA};
    border-color: {ACCENT_TERRACOTTA};
}}
QPushButton:pressed {{
    background-color: {ACCENT_PRESSED};
    padding-top: 4px;
    padding-left: 13px;
}}
QPushButton:disabled {{
    background-color: #A38B84;
    color: #EAE6DA;
    border-color: #7A8B84;
}}
"""

# Navigation / Secondary Tactile Button: Warm Parchment or Pine Slate
PINE_PILL_BTN_QSS = f"""
QPushButton {{
    background-color: {BG_PARCHMENT};
    color: {TEXT_CHARCOAL};
    border: 1.2px solid {BORDER_MUTED};
    border-radius: 6px;
    padding: 3px 10px;
    font-weight: 700;
    letter-spacing: 1.0px;
}}
QPushButton:hover {{
    background-color: #F4F1EA;
    border-color: {ACCENT_TERRACOTTA};
    color: {ACCENT_TERRACOTTA};
}}
QPushButton:pressed {{
    background-color: #DDD8CB;
    padding-top: 4px;
    padding-left: 11px;
}}
"""

# Archival Parchment Input Field (#EAE6DA fill with #7A8B84 subtle border)
PARCHMENT_INPUT_QSS = f"""
QLineEdit {{
    background-color: {BG_PARCHMENT};
    color: {TEXT_CHARCOAL};
    border: 1.2px solid {BORDER_MUTED};
    border-radius: 5px;
    padding: 4px 10px;
    selection-background-color: {ACCENT_TERRACOTTA};
    selection-color: #FFFFFF;
}}
QLineEdit:focus {{
    border: 1.8px solid {ACCENT_TERRACOTTA};
    background-color: #FFFFFF;
}}
"""

# Parchment Multi-line Text Editor (#FAF8F2)
PARCHMENT_TEXTEDIT_QSS = f"""
QTextEdit, QPlainTextEdit {{
    background-color: {BG_PARCHMENT_LIGHT};
    color: {TEXT_CHARCOAL};
    border: 1.2px solid {BORDER_MUTED};
    border-radius: 5px;
    padding: 6px;
    selection-background-color: {ACCENT_TERRACOTTA};
    selection-color: #FFFFFF;
}}
QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1.8px solid {ACCENT_TERRACOTTA};
}}
"""

# Soft Sage Scrollbar
MISTY_SCROLL_QSS = f"""
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollBar:vertical {{
    border: none;
    background: rgba(94, 111, 104, 0.15);
    width: 6px;
    margin: 0px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER_MUTED};
    min-height: 18px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical:hover {{
    background: {ACCENT_TERRACOTTA};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    height: 0px;
}}
"""

# Dropdown Context Menu with Misty Atmosphere
MISTY_MENU_QSS = f"""
QMenu {{
    background-color: {BG_PARCHMENT};
    color: {TEXT_CHARCOAL};
    border: 1.5px solid {BORDER_MUTED};
    border-radius: 6px;
    padding: 4px;
    font-weight: 600;
}}
QMenu::item {{
    padding: 6px 20px;
    background-color: transparent;
    color: {TEXT_CHARCOAL};
    border-radius: 4px;
}}
QMenu::item:selected {{
    background-color: {ACCENT_TERRACOTTA};
    color: #FFFFFF;
}}
QMenu::separator {{
    height: 1.0px;
    background: {BORDER_MUTED};
    margin: 4px 6px;
}}
"""

# Compatibility aliases
SWISS_BTN_RED_QSS = TERRACOTTA_BTN_QSS
SWISS_BTN_BEIGE_QSS = PINE_PILL_BTN_QSS
SWISS_INPUT_QSS = PARCHMENT_INPUT_QSS
SWISS_TEXTEDIT_QSS = PARCHMENT_TEXTEDIT_QSS
SWISS_SCROLL_QSS = MISTY_SCROLL_QSS
SWISS_MENU_QSS = MISTY_MENU_QSS


# =========================================================================
# 4. QPainter Gradient & Atmospheric Capsule Drawing
# =========================================================================

def create_atmospheric_gradient(rect: QRectF) -> QLinearGradient:
    """
    Creates a smooth vertical atmospheric gradient mimicking the misty pine horizon:
    - Top (0.0): Muted Sage-Teal Mist (#9CAFAA)
    - Middle (0.55): Soft Desaturated Fog Cream-Green (#CBD2C4)
    - Bottom (1.0): Warm Dry-Grass Sand (#D6CEB8)
    """
    grad = QLinearGradient(0, rect.top(), 0, rect.bottom())
    grad.setColorAt(0.0, COLOR_GRAD_TOP)
    grad.setColorAt(0.55, COLOR_GRAD_MID)
    grad.setColorAt(1.0, COLOR_GRAD_BOT)
    return grad


def draw_misty_capsule(painter: QPainter, rect: QRectF, r: float):
    """
    Renders the main Dynamic Island capsule or floating node window in the
    Misty Sage & Terracotta aesthetic:
    - Base fill: Atmospheric Sage-to-Sand vertical gradient
    - Perimeter: Crisp 1.5px border in #6B7C75
    - Soft 1px inner mist highlight along top rim
    - Anti-aliasing and SmoothPixmapTransform enforced.
    """
    painter.save()
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.TextAntialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

    # 1. Base Atmospheric Gradient Fill
    grad = create_atmospheric_gradient(rect)
    painter.setBrush(QBrush(grad))
    painter.setPen(QPen(COLOR_BORDER_CAPSULE, 1.5))
    painter.drawRoundedRect(rect, r, r)

    # 2. Subtle Soft Inner Horizon Line at top (1px)
    inner_rect = rect.adjusted(1.5, 1.5, -1.5, -1.5)
    inner_r = max(2.0, r - 1.5)
    painter.setPen(QPen(QColor(255, 255, 255, 120), 1.0))
    painter.setBrush(Qt.NoBrush)
    painter.drawRoundedRect(inner_rect, inner_r, inner_r)

    painter.restore()

# Compatibility aliases
draw_swiss_capsule = draw_misty_capsule
draw_retro_bevel = lambda painter, rect, raised=True, line_w=1.0: None

BG_CANVAS = BG_PARCHMENT
BG_BEIGE = BG_PARCHMENT
BG_WELL = BG_WELL_PINE
BG_CARD = BG_PARCHMENT
INK_BLACK = TEXT_CHARCOAL
INK_DARK = TEXT_CHARCOAL
INK_MUTED = TEXT_MUTED
INK_FAINT = TEXT_FAINT
BORDER_STRUCT = BORDER_MUTED
BEVEL_LIGHT = "#FFFFFF"
BEVEL_DARK = "#7A8B84"
BEVEL_DEPRESSED = "#CBD2C4"
ACCENT_RED = ACCENT_TERRACOTTA
ACCENT_RED_HOVER = ACCENT_SIENNA
ACCENT_RED_PRESSED = ACCENT_PRESSED
ACCENT_BLUE = ACCENT_AMBER
ACCENT_GREEN = ACCENT_SAGE

COLOR_BG_CANVAS = COLOR_PARCHMENT
COLOR_BG_BEIGE = COLOR_PARCHMENT
COLOR_BG_WELL = QColor(94, 111, 104, 56)
COLOR_BG_CARD = COLOR_PARCHMENT
COLOR_BG_WHITE = COLOR_WHITE
COLOR_INK_BLACK = COLOR_TEXT_CHARCOAL
COLOR_INK_MUTED = QColor(TEXT_MUTED)
COLOR_ACCENT_RED = COLOR_TERRACOTTA
COLOR_ACCENT_BLUE = COLOR_AMBER
COLOR_ACCENT_GREEN = COLOR_SAGE
COLOR_BEVEL_LIGHT = QColor(255, 255, 255, 120)
COLOR_BEVEL_DARK = COLOR_BORDER_MUTED
