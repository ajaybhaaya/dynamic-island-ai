"""
main.py - Entry Point, System Tray Kill-Switch, Global Pynput Hooks & App Loop
Windows 11 Dynamic Island Desktop Companion
"""

import sys
import os
import ctypes
import time
import logging
from collections import deque
from PySide6.QtCore import Qt, QObject, Signal, QTimer
from PySide6.QtGui import QIcon, QAction, QColor, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QSystemTrayIcon,
    QMenu,
    QMessageBox,
)

from ui_island import DynamicIslandWindow
from avatar_widget import BotState
from ai_workers import ScreenVisionWorker, VoiceListenerWorker, OpenRouterChatWorker
from theme_misty_sage import MISTY_MENU_QSS

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DynamicIslandMain")


# =========================================================================
# Privacy Panic Window Minimizer
# =========================================================================

SW_MINIMIZE = 6

def minimize_all_other_windows(target_island_hwnd: int):
    """
    Minimizes all visible top-level windows via Win32 EnumWindows,
    preserving only the Dynamic Island window.
    """
    try:
        def enum_windows_callback(hwnd, lparam):
            if hwnd != target_island_hwnd and ctypes.windll.user32.IsWindowVisible(hwnd):
                # Filter out shell desktop & taskbar windows
                class_buf = ctypes.create_unicode_buffer(256)
                ctypes.windll.user32.GetClassNameW(hwnd, class_buf, 256)
                cls_name = class_buf.value
                if cls_name not in ("Shell_TrayWnd", "Progman", "WorkerW", "Shell_SecondaryTrayWnd"):
                    # Check window title length
                    txt_len = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                    if txt_len > 0:
                        ctypes.windll.user32.ShowWindow(hwnd, SW_MINIMIZE)
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        ctypes.windll.user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)
        logger.info("Privacy panic executed: minimized all top-level windows.")
    except Exception as e:
        logger.error("Privacy panic error: %s", e)


# =========================================================================
# Global Input Event Bridge (Pynput to Qt Main Thread)
# =========================================================================

class GlobalInputBridge(QObject):
    """
    Safely bridges background thread pynput events to the Qt main GUI loop.
    """
    rapid_clicks_detected = Signal()
    refresh_f5_detected = Signal()
    privacy_panic_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._click_timestamps = deque(maxlen=5)
        self._ctrl_pressed = False
        self._shift_pressed = False

    def on_click(self, x, y, button, pressed):
        if pressed:
            now = time.time()
            self._click_timestamps.append(now)
            if len(self._click_timestamps) == 5:
                # 5 clicks within 0.85 seconds (850ms) triggers SCARED
                if (self._click_timestamps[-1] - self._click_timestamps[0]) <= 0.85:
                    self.rapid_clicks_detected.emit()
                    self._click_timestamps.clear()

    def on_key_press(self, key):
        from pynput.keyboard import Key, KeyCode
        if key in (Key.ctrl, Key.ctrl_l, Key.ctrl_r):
            self._ctrl_pressed = True
        elif key in (Key.shift, Key.shift_l, Key.shift_r):
            self._shift_pressed = True
        elif key == Key.f5:
            self.refresh_f5_detected.emit()
        elif isinstance(key, KeyCode) and key.char in ('h', 'H'):
            if self._ctrl_pressed and self._shift_pressed:
                self.privacy_panic_requested.emit()

    def on_key_release(self, key):
        from pynput.keyboard import Key
        if key in (Key.ctrl, Key.ctrl_l, Key.ctrl_r):
            self._ctrl_pressed = False
        elif key in (Key.shift, Key.shift_l, Key.shift_r):
            self._shift_pressed = False


# =========================================================================
# System Tray Helper
# =========================================================================

def create_tray_icon_pixmap() -> QPixmap:
    """Generates a sleek pill-shaped vector icon for the Windows system tray."""
    pix = QPixmap(32, 32)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing, True)

    # Dark background pill
    painter.setBrush(QColor(18, 18, 24))
    painter.setPen(QColor(255, 255, 255, 60))
    painter.drawRoundedRect(2, 8, 28, 16, 8, 8)

    # Two glowing eyes
    painter.setBrush(QColor(255, 255, 255))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(10, 13, 3, 6)
    painter.drawEllipse(18, 13, 3, 6)

    painter.end()
    return pix


# =========================================================================
# Main Controller Application
# =========================================================================

