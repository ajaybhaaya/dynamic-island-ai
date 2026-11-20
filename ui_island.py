"""
ui_island.py - Misty Sage & Terracotta Illustrated Editorial Capsule (v2.0)
Windows 11 Dynamic Island Desktop Companion
"""

import time
import math
from PySide6.QtCore import (
    Qt,
    QRect,
    QRectF,
    QPointF,
    QPoint,
    Signal,
    Property,
    QPropertyAnimation,
    QParallelAnimationGroup,
    QEasingCurve,
    QEvent,
    QTimer,
)
from PySide6.QtGui import (
    QPainter,
    QColor,
    QBrush,
    QPen,
    QGuiApplication,
    QPainterPath,
    QLinearGradient,
    QRadialGradient,
    QAction,
    QFont,
)
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QGraphicsDropShadowEffect,
    QMenu,
    QPushButton,
)

from avatar_widget import AvatarWidget, BotState
from widgets_panel import (
    Page1Companion,
    Page2Media,
    Page3Telemetry,
    Page4Shelf,
    Page5Chat,
    Page6FocusTimer,
    Page7DevTools,
    Page8Scratchpad,
    Page9NeuralWorkspace,
    StatusDotWidget,
    get_editorial_font,
)
from network_worker import NetworkMonitorWorker, format_speed, get_ping_health_color
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
    BG_CARD,
    INK_BLACK,
    INK_MUTED,
    BEVEL_LIGHT,
    BEVEL_DARK,
    BEVEL_DEPRESSED,
    ACCENT_RED,
    ACCENT_RED_HOVER,
    ACCENT_RED_PRESSED,
    COLOR_BG_CANVAS,
    COLOR_INK_BLACK,
    COLOR_ACCENT_RED,
    draw_swiss_capsule,
    SWISS_MENU_QSS,
)
from neural_workspace import WorkspaceManager

TAB_TITLES = [
    "Tab 1: AI Companion & Screen Vision",
    "Tab 2: Media Player & Volume Controls",
    "Tab 3: Hardware Telemetry (RAM/CPU/Cache)",
    "Tab 4: Rich Document Shelf & Drag-Drop",
    "Tab 5: Quick AI Assistant (OpenRouter)",
    "Tab 6: Focus & Sprint Pomodoro Timer",
    "Tab 7: Neural Workspace (Extend Mode)",
]


