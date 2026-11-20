"""
network_worker.py - Real-Time Network Speed & TCP Ping Latency Worker
CPU-efficient, non-blocking polling using psutil delta rates and socket.create_connection.
Windows 11 Dynamic Island Desktop Companion
"""

import socket
import time
import threading
import logging
from PySide6.QtCore import QThread, Signal
import psutil

logger = logging.getLogger("NetworkWorker")


def format_speed(bps: float) -> str:
    """
    Compact fixed-width format helper:
    < 1 KB/s -> 0K
    < 1 MB/s -> {val:.0f}K (e.g. 420K)
    < 1 GB/s -> {val:.1f}M (e.g. 12.4M)
    >= 1 GB/s -> {val:.1f}G (e.g. 1.2G)
    """
    if bps < 1024.0:
        return "0K"
    elif bps < 1024.0 * 1024.0:
        kb = bps / 1024.0
        return f"{kb:.0f}K"
    elif bps < 1024.0 * 1024.0 * 1024.0:
        mb = bps / (1024.0 * 1024.0)
        return f"{mb:.1f}M"
    else:
        gb = bps / (1024.0 * 1024.0 * 1024.0)
        return f"{gb:.1f}G"


def get_ping_health_color(ping_ms: int, is_online: bool) -> str:
    """
    Connection Health Color Palette:
    - < 70ms: Forest Sage Green (#4A6B5D / #22C55E)
    - 70ms - 160ms: Warm Amber (#E88D5A)
    - > 160ms or Offline: Terracotta Rust (#B83B24)
    """
    if not is_online or ping_ms < 0:
        return "#B83B24"
    if ping_ms < 70:
        return "#22C55E"
    elif ping_ms <= 160:
        return "#E88D5A"
    else:
        return "#B83B24"


class NetworkMonitorWorker(QThread):
    """
    Non-blocking background thread measuring bandwidth every 1.0s via psutil
    and TCP handshake latency every 3.0s via socket.create_connection(target, 443).
    Zero console flashes (no subprocess/cmd).
    """
    network_updated = Signal(float, float, int, bool)  # dl_bps, ul_bps, ping_ms, is_online
    target_changed = Signal(str)

    TARGET_WEB = "1.1.1.1"
    TARGET_API = "openrouter.ai"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop_event = threading.Event()
        self._target_host = self.TARGET_WEB
        self._target_lock = threading.Lock()
        self._last_ping_ms = -1
        self._is_online = False

    def set_target(self, target: str):
        """Switches the live ping target between 1.1.1.1 and openrouter.ai."""
        with self._target_lock:
            self._target_host = target
        self.target_changed.emit(target)
        logger.info(f"Ping target host switched to: {target}")

    def get_target(self) -> str:
        with self._target_lock:
            return self._target_host

    def stop(self):
        """Immediately sets stop flag and cleanly waits for the thread to terminate."""
        self._stop_event.set()
        self.wait(1500)

    def _measure_ping(self, host: str) -> tuple[int, bool]:
        """
        Measures real HTTPS/TCP handshake latency without subprocess or cmd window flash.
        Returns (latency_ms, is_online).
        """
        t0 = time.perf_counter()
        try:
            sock = socket.create_connection((host, 443), timeout=1.5)
            sock.close()
            latency = int(round((time.perf_counter() - t0) * 1000.0))
            return max(1, latency), True
        except (socket.timeout, OSError, Exception):
            return -1, False

    def run(self):
        logger.info("NetworkMonitorWorker started.")
        try:
            prev_counters = psutil.net_io_counters()
            prev_time = time.perf_counter()
        except Exception as e:
            logger.warning(f"Failed to read initial net_io_counters: {e}")
            prev_counters = None
            prev_time = time.perf_counter()

        # Perform initial ping check immediately
        with self._target_lock:
            target = self._target_host
        self._last_ping_ms, self._is_online = self._measure_ping(target)
        last_ping_check = time.perf_counter()

        while not self._stop_event.is_set():
            # Wait for 1.0 second or wake immediately if stopped
            if self._stop_event.wait(timeout=1.0):
                break

            now = time.perf_counter()
            dt = max(0.001, now - prev_time)

            # Bandwidth delta calculation
            dl_bps = 0.0
            ul_bps = 0.0
            try:
                curr_counters = psutil.net_io_counters()
                if prev_counters and curr_counters:
                    dl_bps = max(0.0, (curr_counters.bytes_recv - prev_counters.bytes_recv) / dt)
                    ul_bps = max(0.0, (curr_counters.bytes_sent - prev_counters.bytes_sent) / dt)
                prev_counters = curr_counters
                prev_time = now
            except Exception as e:
                logger.debug(f"Error calculating bandwidth delta: {e}")

            # Ping check every 3.0 seconds
            if (now - last_ping_check) >= 3.0:
                with self._target_lock:
                    cur_target = self._target_host
                self._last_ping_ms, self._is_online = self._measure_ping(cur_target)
                last_ping_check = now

            self.network_updated.emit(dl_bps, ul_bps, self._last_ping_ms, self._is_online)

        logger.info("NetworkMonitorWorker stopped cleanly.")