class DynamicIslandApp:
    def __init__(self):
        # 1. Initialize PySide6 application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Windows Dynamic Island AI")
        self.app.setQuitOnLastWindowClosed(False)

        # 2. Main floating island window
        self.island = DynamicIslandWindow()
        self.island_hwnd = int(self.island.winId())

        # 3. Global input bridge & pynput listeners
        self.bridge = GlobalInputBridge()
        self.bridge.rapid_clicks_detected.connect(self._on_rapid_clicks)
        self.bridge.refresh_f5_detected.connect(self._on_refresh_f5)
        self.bridge.privacy_panic_requested.connect(self._on_privacy_panic)

        self._start_global_listeners()

        # 4. AI workers & conversational screen memory
        self._vision_worker = None
        self._voice_worker = None
        self._chat_worker = None
        self.last_screen_analysis = ""
        self.last_screen_time = 0.0

        # Wire island events
        self.island.request_screen_summary.connect(self._trigger_screen_summary)
        self.island.request_voice_toggle.connect(self._toggle_voice_listener)
        self.island.request_chat_question.connect(self._trigger_chat_question)
        self.island.privacy_panic_requested.connect(self._on_privacy_panic)

        # 5. System tray icon with Exit / Kill Switch
        self._init_system_tray()

    def _start_global_listeners(self):
        """Initializes non-blocking pynput global mouse and keyboard listeners."""
        try:
            from pynput import mouse, keyboard

            self.mouse_listener = mouse.Listener(on_click=self.bridge.on_click)
            self.mouse_listener.daemon = True
            self.mouse_listener.start()

            self.keyboard_listener = keyboard.Listener(
                on_press=self.bridge.on_key_press,
                on_release=self.bridge.on_key_release
            )
            self.keyboard_listener.daemon = True
            self.keyboard_listener.start()
            logger.info("Global pynput listeners active.")
        except Exception as e:
            logger.warning("Could not start global pynput listeners: %s", e)

    def _init_system_tray(self):
        self.tray = QSystemTrayIcon(self.island)
        self.tray.setIcon(QIcon(create_tray_icon_pixmap()))
        self.tray.setToolTip("Dynamic Island AI Overlay (Ctrl+Shift+H for Privacy Panic)")

        menu = QMenu()
        menu.setStyleSheet(MISTY_MENU_QSS)

        act_toggle = QAction("Toggle Expand / Collapse", menu)
        act_toggle.triggered.connect(self.island.toggle_expand)
        menu.addAction(act_toggle)

        # Position submenu
        pos_menu = menu.addMenu("📍 Screen Position")
        for p_key, p_label in [("top", "Top"), ("bottom", "Bottom"), ("left", "Left"), ("right", "Right")]:
            act_p = QAction(f"Move to {p_label}", pos_menu)
            act_p.triggered.connect(lambda checked=False, k=p_key: self.island.set_position(k))
            pos_menu.addAction(act_p)
        act_cycle = QAction("🔄 Cycle Next Position", pos_menu)
        act_cycle.triggered.connect(self.island.cycle_position)
        pos_menu.addAction(act_cycle)

        act_chat = QAction("⚡ Ask AI Agent (Tab 5)", menu)
        act_chat.triggered.connect(lambda: (self.island.expand_island(), self.island.carousel.snap_to_page(4)))
        menu.addAction(act_chat)

        act_timer = QAction("⏱️ Focus & Sprint Timer (Tab 6)", menu)
        act_timer.triggered.connect(lambda: (self.island.expand_island(), self.island.carousel.snap_to_page(5)))
        menu.addAction(act_timer)

        act_workspace = QAction("🌐 Neural Workspace (Tab 7)", menu)
        act_workspace.triggered.connect(lambda: (self.island.expand_island(), self.island.carousel.snap_to_page(6)))
        menu.addAction(act_workspace)

        act_panic = QAction("Privacy Panic (Minimize All Windows)", menu)
        act_panic.triggered.connect(self._on_privacy_panic)
        menu.addAction(act_panic)

        act_sum = QAction("Analyze Screen Now", menu)
        act_sum.triggered.connect(lambda: self._trigger_screen_summary(""))
        menu.addAction(act_sum)

        menu.addSeparator()

        act_quit = QAction("Exit / Kill Switch", menu)
        act_quit.triggered.connect(self.quit)
        menu.addAction(act_quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.island.toggle_expand()

    def _on_rapid_clicks(self):
        logger.info("Triggering SCARED state from rapid clicking.")
        self.island.set_avatar_state(BotState.SCARED, duration_ms=900)

    def _on_refresh_f5(self):
        logger.info("Triggering HAPPY state from F5 refresh.")
        self.island.set_avatar_state(BotState.HAPPY, duration_ms=1400)

    def _on_privacy_panic(self):
        logger.info("Executing Privacy Panic command.")
        minimize_all_other_windows(self.island_hwnd)
        self.island.set_avatar_state(BotState.HAPPY, duration_ms=1200)

    def _trigger_screen_summary(self, prompt: str):
        if self._vision_worker and self._vision_worker.isRunning():
            logger.info("Vision worker already running.")
            return

        logger.info("Starting OpenRouter ScreenVisionWorker...")
        self._vision_worker = ScreenVisionWorker(prompt=prompt, parent=self.island)
        self._vision_worker.chunk_received.connect(self._on_vision_chunk)
        self._vision_worker.finished.connect(self._on_vision_finished)
        self._vision_worker.start()

    def _on_vision_chunk(self, chunk_text: str):
        self.island.carousel.page1.set_output_text(chunk_text, is_success=True)

    def _on_vision_finished(self, text: str, is_success: bool):
        self.island.carousel.page1.set_output_text(text, is_success)
        if is_success:
            self.last_screen_analysis = text
            self.last_screen_time = time.time()
            self.island.carousel.page5.set_screen_context_active(True)
            self.island.set_avatar_state(BotState.HAPPY, duration_ms=1400)
        else:
            self.island.set_avatar_state(BotState.SAD, duration_ms=1200)

    def _trigger_chat_question(self, question: str, system_prompt: str = ""):
        if self._chat_worker and self._chat_worker.isRunning():
            logger.info("Chat worker already running.")
            return

        screen_ctx = ""
        # Inject screen context if captured within the last 15 minutes
        if self.last_screen_analysis and (time.time() - self.last_screen_time) < 900:
            screen_ctx = self.last_screen_analysis

        logger.info("Starting OpenRouterChatWorker for question: '%s' (has_screen_ctx=%s)", question[:50], bool(screen_ctx))
        self._chat_worker = OpenRouterChatWorker(
            question=question,
            system_prompt=system_prompt,
            screen_context=screen_ctx,
            parent=self.island
        )
        self._chat_worker.chunk_received.connect(self._on_chat_chunk)
        self._chat_worker.finished.connect(self._on_chat_finished)
        self._chat_worker.start()

    def _on_chat_chunk(self, chunk_text: str):
        self.island.carousel.page5.set_reply_text(chunk_text, is_success=True)

    def _on_chat_finished(self, reply_text: str, is_success: bool):
        self.island.carousel.page5.set_reply_text(reply_text, is_success)
        if is_success:
            self.island.set_avatar_state(BotState.HAPPY, duration_ms=1500)
        else:
            self.island.set_avatar_state(BotState.SAD, duration_ms=1200)

    def _toggle_voice_listener(self):
        if self._voice_worker and self._voice_worker.isRunning():
            logger.info("Stopping voice listener...")
            self._voice_worker.stop()
            self._voice_worker = None
            self.island.carousel.page1.set_voice_active(False)
        else:
            logger.info("Starting voice listener...")
            self._voice_worker = VoiceListenerWorker(parent=self.island)
            self._voice_worker.speech_recognized.connect(self._on_voice_command)
            self._voice_worker.status_changed.connect(self._on_voice_status)
            self._voice_worker.start()
            self.island.carousel.page1.set_voice_active(True)

    def _on_voice_status(self, is_listening: bool, msg: str):
        self.island.carousel.page1.set_voice_active(is_listening)
        logger.info("Voice status: %s", msg)

    def _on_voice_command(self, recognized_text: str):
        cmd = recognized_text.lower()
        logger.info("Voice Command Received: '%s'", cmd)

        if "hide windows" in cmd or "privacy mode" in cmd or "minimize all" in cmd:
            self._on_privacy_panic()
        elif "summarize" in cmd or "analyze screen" in cmd:
            self._trigger_screen_summary("")
        elif "happy" in cmd or "smile" in cmd:
            self.island.set_avatar_state(BotState.HAPPY, duration_ms=1500)
        elif "scared" in cmd:
            self.island.set_avatar_state(BotState.SCARED, duration_ms=1000)
        elif "play" in cmd or "pause" in cmd:
            self.island.carousel.page2._on_toggle_play()
        elif "next" in cmd:
            self.island.carousel.page2._on_next()
        elif "previous" in cmd or "back" in cmd:
            self.island.carousel.page2._on_prev()

    def run(self):
        self.island.show()
        return self.app.exec()

    def quit(self):
        logger.info("Quitting Windows Dynamic Island.")
        if hasattr(self.island, "network_worker") and self.island.network_worker.isRunning():
            try:
                self.island.network_worker.stop()
            except Exception:
                pass
        if hasattr(self.island, "workspace_manager"):
            try:
                self.island.workspace_manager.close_all()
            except Exception:
                pass
        if self._voice_worker and self._voice_worker.isRunning():
            self._voice_worker.stop()
        if self._vision_worker and self._vision_worker.isRunning():
            self._vision_worker.wait(500)
        if self._chat_worker and self._chat_worker.isRunning():
            self._chat_worker.wait(500)
        self.app.quit()


if __name__ == "__main__":
    app_instance = DynamicIslandApp()
    sys.exit(app_instance.run())