class QuickSwitchButton(QPushButton):
    """
    Sleek quick switch dropdown button allowing instant navigation directly
    from any tab to any tab and back in the Misty Sage & Terracotta aesthetic.
    """
    def __init__(self, carousel, parent=None):
        super().__init__("📑 TABS ▾", parent)
        self.carousel = carousel
        self.setFixedHeight(22)
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(get_nav_pill_font(size=7.8, weight=QFont.Bold))
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_PARCHMENT};
                color: {TEXT_CHARCOAL};
                border: 1.2px solid {BORDER_MUTED};
                border-radius: 4px;
                padding: 2px 10px;
                font-weight: 700;
                letter-spacing: 1.0px;
            }}
            QPushButton:hover {{
                background-color: #FAF8F2;
                border-color: {ACCENT_TERRACOTTA};
                color: {ACCENT_TERRACOTTA};
            }}
            QPushButton:pressed {{
                background-color: #DDD8CB;
                padding-top: 3px;
                padding-left: 11px;
            }}
        """)
        self.setToolTip("Quick switch menu: jump directly to any tab")
        self.clicked.connect(self._show_menu)

    def _show_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(MISTY_MENU_QSS)
        cur = self.carousel.current_page
        for i, title in enumerate(TAB_TITLES):
            prefix = "✓  " if i == cur else "    "
            act = QAction(f"{prefix}{title}", menu)
            act.triggered.connect(lambda checked=False, target=i: self.carousel.snap_to_page(target))
            menu.addAction(act)

        # Show menu aligned above button
        p = self.mapToGlobal(QPoint(0, 0))
        menu_height = menu.sizeHint().height()
        menu.exec(QPoint(p.x(), p.y() - menu_height - 4))


class PageIndicatorBar(QWidget):
    """
    Bottom clickable page indicator bar.
    Shows 8 minimalist dots with fixed slot centers (active pill 16x6px, inactive 6x6px).
    Generous click area maps clicks directly to that specific tab
    (Dot 1 -> Tab 1, Dot 5 -> Tab 5, Dot 6 -> Tab 6, Dot 8 -> Tab 8).
    Hovering shows high-visibility glow and descriptive tab tooltip.
    """
    dot_clicked = Signal(int)

    def __init__(self, carousel, parent=None):
        super().__init__(parent)
        self.carousel = carousel
        self.slot_pitch = 20.0
        self.setFixedHeight(24)
        self.setMinimumWidth(180)
        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)
        self._hover_idx = -1
        self.carousel.page_changed.connect(lambda _: self.update())

    def _get_start_center_x(self) -> float:
        w = max(float(self.width()), 180.0)
        num_pages = self.carousel.num_pages
        total_span = (num_pages - 1) * self.slot_pitch
        return (w - total_span) / 2.0

    def get_dot_center(self, idx: int) -> float:
        start_cx = self._get_start_center_x()
        return start_cx + idx * self.slot_pitch

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        active_idx = self.carousel.current_page
        start_cx = self._get_start_center_x()
        cy = self.height() / 2.0

        for i in range(self.carousel.num_pages):
            cx = start_cx + i * self.slot_pitch
            is_active = (i == active_idx)
            is_hover = (i == self._hover_idx)

            if is_active:
                rect = QRectF(cx - 9.0, cy - 3.5, 18.0, 7.0)
                painter.setBrush(QBrush(COLOR_TERRACOTTA))
                painter.setPen(QPen(COLOR_MAHOGANY, 1.2))
                painter.drawRoundedRect(rect, 3.5, 3.5)
            elif is_hover:
                rect = QRectF(cx - 4.0, cy - 4.0, 8.0, 8.0)
                painter.setBrush(QBrush(COLOR_PINE_SLATE))
                painter.setPen(QPen(COLOR_TERRACOTTA, 1.2))
                painter.drawEllipse(rect)
            else:
                rect = QRectF(cx - 3.0, cy - 3.0, 6.0, 6.0)
                painter.setBrush(QBrush(COLOR_PINE_SLATE))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(rect)

    def _find_dot_index_at(self, click_x: float) -> int:
        start_cx = self._get_start_center_x()
        raw_idx = int(round((click_x - start_cx) / self.slot_pitch))
        return max(0, min(self.carousel.num_pages - 1, raw_idx))

    def mouseMoveEvent(self, event):
        idx = self._find_dot_index_at(event.position().x())
        if idx != self._hover_idx:
            self._hover_idx = idx
            if 0 <= idx < len(TAB_TITLES):
                self.setToolTip(f"{TAB_TITLES[idx]} (Click to jump)")
            self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self._hover_idx = -1
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            target_idx = self._find_dot_index_at(event.position().x())
            self.dot_clicked.emit(target_idx)
            self.carousel.snap_to_page(target_idx)
        super().mousePressEvent(event)


class CarouselContainer(QWidget):
    """
    Houses 8 pages side-by-side with horizontal swipe gesture tracking,
    rubber-band resistance, subtle parallax, and 300ms OutExpo snap animations.
    """
    page_changed = Signal(int)
    swiping = Signal(float)  # delta_x relative to current page

    def __init__(self, parent=None):
        super().__init__(parent)
        self.num_pages = 7
        self.current_page = 0
        self.page_width = 490
        self.page_height = 168

        self._offset_x = 0.0

        # Create the 7 functional pages (Tab 7 is Neural Workspace)
        self.page1 = Page1Companion(self)
        self.page2 = Page2Media(self)
        self.page3 = Page3Telemetry(self)
        self.page4 = Page4Shelf(self)
        self.page5 = Page5Chat(self)
        self.page6 = Page6FocusTimer(self)
        self.page7 = Page9NeuralWorkspace(self)
        self.page9 = self.page7  # Backward compatibility alias
        self.pages = [
            self.page1,
            self.page2,
            self.page3,
            self.page4,
            self.page5,
            self.page6,
            self.page7,
        ]

        for p in self.pages:
            p.setFixedSize(self.page_width, self.page_height)

        # Snap animation (300ms OutExpo)
        self._snap_anim = QPropertyAnimation(self, b"offset_x")
        self._snap_anim.setDuration(300)
        self._snap_anim.setEasingCurve(QEasingCurve.OutExpo)

        # Gesture tracking
        self._is_dragging = False
        self._drag_start_x = 0
        self._drag_start_offset = 0.0

        self.setFixedSize(self.page_width, self.page_height)
        self._layout_pages()

    def get_offset_x(self) -> float:
        return self._offset_x

    def set_offset_x(self, val: float):
        self._offset_x = float(val)
        self._layout_pages()
        self.update()

    offset_x = Property(float, get_offset_x, set_offset_x)

    def _layout_pages(self):
        for i, page in enumerate(self.pages):
            x = int(self._offset_x + i * self.page_width)
            page.move(x, 0)

    def snap_to_page(self, page_idx: int):
        self.current_page = max(0, min(self.num_pages - 1, page_idx))
        target_offset = -self.current_page * self.page_width
        self._snap_anim.stop()
        self._snap_anim.setStartValue(self._offset_x)
        self._snap_anim.setEndValue(target_offset)
        self._snap_anim.start()
        self.page_changed.emit(self.current_page)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self._drag_start_x = event.position().x()
            self._drag_start_offset = self._offset_x
            self._snap_anim.stop()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_dragging:
            cur_x = event.position().x()
            dx = cur_x - self._drag_start_x
            new_offset = self._drag_start_offset + dx

            # Apply rubber-band resistance at boundaries (0 and 4)
            min_offset = -(self.num_pages - 1) * self.page_width
            max_offset = 0.0
            if new_offset > max_offset:
                overshoot = new_offset - max_offset
                new_offset = max_offset + (overshoot * 0.3)
            elif new_offset < min_offset:
                undershoot = min_offset - new_offset
                new_offset = min_offset - (undershoot * 0.3)

            self.set_offset_x(new_offset)
            self.swiping.emit(dx)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._is_dragging and event.button() == Qt.LeftButton:
            self._is_dragging = False
            cur_x = event.position().x()
            delta_x = cur_x - self._drag_start_x

            # If drag distance > 55px, switch pages
            if delta_x < -55 and self.current_page < self.num_pages - 1:
                self.snap_to_page(self.current_page + 1)
            elif delta_x > 55 and self.current_page > 0:
                self.snap_to_page(self.current_page - 1)
            else:
                self.snap_to_page(self.current_page)

            self.swiping.emit(0.0)
        super().mouseReleaseEvent(event)


class DynamicIslandWindow(QWidget):
    """
    Translucent Frosted-Glass Capsule (v2.0) for Windows 11.
    Frameless, translucent, staying on top, customizable to 4 screen positions.
    Elastic-spring physics (380ms OutBack overshoot=1.22 expand, 280ms OutQuint collapse).
    """
    request_screen_summary = Signal(str)
    request_voice_toggle = Signal()
    request_chat_question = Signal(str)
    file_dropped = Signal(str)
    privacy_panic_requested = Signal()

    POSITIONS = ["top", "bottom", "left", "right"]

    def __init__(self, parent=None):
        super().__init__(parent)

        # Window Flags & Attributes
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAcceptDrops(True)

        # Active position (top, bottom, left, right)
        self.current_position = "top"

        # Dimensions: Collapsed (264x54, r=27) -> Expanded (490x220, r=34)
        self.COLLAPSED_W = 264
        self.COLLAPSED_H = 54
        self.COLLAPSED_RADIUS = 27.0

        self.EXPANDED_W = 490
        self.EXPANDED_H = 220
        self.EXPANDED_RADIUS = 34.0

        self.is_expanded = False

        # Animated properties
        self._cur_w = float(self.COLLAPSED_W)
        self._cur_h = float(self.COLLAPSED_H)
        self._corner_radius = self.COLLAPSED_RADIUS
        self._collapsed_opacity = 1.0
        self._expanded_opacity = 0.0
        self._specular_intensity = 0.45
        self._swipe_parallax_offset = 0.0

        # Ambient elevation shadow for opaque pill
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(24)
        self._shadow.setColor(QColor(0, 0, 0, 180))
        self._shadow.setOffset(0, 6)
        self.setGraphicsEffect(self._shadow)

        # Setup subviews
        self._init_subviews()

        # Parallel Animation Group for Expand/Collapse with spring physics
        self._setup_animations()

        # Initial geometry positioning
        self._update_window_geometry()

        # Monitor resolution change listener
        primary_screen = QGuiApplication.primaryScreen()
        if primary_screen:
            primary_screen.geometryChanged.connect(self._on_screen_geometry_changed)

    # ---------------------------------------------------------------------
    # Animated Properties
    # ---------------------------------------------------------------------

    def get_island_width(self) -> float:
        return self._cur_w

    def set_island_width(self, w: float):
        self._cur_w = float(w)
        self._update_window_geometry()
        self.update()

    island_width = Property(float, get_island_width, set_island_width)

    def get_island_height(self) -> float:
        return self._cur_h

    def set_island_height(self, h: float):
        self._cur_h = float(h)
        self._update_window_geometry()
        self.update()

    island_height = Property(float, get_island_height, set_island_height)

    def get_corner_radius(self) -> float:
        return self._corner_radius

    def set_corner_radius(self, r: float):
        self._corner_radius = float(r)
        self.update()

    corner_radius = Property(float, get_corner_radius, set_corner_radius)

    def get_collapsed_opacity(self) -> float:
        return self._collapsed_opacity

    def set_collapsed_opacity(self, o: float):
        self._collapsed_opacity = float(o)
        self.collapsed_container.setVisible(o > 0.02)
        self.update()

    collapsed_opacity = Property(float, get_collapsed_opacity, set_collapsed_opacity)

    def get_expanded_opacity(self) -> float:
        return self._expanded_opacity

    def set_expanded_opacity(self, o: float):
        self._expanded_opacity = float(o)
        self.expanded_container.setVisible(o > 0.02)
        self.update()

    expanded_opacity = Property(float, get_expanded_opacity, set_expanded_opacity)

    def get_specular_intensity(self) -> float:
        return self._specular_intensity

    def set_specular_intensity(self, val: float):
        self._specular_intensity = float(val)
        self.update()

    specular_intensity = Property(float, get_specular_intensity, set_specular_intensity)

    # ---------------------------------------------------------------------
    # Subview Initialization
    # ---------------------------------------------------------------------

    def _init_subviews(self):
        # 1. Collapsed Pill Container
        self.collapsed_container = QWidget(self)
        self.collapsed_container.setGeometry(0, 0, self.COLLAPSED_W, self.COLLAPSED_H)
        c_layout = QHBoxLayout(self.collapsed_container)
        c_layout.setContentsMargins(8, 5, 12, 5)
        c_layout.setSpacing(10)

        # Avatar in collapsed state (42x42px) inside smoked glass pod
        self.collapsed_avatar = AvatarWidget(size=42, parent=self.collapsed_container)
        c_layout.addWidget(self.collapsed_avatar, alignment=Qt.AlignVCenter)

        # Telemetry / Status indicator in collapsed pill with italic typography
        self.collapsed_status_col = QVBoxLayout()
        self.collapsed_status_col.setSpacing(1)
        self.collapsed_status_col.setAlignment(Qt.AlignVCenter)

        # Top row: Title + Live Speeds (Consolas monospace fixed-width)
        row_top = QHBoxLayout()
        row_top.setSpacing(6)
        row_top.setContentsMargins(0, 0, 0, 0)

        self.lbl_collapsed_title = QLabel("Dynamic Island", self.collapsed_container)
        self.lbl_collapsed_title.setFont(get_display_font(size=10.5, weight=QFont.Black))
        self.lbl_collapsed_title.setStyleSheet("color: #FFFFFF;")
        row_top.addWidget(self.lbl_collapsed_title)
        row_top.addStretch(1)

        self.lbl_collapsed_speed = QLabel("↓ 0K  ↑ 0K", self.collapsed_container)
        self.lbl_collapsed_speed.setFont(QFont("Consolas", 9, QFont.Bold))
        self.lbl_collapsed_speed.setStyleSheet(f"color: {TEXT_CHARCOAL};")
        self.lbl_collapsed_speed.setToolTip("Live network throughput (Download ↓ / Upload ↑)")
        row_top.addWidget(self.lbl_collapsed_speed)

        self.collapsed_status_col.addLayout(row_top)

        # Bottom row: Connection Health Dot + Ping + AI Online
        row_bot = QHBoxLayout()
        row_bot.setSpacing(4)
        row_bot.setContentsMargins(0, 0, 0, 0)

        self.dot_collapsed = StatusDotWidget(size=6, parent=self.collapsed_container)
        row_bot.addWidget(self.dot_collapsed, alignment=Qt.AlignVCenter)

        self.lbl_collapsed_ping = QLabel("--ms", self.collapsed_container)
        self.lbl_collapsed_ping.setFont(QFont("Consolas", 8, QFont.Bold))
        self.lbl_collapsed_ping.setStyleSheet(f"color: {TEXT_CHARCOAL};")
        row_bot.addWidget(self.lbl_collapsed_ping, alignment=Qt.AlignVCenter)

        self.lbl_collapsed_sub = QLabel("• AI Online", self.collapsed_container)
        self.lbl_collapsed_sub.setFont(get_body_font(size=8.4, weight=QFont.Medium))
        self.lbl_collapsed_sub.setStyleSheet(f"color: {TEXT_CHARCOAL};")
        row_bot.addWidget(self.lbl_collapsed_sub, alignment=Qt.AlignVCenter)
        row_bot.addStretch(1)

        self.collapsed_status_col.addLayout(row_bot)
        c_layout.addLayout(self.collapsed_status_col, stretch=1)

        # 2. Expanded Hub Container
        self.expanded_container = QWidget(self)
        self.expanded_container.setGeometry(0, 0, self.EXPANDED_W, self.EXPANDED_H)
        self.expanded_container.setVisible(False)

        e_layout = QVBoxLayout(self.expanded_container)
        e_layout.setContentsMargins(0, 6, 0, 8)
        e_layout.setSpacing(4)

        # Carousel with 9 swipeable views
        self.carousel = CarouselContainer(self.expanded_container)
        self.carousel.page_changed.connect(self._on_carousel_page_changed)
        self.carousel.swiping.connect(self._on_carousel_swiping)
        e_layout.addWidget(self.carousel, alignment=Qt.AlignTop | Qt.AlignHCenter)

        # Wire Page 1 & Page 5 & Page 9 requests
        self.carousel.page1.request_screen_summary.connect(self.request_screen_summary.emit)
        self.carousel.page1.request_voice_toggle.connect(self.request_voice_toggle.emit)
        self.carousel.page1.request_open_chat.connect(lambda: self.carousel.snap_to_page(4))
        self.carousel.page5.request_chat_question.connect(self.request_chat_question.emit)
        self.carousel.page9.request_extend.connect(self._on_request_extend)

        # Workspace Manager for Neural Workspace Free-Roaming Floating Windows & Tethers
        self.workspace_manager = WorkspaceManager(self)
        self.carousel.page9.request_add_tab.connect(self._on_add_extension_tab)
        self.carousel.page9.request_remove_tab.connect(self._on_remove_extension_tab)
        self.carousel.page9.request_open_tab.connect(self._on_open_extension_tab)
        self.workspace_manager.tabs_updated.connect(self.carousel.page9.set_tabs_data)
        self.carousel.page9.set_tabs_data(self.workspace_manager.get_tabs_data())

        # Live Network Speed & Latency Engine
        self.collapsed_ticker_visible = True
        self._prev_online = True
        self.network_worker = NetworkMonitorWorker(self)
        self.network_worker.network_updated.connect(self._on_network_updated)
        self.carousel.page3.ping_target_changed.connect(self.network_worker.set_target)
        self.carousel.page3.toggle_pill_ticker.connect(self.set_pill_ticker_visible)
        self.network_worker.start()

        # Bottom Navigation & Quick Switch Bar
        self.bottom_bar = QWidget(self.expanded_container)
        self.bottom_bar.setFixedSize(self.EXPANDED_W, 28)
        b_layout = QHBoxLayout(self.bottom_bar)
        b_layout.setContentsMargins(14, 0, 14, 0)
        b_layout.setSpacing(10)

        # 1. Quick Switch Dropdown Button (Direct jump from any tab to any tab)
        self.btn_quick_switch = QuickSwitchButton(self.carousel, self.bottom_bar)
        b_layout.addWidget(self.btn_quick_switch, alignment=Qt.AlignVCenter)

        # 2. Clickable Page Indicator Dots (Dot 1 -> Tab 1, Dot 5 -> Tab 5, Dot 6 -> Tab 6, etc.)
        self.indicator_widget = PageIndicatorBar(self.carousel, self.bottom_bar)
        b_layout.addWidget(self.indicator_widget, stretch=1, alignment=Qt.AlignCenter)

        # 3. Direct Tab 1 / Return Button (Instant jump back to first tab or last tab)
        self.btn_first_tab = QPushButton("Tab 7 ⏭️", self.bottom_bar)
        self.btn_first_tab.setFixedHeight(22)
        self.btn_first_tab.setCursor(Qt.PointingHandCursor)
        self.btn_first_tab.setFont(get_nav_pill_font(size=7.6, weight=QFont.Bold))
        self.btn_first_tab.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_PARCHMENT};
                color: {TEXT_CHARCOAL};
                border: 1.2px solid {BORDER_MUTED};
                border-radius: 4px;
                padding: 2px 10px;
                font-weight: 700;
                letter-spacing: 1.0px;
            }}
            QPushButton:hover {{
                background-color: #FAF8F2;
                border-color: {ACCENT_TERRACOTTA};
                color: {ACCENT_TERRACOTTA};
            }}
            QPushButton:pressed {{
                background-color: #DDD8CB;
                padding-top: 3px;
                padding-left: 11px;
            }}
        """)
        self.btn_first_tab.setToolTip("Quick switch to Tab 7 (Neural Workspace)")
        self.btn_first_tab.clicked.connect(self._on_first_tab_clicked)
        b_layout.addWidget(self.btn_first_tab, alignment=Qt.AlignVCenter)

        e_layout.addWidget(self.bottom_bar, alignment=Qt.AlignBottom | Qt.AlignHCenter)

    def _setup_animations(self):
        # 1. Squish & Stretch Micro-Deformation (70ms before expand)
        self._squish_anim = QPropertyAnimation(self, b"island_width")
        self._squish_anim.setDuration(70)
        self._squish_anim.setEasingCurve(QEasingCurve.OutQuad)
        self._squish_anim.setStartValue(float(self.COLLAPSED_W))
        self._squish_anim.setEndValue(float(self.COLLAPSED_W + 4))

        # 2. Expand Animation Group (380ms, QEasingCurve.OutBack, overshoot=1.22)
        self._expand_group = QParallelAnimationGroup(self)

        anim_w = QPropertyAnimation(self, b"island_width")
        anim_w.setDuration(380)
        curve_expand = QEasingCurve(QEasingCurve.OutBack)
        curve_expand.setOvershoot(1.22)
        anim_w.setEasingCurve(curve_expand)
        anim_w.setStartValue(float(self.COLLAPSED_W))
        anim_w.setEndValue(float(self.EXPANDED_W))

        anim_h = QPropertyAnimation(self, b"island_height")
        anim_h.setDuration(380)
        anim_h.setEasingCurve(curve_expand)
        anim_h.setStartValue(float(self.COLLAPSED_H))
        anim_h.setEndValue(float(self.EXPANDED_H))

        anim_r = QPropertyAnimation(self, b"corner_radius")
        anim_r.setDuration(380)
        anim_r.setEasingCurve(curve_expand)
        anim_r.setStartValue(self.COLLAPSED_RADIUS)
        anim_r.setEndValue(self.EXPANDED_RADIUS)

        anim_spec = QPropertyAnimation(self, b"specular_intensity")
        anim_spec.setDuration(380)
        anim_spec.setEasingCurve(QEasingCurve.OutCubic)
        anim_spec.setStartValue(0.35)
        anim_spec.setEndValue(0.60)

        anim_c_op = QPropertyAnimation(self, b"collapsed_opacity")
        anim_c_op.setDuration(120)
        anim_c_op.setStartValue(1.0)
        anim_c_op.setEndValue(0.0)

        anim_e_op = QPropertyAnimation(self, b"expanded_opacity")
        anim_e_op.setDuration(240)
        anim_e_op.setStartValue(0.0)
        anim_e_op.setEndValue(1.0)

        self._expand_group.addAnimation(anim_w)
        self._expand_group.addAnimation(anim_h)
        self._expand_group.addAnimation(anim_r)
        self._expand_group.addAnimation(anim_spec)
        self._expand_group.addAnimation(anim_c_op)
        self._expand_group.addAnimation(anim_e_op)

        # 3. Collapse Animation Group (280ms, QEasingCurve.OutQuint)
        self._collapse_group = QParallelAnimationGroup(self)

        c_anim_w = QPropertyAnimation(self, b"island_width")
        c_anim_w.setDuration(280)
        c_anim_w.setEasingCurve(QEasingCurve.OutQuint)
        c_anim_w.setStartValue(float(self.EXPANDED_W))
        c_anim_w.setEndValue(float(self.COLLAPSED_W))

        c_anim_h = QPropertyAnimation(self, b"island_height")
        c_anim_h.setDuration(280)
        c_anim_h.setEasingCurve(QEasingCurve.OutQuint)
        c_anim_h.setStartValue(float(self.EXPANDED_H))
        c_anim_h.setEndValue(float(self.COLLAPSED_H))

        c_anim_r = QPropertyAnimation(self, b"corner_radius")
        c_anim_r.setDuration(280)
        c_anim_r.setEasingCurve(QEasingCurve.OutQuint)
        c_anim_r.setStartValue(self.EXPANDED_RADIUS)
        c_anim_r.setEndValue(self.COLLAPSED_RADIUS)

        c_anim_spec = QPropertyAnimation(self, b"specular_intensity")
        c_anim_spec.setDuration(280)
        c_anim_spec.setEasingCurve(QEasingCurve.OutCubic)
        c_anim_spec.setStartValue(0.60)
        c_anim_spec.setEndValue(0.35)

        c_anim_c_op = QPropertyAnimation(self, b"collapsed_opacity")
        c_anim_c_op.setDuration(200)
        c_anim_c_op.setStartValue(0.0)
        c_anim_c_op.setEndValue(1.0)

        c_anim_e_op = QPropertyAnimation(self, b"expanded_opacity")
        c_anim_e_op.setDuration(120)
        c_anim_e_op.setStartValue(1.0)
        c_anim_e_op.setEndValue(0.0)

        self._collapse_group.addAnimation(c_anim_w)
        self._collapse_group.addAnimation(c_anim_h)
        self._collapse_group.addAnimation(c_anim_r)
        self._collapse_group.addAnimation(c_anim_spec)
        self._collapse_group.addAnimation(c_anim_c_op)
        self._collapse_group.addAnimation(c_anim_e_op)

    # ---------------------------------------------------------------------
    # Positioning & Screen Geometry (4 Fixed Positions)
    # ---------------------------------------------------------------------

    def set_position(self, pos: str):
        """Sets the screen location: 'top', 'bottom', 'left', or 'right'."""
        if pos in self.POSITIONS:
            self.current_position = pos
            self._update_window_geometry()
            self.set_avatar_state(BotState.HAPPY, duration_ms=900)

    def cycle_position(self):
        """Cycles to the next screen position in order: top -> bottom -> left -> right."""
        idx = self.POSITIONS.index(self.current_position)
        next_pos = self.POSITIONS[(idx + 1) % len(self.POSITIONS)]
        self.set_position(next_pos)

    def _update_window_geometry(self):
        screen = QGuiApplication.primaryScreen()
        if not screen:
            return
        avail = screen.availableGeometry()
        margin = 12

        w = int(self._cur_w)
        h = int(self._cur_h)

        if self.current_position == "top":
            x = int(avail.x() + (avail.width() - w) / 2.0)
            y = int(avail.y() + margin)
        elif self.current_position == "bottom":
            x = int(avail.x() + (avail.width() - w) / 2.0)
            y = int(avail.y() + avail.height() - h - margin)
        elif self.current_position == "left":
            x = int(avail.x() + margin)
            y = int(avail.y() + (avail.height() - h) / 2.0)
        elif self.current_position == "right":
            x = int(avail.x() + avail.width() - w - margin)
            y = int(avail.y() + (avail.height() - h) / 2.0)
        else:
            x = int(avail.x() + (avail.width() - w) / 2.0)
            y = int(avail.y() + margin)

        self.setGeometry(x, y, w, h)
        self.collapsed_container.setGeometry(0, 0, w, h)
        self.expanded_container.setGeometry(0, 0, w, h)

    def _on_screen_geometry_changed(self):
        self._update_window_geometry()

    # ---------------------------------------------------------------------
    # Right-Click Context Menu to Move Island
    # ---------------------------------------------------------------------

    def _show_position_menu(self, global_pos: QPoint):
        menu = QMenu(self)
        menu.setStyleSheet(SWISS_MENU_QSS)

        pos_labels = [
            ("top", "⬆️ Move to Top"),
            ("bottom", "⬇️ Move to Bottom"),
            ("left", "⬅️ Move to Left"),
            ("right", "➡️ Move to Right"),
        ]

        for p_key, p_label in pos_labels:
            prefix = "✓ " if self.current_position == p_key else "    "
            act = QAction(f"{prefix}{p_label}", menu)
            act.triggered.connect(lambda checked=False, k=p_key: self.set_position(k))
            menu.addAction(act)

        menu.addSeparator()

        act_cycle = QAction("🔄 Cycle to Next Position", menu)
        act_cycle.triggered.connect(self.cycle_position)
        menu.addAction(act_cycle)

        act_chat = QAction("⚡ Ask AI Agent (Tab 5)", menu)
        act_chat.triggered.connect(lambda: (self.expand_island(), self.carousel.snap_to_page(4)))
        menu.addAction(act_chat)

        act_timer = QAction("⏱️ Focus & Sprint Timer (Tab 6)", menu)
        act_timer.triggered.connect(lambda: (self.expand_island(), self.carousel.snap_to_page(5)))
        menu.addAction(act_timer)

        act_workspace = QAction("🌐 Neural Workspace (Tab 7)", menu)
        act_workspace.triggered.connect(lambda: (self.expand_island(), self.carousel.snap_to_page(6)))
        menu.addAction(act_workspace)

        act_panic = QAction("🖥️ Privacy Panic (Minimize All)", menu)
        act_panic.triggered.connect(self.privacy_panic_requested.emit)
        menu.addAction(act_panic)

        menu.exec(global_pos)

    # ---------------------------------------------------------------------
    # Expand / Collapse Trigger & Neural Workspace Extend
    # ---------------------------------------------------------------------

    def _on_request_extend(self):
        """
        Spawns the free-roaming floating workspace windows (NP, AI, DASH, + custom windows)
        with live grounded black neural tethers, then collapses the Dynamic
        Island back to its compact pill shape.
        """
        self.workspace_manager.spawn_workspace()
        self.collapse_island()

    def _on_add_extension_tab(self, from_idx: int):
        self.workspace_manager.add_custom_tab()

    def _on_remove_extension_tab(self, tab_idx: int):
        self.workspace_manager.remove_custom_tab(tab_idx)

    def _on_open_extension_tab(self, tab_idx: int):
        self.workspace_manager.focus_tab(tab_idx)

    def set_pill_ticker_visible(self, visible: bool):
        """Shows or hides the live network ticker in the collapsed pill."""
        self.collapsed_ticker_visible = visible
        self.lbl_collapsed_speed.setVisible(visible)
        self.dot_collapsed.setVisible(visible)
        self.lbl_collapsed_ping.setVisible(visible)
        if not visible:
            self.lbl_collapsed_sub.setText("● AI Online • Right-click to move")
            self.lbl_collapsed_sub.setStyleSheet(f"color: {TEXT_CHARCOAL};")
        else:
            self.lbl_collapsed_sub.setText("• AI Online")

    def _on_network_updated(self, dl_bps: float, ul_bps: float, ping_ms: int, is_online: bool):
        """Updates the collapsed pill micro-readout and forwards metrics to Page 3."""
        if self.collapsed_ticker_visible:
            self.lbl_collapsed_speed.setText(f"↓ {format_speed(dl_bps)}  ↑ {format_speed(ul_bps)}")
            self.lbl_collapsed_ping.setText(f"{ping_ms}ms" if is_online and ping_ms >= 0 else "--ms")
            self.dot_collapsed.set_status(ping_ms, is_online)
            if not is_online:
                self.lbl_collapsed_sub.setText("• OFFLINE")
                self.lbl_collapsed_sub.setStyleSheet(f"color: {ACCENT_TERRACOTTA}; font-weight: bold;")
            else:
                self.lbl_collapsed_sub.setText("• AI Online")
                self.lbl_collapsed_sub.setStyleSheet(f"color: {TEXT_CHARCOAL};")

        # Bot reaction hook: If connection drops, avatar briefly reacts
        if self._prev_online is True and not is_online:
            self.set_avatar_state(BotState.NERVOUS, duration_ms=1500)
        self._prev_online = is_online

        # Forward to Page 3 Telemetry Strip
        self.carousel.page3.update_network_data(dl_bps, ul_bps, ping_ms, is_online)

    def closeEvent(self, event):
        """Clean shutdown of background network monitor thread and spawned windows."""
        if hasattr(self, "network_worker") and self.network_worker.isRunning():
            self.network_worker.stop()
        if hasattr(self, "workspace_manager"):
            try:
                self.workspace_manager.close_all()
            except Exception:
                pass
        super().closeEvent(event)

    def toggle_expand(self):
        if self.is_expanded:
            self.collapse_island()
        else:
            self.expand_island()

    def expand_island(self):
        if self.is_expanded:
            return
        self.is_expanded = True
        self._collapse_group.stop()
        self._expand_group.stop()
        self._expand_group.start()

    def collapse_island(self):
        if not self.is_expanded:
            return
        self.is_expanded = False
        self._expand_group.stop()
        self._collapse_group.stop()
        self._collapse_group.start()

    def _on_carousel_page_changed(self, idx: int):
        self.indicator_widget.update()
        if idx == 0:
            self.btn_first_tab.setText("Tab 7 ⏭️")
            self.btn_first_tab.setToolTip("Quick switch to Tab 7 (Neural Workspace)")
        else:
            self.btn_first_tab.setText("◀ Tab 1")
            self.btn_first_tab.setToolTip("Quick switch back to Tab 1 (AI Companion)")

    def _on_first_tab_clicked(self):
        if self.carousel.current_page == 0:
            self.carousel.snap_to_page(self.carousel.num_pages - 1)
        else:
            self.carousel.snap_to_page(0)

    def _on_carousel_swiping(self, delta_x: float):
        # 15% parallax lag on background specular highlights
        self._swipe_parallax_offset = delta_x * 0.15
        if self.carousel.current_page == 0:
            self.carousel.page1.avatar.set_swipe_offset(delta_x)
        self.update()

    def set_avatar_state(self, state: BotState, duration_ms: int = 0):
        self.collapsed_avatar.set_state(state, duration_ms)
        self.carousel.page1.avatar.set_state(state, duration_ms)

    # ---------------------------------------------------------------------
    # Drawing: Misty Sage & Terracotta Illustrated Capsule
    # ---------------------------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        rect = QRectF(1.0, 1.0, self.width() - 2.0, self.height() - 2.0)
        r = self._corner_radius
        draw_misty_capsule(painter, rect, r)

    # ---------------------------------------------------------------------
    # Mouse & Keyboard Event Overrides (Squish on Click & Expand)
    # ---------------------------------------------------------------------

    def mousePressEvent(self, event):
        # Right click allows moving the AI assistant to 4 different places
        if event.button() == Qt.RightButton:
            self._show_position_menu(event.globalPosition().toPoint())
            return

        # Left click on collapsed pill: squish micro-deformation then expand
        if not self.is_expanded and event.button() == Qt.LeftButton:
            self._squish_anim.stop()
            self._squish_anim.finished.connect(self._on_squish_finished)
            self._squish_anim.start()
        super().mousePressEvent(event)

    def _on_squish_finished(self):
        try:
            self._squish_anim.finished.disconnect(self._on_squish_finished)
        except Exception:
            pass
        self.expand_island()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.is_expanded:
            self.collapse_island()
            return
        # Quick number key jumps: 1 through 9
        if self.is_expanded and Qt.Key_1 <= event.key() <= Qt.Key_9:
            target_idx = event.key() - Qt.Key_1
            self.carousel.snap_to_page(target_idx)
            return
        super().keyPressEvent(event)

    def changeEvent(self, event):
        # Collapse on WindowDeactivate (clicking outside capsule)
        if event.type() == QEvent.ActivationChange and not self.isActiveWindow():
            if self.is_expanded:
                self.collapse_island()
        super().changeEvent(event)

    # ---------------------------------------------------------------------
    # Drag and Drop Handling (NERVOUS state & shelf drop)
    # ---------------------------------------------------------------------

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.set_avatar_state(BotState.NERVOUS)
            # Expand to show shelf if collapsed
            if not self.is_expanded:
                self.expand_island()
                self.carousel.snap_to_page(3)  # Shelf page
        else:
            super().dragEnterEvent(event)

    def dragLeaveEvent(self, event):
        self.set_avatar_state(BotState.IDLE)
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            for url in event.mimeData().urls():
                filepath = url.toLocalFile()
                if filepath:
                    self.carousel.page4.add_file(filepath)
                    self.file_dropped.emit(filepath)
            self.set_avatar_state(BotState.HAPPY, duration_ms=1600)
        else:
            super().dropEvent(event)
