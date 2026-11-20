"""
avatar_widget.py - Expressive, Procedural AI Companion Avatar
Windows 11 Dynamic Island Desktop Companion
"""

import math
import random
import time
from enum import Enum
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF, Property, QTime
from PySide6.QtGui import (
    QPainter,
    QColor,
    QBrush,
    QPen,
    QRadialGradient,
    QPainterPath,
    QCursor,
)
from PySide6.QtWidgets import QWidget


class BotState(Enum):
    IDLE = 1
    SCARED = 2
    HAPPY = 3
    NERVOUS = 4
    SAD = 5


class AvatarWidget(QWidget):
    """
    Procedural Avatar rendering a translucent black box with two glowing white eyes.
    Runs at 60 FPS (16ms tick), interpolating cursor look-at offsets with lerp,
    blinking, and transitioning through expressive emotional states.
    """

    def __init__(self, size: int = 42, parent=None):
        super().__init__(parent)
        self._box_size = size
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        # State machine
        self._state = BotState.IDLE
        self._state_start_time = time.time()
        self._state_duration_ms = 0

        # Cursor tracking coordinates & lerp
        self._current_x = 0.0
        self._current_y = 0.0
        self._target_x = 0.0
        self._target_y = 0.0
        self.MAX_OFFSET_X = 6.5
        self.MAX_OFFSET_Y = 4.5
        self.DAMPENING_R = 400.0

        # Blink animation state
        self._is_blinking = False
        self._blink_start_time = 0.0
        self._blink_duration_ms = 140.0
        self._next_blink_time = time.time() + random.uniform(3.2, 5.5)

        # Drag/Swipe interaction offsets
        self._swipe_offset_x = 0.0
        self._teardrop_progress = 0.0

        # 60 FPS rendering timer (16ms frame tick)
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(16)
        self._anim_timer.timeout.connect(self._on_frame_tick)
        self._anim_timer.start()

    def set_box_size(self, size: int):
        self._box_size = size
        self.setFixedSize(size, size)
        self.update()

    def set_state(self, new_state: BotState, duration_ms: int = 0):
        """Transition avatar emotional state with optional duration before returning to IDLE."""
        self._state = new_state
        self._state_start_time = time.time()
        self._state_duration_ms = duration_ms
        self.update()

    def get_state(self) -> BotState:
        return self._state

    def set_swipe_offset(self, offset_x: float):
        """Called by carousel during drag/swipe to drive SAD state dynamically."""
        self._swipe_offset_x = offset_x
        if offset_x < -35:
            if self._state != BotState.SAD:
                self.set_state(BotState.SAD)
        elif self._state == BotState.SAD and self._state_duration_ms == 0:
            self.set_state(BotState.IDLE)
        self.update()

    def _on_frame_tick(self):
        now = time.time()
        elapsed_state_ms = (now - self._state_start_time) * 1000.0

        # Check timed state decay back to IDLE
        if self._state_duration_ms > 0 and elapsed_state_ms >= self._state_duration_ms:
            self._state = BotState.IDLE
            self._state_duration_ms = 0

        # Eye blink logic in IDLE
        if self._state == BotState.IDLE:
            if not self._is_blinking and now >= self._next_blink_time:
                self._is_blinking = True
                self._blink_start_time = now
            elif self._is_blinking:
                if (now - self._blink_start_time) * 1000.0 >= self._blink_duration_ms:
                    self._is_blinking = False
                    self._next_blink_time = now + random.uniform(3.2, 5.5)

        # Cursor look-at mathematical tracking
        global_center = self.mapToGlobal(self.rect().center())
        cursor_pos = QCursor.pos()
        dx = cursor_pos.x() - global_center.x()
        dy = cursor_pos.y() - global_center.y()
        dist = math.hypot(dx, dy)

        factor = min(dist / self.DAMPENING_R, 1.0)
        self._target_x = (dx / (dist + 1e-5)) * self.MAX_OFFSET_X * factor
        self._target_y = (dy / (dist + 1e-5)) * self.MAX_OFFSET_Y * factor

        # Smooth exponential lerp
        self._current_x += (self._target_x - self._current_x) * 0.18
        self._current_y += (self._target_y - self._current_y) * 0.18

        # Teardrop progression for NERVOUS state
        if self._state == BotState.NERVOUS:
            self._teardrop_progress = (elapsed_state_ms % 1200.0) / 1200.0

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        now = time.time()
        elapsed_ms = (now - self._state_start_time) * 1000.0
        w = self.width()
        h = self.height()
        scale = w / 42.0

        # Calculate state-specific offsets & transforms
        shake_x = 0.0
        bounce_y = 0.0
        dart_x = 0.0
        extra_y = 0.0
        eye_rot_deg = 0.0
        eye_opacity = 1.0
        glow_color = QColor(255, 255, 255, 90)

        if self._state == BotState.SCARED:
            decay = max(0.0, 1.0 - (elapsed_ms / max(1.0, float(self._state_duration_ms))))
            shake_x = math.sin(elapsed_ms * 0.08) * 2.5 * decay
            glow_color = QColor(144, 224, 239, 130)  # Pale cyan #90E0EF

        elif self._state == BotState.HAPPY:
            bounce_y = -abs(math.sin(elapsed_ms * 0.012)) * 4.0 * scale
            glow_color = QColor(255, 243, 176, 140)  # Warm white-gold #FFF3B0

        elif self._state == BotState.NERVOUS:
            dart_x = math.sin(elapsed_ms * 0.025) * 4.5 * scale
            glow_color = QColor(76, 201, 240, 110)

        elif self._state == BotState.SAD:
            eye_rot_deg = 18.0
            eye_opacity = 0.45
            extra_y = 3.0 * scale
            glow_color = QColor(160, 175, 200, 50)

        # Parallax shift for head/box (30%)
        box_shift_x = (self._current_x * 0.3 * scale) + shake_x
        box_shift_y = (self._current_y * 0.3 * scale) + bounce_y

        # 1. Render 100% Pitch-Black AI Bot Box with 2px Jet Black Frame
        box_rect = QRectF(
            2.0 + box_shift_x,
            2.0 + box_shift_y,
            w - 4.0,
            h - 4.0
        )
        box_radius = 8.0 * scale

        painter.save()
        # 100% Pitch-Black fill: #050507
        painter.setBrush(QBrush(QColor(5, 5, 7, 255)))
        # Crisp 2px Jet Black frame: #0F1115
        painter.setPen(QPen(QColor(15, 17, 21, 255), 2.0))
        painter.drawRoundedRect(box_rect, box_radius, box_radius)
        painter.restore()

        # Teardrop in NERVOUS state
        if self._state == BotState.NERVOUS:
            drop_x = box_rect.right() - 8.0 * scale
            drop_y = box_rect.top() + 6.0 * scale + (self._teardrop_progress * 18.0 * scale)
            drop_alpha = int(220 * (1.0 - (self._teardrop_progress * 0.5)))
            painter.save()
            painter.setBrush(QBrush(QColor(76, 201, 240, drop_alpha)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(drop_x, drop_y), 2.2 * scale, 3.2 * scale)
            painter.restore()

        # Eye gaze center with lerp, shake, dart, and extra Y
        center_x = (w / 2.0) + (self._current_x * scale) + shake_x + dart_x
        center_y = (h / 2.0) + (self._current_y * scale) + bounce_y + extra_y

        eye_spacing = 10.0 * scale
        left_eye_center = QPointF(center_x - (eye_spacing / 2.0), center_y)
        right_eye_center = QPointF(center_x + (eye_spacing / 2.0), center_y)

        # 2. Draw soft cyan-white ambient aura halo around eye zone
        painter.save()
        halo_radius = 20.0 * scale
        halo_grad = QRadialGradient(QPointF(center_x, center_y), halo_radius)
        # Default cyan-white ambient aura: rgba(210, 240, 255, 0.45)
        if self._state == BotState.IDLE:
            halo_grad.setColorAt(0.0, QColor(210, 240, 255, int(255 * 0.45)))
        else:
            halo_grad.setColorAt(0.0, glow_color)
        halo_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(halo_grad))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(center_x, center_y), halo_radius, halo_radius)
        painter.restore()

        # 3. Draw eyes based on emotional state
        painter.save()
        painter.setOpacity(eye_opacity)

        if self._state == BotState.HAPPY:
            # Crescent happy arcs (^ ^)
            pen = QPen(QColor(255, 255, 255), 2.6 * scale)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)

            arc_w = 7.0 * scale
            arc_h = 5.0 * scale
            for ec in (left_eye_center, right_eye_center):
                path = QPainterPath()
                path.moveTo(ec.x() - (arc_w / 2.0), ec.y() + (arc_h / 2.0))
                path.quadTo(ec.x(), ec.y() - (arc_h / 2.0), ec.x() + (arc_w / 2.0), ec.y() + (arc_h / 2.0))
                painter.drawPath(path)

        elif self._state == BotState.SCARED:
            # Startled circular eyes
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            r = 2.75 * scale
            painter.drawEllipse(left_eye_center, r, r)
            painter.drawEllipse(right_eye_center, r, r)

        elif self._state == BotState.NERVOUS:
            # Widened darting eyes
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            ew = 4.5 * scale
            eh = 7.0 * scale
            painter.drawRoundedRect(
                QRectF(left_eye_center.x() - ew, left_eye_center.y() - eh, ew * 2, eh * 2),
                ew, ew
            )
            painter.drawRoundedRect(
                QRectF(right_eye_center.x() - ew, right_eye_center.y() - eh, ew * 2, eh * 2),
                ew, ew
            )

        elif self._state == BotState.SAD:
            # Droopy outward angled eyes (\ /)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            ew = 3.2 * scale
            eh = 5.0 * scale

            # Left eye rotated outward
            painter.save()
            painter.translate(left_eye_center)
            painter.rotate(-eye_rot_deg)
            painter.drawRoundedRect(QRectF(-ew, -eh, ew * 2, eh * 2), ew, ew)
            painter.restore()

            # Right eye rotated outward
            painter.save()
            painter.translate(right_eye_center)
            painter.rotate(eye_rot_deg)
            painter.drawRoundedRect(QRectF(-ew, -eh, ew * 2, eh * 2), ew, ew)
            painter.restore()

        else:
            # IDLE state with randomized blinking
            eye_w = 7.0 * scale
            base_eye_h = 12.0 * scale
            eye_h = base_eye_h

            if self._is_blinking:
                blink_elapsed = (now - self._blink_start_time) * 1000.0
                progress = blink_elapsed / self._blink_duration_ms
                if progress < 0.5:
                    t = progress / 0.5
                    eye_h = base_eye_h * (1.0 - t) + 1.0 * t
                else:
                    t = (progress - 0.5) / 0.5
                    eye_h = 1.0 * (1.0 - t) + base_eye_h * t

            rx = eye_w / 2.0
            ry = min(rx, eye_h / 2.0)

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255)))

            left_rect = QRectF(
                left_eye_center.x() - (eye_w / 2.0),
                left_eye_center.y() - (eye_h / 2.0),
                eye_w,
                eye_h
            )
            right_rect = QRectF(
                right_eye_center.x() - (eye_w / 2.0),
                right_eye_center.y() - (eye_h / 2.0),
                eye_w,
                eye_h
            )
            painter.drawRoundedRect(left_rect, rx, ry)
            painter.drawRoundedRect(right_rect, rx, ry)

        painter.restore()
