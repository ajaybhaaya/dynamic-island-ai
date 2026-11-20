"""
ai_workers.py - Non-blocking QThread AI & Audio Workers with OpenRouter Vision & Streaming
Windows 11 Dynamic Island Desktop Companion
"""

import io
import os
import sys
import base64
import time
import json
import logging
import urllib.request
import urllib.error
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtGui import QGuiApplication, QImage

# Pillow and MSS for rapid lightweight screen capture
import mss
from PIL import Image

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AIWorkers")

# Try loading from local .env if present (multi-path resilient for both source & frozen exe)
def _load_local_env():
    candidates = []
    if getattr(sys, "frozen", False):
        candidates.append(os.path.join(os.path.dirname(sys.executable), ".env"))
    candidates.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
    candidates.append(os.path.join(os.getcwd(), ".env"))
    candidates.append(os.path.join(os.path.expanduser("~"), ".dynamic_island.env"))
    candidates.append(os.path.join(os.path.expanduser("~"), ".env"))

    for env_file in candidates:
        if os.path.exists(env_file):
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            except Exception:
                pass

_load_local_env()
DEFAULT_OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


# =========================================================================
# OpenRouter Live Telemetry Tracker (Session Stats & Remote Wallet)
# =========================================================================

class OpenRouterTelemetryTracker(QObject):
    """
    Centralized singleton tracker for OpenRouter API telemetry:
    - Session Prompt & Completion Token counts
    - Estimated Session Cost ($ USD)
    - Average Response Latency (ms)
    - Requests-Per-Minute (RPM) rolling metric
    - Remote Wallet Balance & Spend (queried from /api/v1/auth/key)
    """
    updated = Signal()

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = OpenRouterTelemetryTracker()
        return cls._instance

    def __init__(self, parent=None):
        super().__init__(parent)
        self.session_prompt_tokens = 0
        self.session_completion_tokens = 0
        self.session_requests = 0
        self.session_errors = 0
        self.session_cost_usd = 0.0

        self.request_latencies = []
        self.request_timestamps = []
        self.model_stats = {}

        # Remote wallet & key telemetry
        self.wallet_remaining = 999.96
        self.wallet_usage = 0.0335
        self.wallet_daily = 0.0047
        self.is_connected = False
        self.last_sync_time = 0.0

    def record_request(self, model: str, prompt_text: str, reply_text: str, latency_ms: float, is_success: bool = True):
        p_tok = max(1, len(prompt_text) // 4)
        c_tok = max(1, len(reply_text) // 4) if reply_text else 0

        self.session_prompt_tokens += p_tok
        self.session_completion_tokens += c_tok
        self.session_requests += 1
        if not is_success:
            self.session_errors += 1

        self.request_latencies.append(latency_ms)
        if len(self.request_latencies) > 60:
            self.request_latencies.pop(0)

        now = time.time()
        self.request_timestamps.append(now)
        self.request_timestamps = [t for t in self.request_timestamps if now - t <= 300]

        if model not in self.model_stats:
            self.model_stats[model] = {"requests": 0, "latencies": [], "tokens": 0}
        self.model_stats[model]["requests"] += 1
        self.model_stats[model]["latencies"].append(latency_ms)
        self.model_stats[model]["tokens"] += (p_tok + c_tok)

        cost = self._calculate_cost(model, p_tok, c_tok)
        self.session_cost_usd += cost

        logger.info(
            "Telemetry updated: model=%s, latency=%.1fms, tokens=(%d prompt, %d comp), cost=$%.6f",
            model, latency_ms, p_tok, c_tok, cost
        )
        self.updated.emit()

    def get_avg_latency_ms(self) -> float:
        if not self.request_latencies:
            return 320.0
        return sum(self.request_latencies) / len(self.request_latencies)

    def get_rpm(self) -> float:
        now = time.time()
        recent = [t for t in self.request_timestamps if now - t <= 60]
        return float(len(recent))

    def _calculate_cost(self, model: str, p_tok: int, c_tok: int) -> float:
        m = model.lower()
        if "claude-3.5-sonnet" in m:
            return (p_tok * 0.000003) + (c_tok * 0.000015)
        elif "gpt-4o-mini" in m:
            return (p_tok * 0.00000015) + (c_tok * 0.00000060)
        elif "gpt-4o" in m:
            return (p_tok * 0.0000025) + (c_tok * 0.000010)
        elif "gemini-2.0-flash" in m:
            return (p_tok * 0.00000010) + (c_tok * 0.00000040)
        elif "nemotron" in m or ":free" in m:
            return 0.0
        else:
            return (p_tok * 0.0000005) + (c_tok * 0.0000015)


class OpenRouterKeyInfoWorker(QThread):
    """
    Polls https://openrouter.ai/api/v1/auth/key to retrieve
    live remaining wallet balance and all-time spend metrics.
    """
    info_received = Signal(dict)

    def __init__(self, api_key: str = "", parent=None):
        super().__init__(parent)
        self.api_key = api_key.strip() if api_key.strip() else DEFAULT_OPENROUTER_KEY

    def run(self):
        if not self.api_key:
            return
        try:
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/auth/key",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "User-Agent": "WindowsDynamicIsland/2.0"
                }
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8")).get("data", {})
                tracker = OpenRouterTelemetryTracker.get_instance()
                tracker.wallet_remaining = float(data.get("limit_remaining") or 0.0)
                tracker.wallet_usage = float(data.get("usage") or 0.0)
                tracker.wallet_daily = float(data.get("usage_daily") or 0.0)
                tracker.is_connected = True
                tracker.last_sync_time = time.time()
                tracker.updated.emit()
                self.info_received.emit(data)
                logger.info(
                    "OpenRouter key telemetry synced: balance=$%.2f, spend=$%.4f",
                    tracker.wallet_remaining, tracker.wallet_usage
                )
        except Exception as e:
            logger.warning("Failed to poll OpenRouter key info: %s", e)


# =========================================================================
# Screen Capture Helper (Robust MSS + QScreen + PIL Fallback)
# =========================================================================

def capture_screen_image() -> Image.Image:
    """
    Captures primary screen using mss, with automatic fallback to Qt QScreen
    or PIL ImageGrab to ensure capture never fails across different Windows desktop environments.
    """
    try:
        with mss.MSS() as sct:
            monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
            sct_img = sct.grab(monitor)
            return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    except Exception as mss_err:
        logger.info("mss screen capture fallback: %s. Using QScreen.", mss_err)

    try:
        app = QGuiApplication.instance()
        if app:
            screen = QGuiApplication.primaryScreen()
            if screen:
                pix = screen.grabWindow(0)
                qimg = pix.toImage().convertToFormat(QImage.Format_RGB888)
                ptr = qimg.bits()
                return Image.frombuffer(
                    "RGB",
                    (qimg.width(), qimg.height()),
                    ptr,
                    "raw",
                    "RGB",
                    qimg.bytesPerLine(),
                    1
                )
    except Exception as qt_err:
        logger.info("Qt grabWindow fallback: %s. Using PIL ImageGrab.", qt_err)

    from PIL import ImageGrab
    return ImageGrab.grab()


# =========================================================================
# OpenRouter Screen Vision Worker (Decoupled from local Ollama)
# =========================================================================

class ScreenVisionWorker(QThread):
    """
    Captures the primary monitor buffer, downscales to a maximum dimension of 1280px
    preserving aspect ratio, encodes to base64 JPEG, and streams analysis from
    OpenRouter multimodal models (Claude 3.5 Sonnet, GPT-4o, etc.).
    """
    chunk_received = Signal(str)  # Live streaming text chunks
    finished = Signal(str, bool)  # (result_text, is_success)
    status_updated = Signal(str)

    def __init__(
        self,
        prompt: str = "",
        model_name: str = "anthropic/claude-3.5-sonnet",
        api_key: str = "",
        stream: bool = True,
        parent=None
    ):
        super().__init__(parent)
        self.prompt = prompt.strip()
        self.model_name = model_name
        self.api_key = api_key.strip() if api_key.strip() else DEFAULT_OPENROUTER_KEY
        self.stream = stream

    def run(self):
        if not self.api_key:
            self.error_occurred.emit("⚠️ OpenRouter API Key Missing. Please set OPENROUTER_API_KEY in .env or as a system environment variable.")
            return

        try:
            self.status_updated.emit("Capturing screen...")
            logger.info("Starting screen capture for OpenRouter vision analysis...")

            # 1. Capture screen buffer
            img = capture_screen_image()
            orig_w, orig_h = img.size

            # 2. Downscale to max dimension of 1280px preserving aspect ratio
            max_dim = 1280
            if max(orig_w, orig_h) > max_dim:
                scale = max_dim / float(max(orig_w, orig_h))
                new_w = int(orig_w * scale)
                new_h = int(orig_h * scale)
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                logger.info("Downscaled screen from %dx%d to %dx%d (max %dpx)", orig_w, orig_h, new_w, new_h, max_dim)

            # 3. Encode image to base64 JPEG
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=82)
            base64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
            image_data_url = f"data:image/jpeg;base64,{base64_data}"

            self.status_updated.emit("Analyzing screen via OpenRouter...")

            # 4. Construct prompt text
            if self.prompt:
                prompt_text = (
                    f"Analyze this active desktop screenshot and answer this specific question: \"{self.prompt}\". "
                    f"Provide a concise, highly structured summary formatted for a compact desktop UI overlay."
                )
            else:
                prompt_text = (
                    "Analyze this active desktop screenshot. Provide a concise, highly structured summary "
                    "of the visible applications, active tasks, and critical content. "
                    "Keep the output formatted for a compact UI overlay."
                )

            # 5. OpenRouter Headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/YourRepo/DynamicIsland",
                "X-Title": "Windows Dynamic Island AI Assistant",
                "User-Agent": "WindowsDynamicIsland/2.0"
            }

            # Model priority list: target requested model first, then resilient fallbacks
            models_to_try = [self.model_name]
            for candidate in ["openai/gpt-4o", "openai/gpt-4o-mini", "nvidia/nemotron-3.5-super-vl:free"]:
                if candidate not in models_to_try:
                    models_to_try.append(candidate)

            last_error_msg = ""
            req_start_time = time.time()
            for model_id in models_to_try:
                try:
                    logger.info("Attempting OpenRouter vision payload with model: %s", model_id)
                    payload = {
                        "model": model_id,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": prompt_text
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": image_data_url
                                        }
                                    }
                                ]
                            }
                        ],
                        "stream": self.stream,
                        "max_tokens": 400
                    }

                    req_data = json.dumps(payload).encode("utf-8")
                    req = urllib.request.Request(
                        OPENROUTER_API_URL,
                        data=req_data,
                        headers=headers
                    )

                    with urllib.request.urlopen(req, timeout=25) as response:
                        if self.stream:
                            accumulated = ""
                            for line in response:
                                line_str = line.decode("utf-8").strip()
                                if line_str.startswith("data: "):
                                    data_content = line_str[6:].strip()
                                    if data_content == "[DONE]":
                                        break
                                    try:
                                        chunk_json = json.loads(data_content)
                                        delta = chunk_json.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                        if delta:
                                            accumulated += delta
                                            self.chunk_received.emit(accumulated)
                                    except Exception:
                                        pass

                            if accumulated.strip():
                                latency = (time.time() - req_start_time) * 1000
                                OpenRouterTelemetryTracker.get_instance().record_request(
                                    model_id, prompt_text, accumulated.strip(), latency, True
                                )
                                logger.info("Streamed vision response received (%d chars, model=%s)", len(accumulated), model_id)
                                self.finished.emit(accumulated.strip(), True)
                                return
                        else:
                            res_body = response.read().decode("utf-8")
                            data = json.loads(res_body)
                            choices = data.get("choices", [])
                            if choices:
                                reply_text = choices[0].get("message", {}).get("content", "").strip()
                                latency = (time.time() - req_start_time) * 1000
                                OpenRouterTelemetryTracker.get_instance().record_request(
                                    model_id, prompt_text, reply_text, latency, True
                                )
                                logger.info("Vision response received (%d chars, model=%s)", len(reply_text), model_id)
                                self.finished.emit(reply_text, True)
                                return

                except urllib.error.HTTPError as http_err:
                    try:
                        err_detail = http_err.read().decode("utf-8")
                        err_json = json.loads(err_detail)
                        msg = err_json.get("error", {}).get("message", str(http_err))
                    except Exception:
                        msg = str(http_err)
                    logger.warning("OpenRouter model %s error (%d): %s", model_id, http_err.code, msg)
                    last_error_msg = f"HTTP {http_err.code}: {msg}"
                    continue

                except Exception as call_err:
                    logger.warning("OpenRouter model %s call failed: %s", model_id, call_err)
                    last_error_msg = str(call_err)
                    continue

            # If all model attempts failed
            latency = (time.time() - req_start_time) * 1000
            OpenRouterTelemetryTracker.get_instance().record_request(
                self.model_name, prompt_text, "", latency, False
            )
            self.finished.emit(f"Vision API Error: {last_error_msg}", False)

        except Exception as e:
            logger.error("ScreenVisionWorker critical error: %s", e)
            self.finished.emit(f"Screen vision error: {str(e)}", False)


# =========================================================================
# Voice Listener Worker (faster-whisper on CPU)
# =========================================================================

class VoiceListenerWorker(QThread):
    """
    Background audio capture and faster-whisper speech recognition running on CPU.
    Detects key phrases like 'hide windows', 'privacy mode', 'summarize', etc.
    """
    speech_recognized = Signal(str)
    status_changed = Signal(bool, str)  # (is_listening, message)
    error_occurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_running = False
        self._whisper_model = None

    def stop(self):
        self._is_running = False
        self.wait(1000)

    def _init_whisper(self):
        if self._whisper_model is not None:
            return True
        try:
            from faster_whisper import WhisperModel
            logger.info("Initializing faster-whisper tiny.en (int8, CPU)...")
            self._whisper_model = WhisperModel(
                "tiny.en",
                device="cpu",
                compute_type="int8",
                cpu_threads=2
            )
            logger.info("faster-whisper loaded successfully.")
            return True
        except Exception as e:
            logger.error("Failed to load faster-whisper: %s", e)
            self.error_occurred.emit(f"Whisper init error: {e}")
            return False

    def run(self):
        self._is_running = True
        self.status_changed.emit(True, "Initializing microphone...")

        import numpy as np

        try:
            import sounddevice as sd
        except ImportError:
            self.status_changed.emit(False, "sounddevice not installed")
            return

        if not self._init_whisper():
            self.status_changed.emit(False, "Whisper model unavailable")
            return

        sample_rate = 16000
        duration_sec = 3.5  # Record in 3.5s conversational chunks
        self.status_changed.emit(True, "Listening...")

        while self._is_running:
            try:
                recording = sd.rec(
                    int(duration_sec * sample_rate),
                    samplerate=sample_rate,
                    channels=1,
                    dtype="float32"
                )
                sd.wait()

                if not self._is_running:
                    break

                audio_data = recording.flatten()
                energy = float(np.sqrt(np.mean(audio_data ** 2)))
                if energy < 0.012:
                    time.sleep(0.05)
                    continue

                segments, info = self._whisper_model.transcribe(
                    audio_data,
                    beam_size=1,
                    language="en",
                    vad_filter=True
                )

                text = " ".join([seg.text for seg in segments]).strip()
                if text:
                    logger.info("Recognized voice: '%s'", text)
                    self.speech_recognized.emit(text)

            except Exception as e:
                logger.warning("Voice loop iteration error: %s", e)
                time.sleep(0.5)

        self.status_changed.emit(False, "Voice listening paused.")


# =========================================================================
# OpenRouter Quick AI Assistant Worker with Conversational Context
# =========================================================================

class OpenRouterChatWorker(QThread):
    """
    Non-blocking QThread worker that handles direct chat completions and
    subsequent conversational follow-ups with screen context via OpenRouter API.
    """
    chunk_received = Signal(str)  # Live streaming response chunks
    finished = Signal(str, bool)  # (reply_text, is_success)
    status_updated = Signal(str)

    def __init__(
        self,
        question: str,
        api_key: str = "",
        model_name: str = "openai/gpt-4o-mini",
        system_prompt: str = "",
        screen_context: str = "",
        stream: bool = True,
        parent=None
    ):
        super().__init__(parent)
        self.question = question.strip()
        self.api_key = api_key.strip() if api_key.strip() else DEFAULT_OPENROUTER_KEY
        self.model_name = model_name
        self.system_prompt = system_prompt.strip()
        self.screen_context = screen_context.strip()
        self.stream = stream

    def run(self):
        if not self.question:
            self.finished.emit("Please enter a question to ask the AI agent.", False)
            return

        if not self.api_key:
            self.finished.emit("⚠️ OpenRouter API Key Missing. Please set OPENROUTER_API_KEY in .env or as a system environment variable to use AI chat.", False)
            return

        try:
            self.status_updated.emit("Thinking...")
            logger.info("Sending question to OpenRouter model: %s", self.model_name)

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/YourRepo/DynamicIsland",
                "X-Title": "Windows Dynamic Island AI Assistant",
                "User-Agent": "WindowsDynamicIsland/2.0"
            }

            base_system = self.system_prompt if self.system_prompt else (
                "You are the built-in intelligent companion of the Windows 11 Dynamic Island desktop assistant. "
                "Provide concise, high-signal, clear, and direct answers tailored for a desktop overlay widget. "
                "Use brief bullet points or short code snippets when helpful."
            )

            if self.screen_context:
                sys_content = (
                    f"{base_system}\n\n"
                    f"[Active Desktop Screen Vision Context]:\n{self.screen_context}\n\n"
                    "Use this screen vision context to answer conversational follow-up questions accurately."
                )
            else:
                sys_content = base_system

            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": sys_content
                    },
                    {
                        "role": "user",
                        "content": self.question
                    }
                ],
                "temperature": 0.5,
                "max_tokens": 450,
                "stream": self.stream
            }

            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                OPENROUTER_API_URL,
                data=req_data,
                headers=headers
            )

            req_start_time = time.time()
            with urllib.request.urlopen(req, timeout=20) as response:
                if self.stream:
                    accumulated = ""
                    for line in response:
                        line_str = line.decode("utf-8").strip()
                        if line_str.startswith("data: "):
                            data_content = line_str[6:].strip()
                            if data_content == "[DONE]":
                                break
                            try:
                                chunk_json = json.loads(data_content)
                                delta = chunk_json.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if delta:
                                    accumulated += delta
                                    self.chunk_received.emit(accumulated)
                            except Exception:
                                pass

                    if accumulated.strip():
                        latency = (time.time() - req_start_time) * 1000
                        OpenRouterTelemetryTracker.get_instance().record_request(
                            self.model_name, self.question, accumulated.strip(), latency, True
                        )
                        logger.info("Streamed chat response complete (%d chars)", len(accumulated))
                        self.finished.emit(accumulated.strip(), True)
                    else:
                        latency = (time.time() - req_start_time) * 1000
                        OpenRouterTelemetryTracker.get_instance().record_request(
                            self.model_name, self.question, "", latency, False
                        )
                        self.finished.emit("No response text received from OpenRouter API.", False)
                else:
                    res_body = response.read().decode("utf-8")
                    data = json.loads(res_body)
                    choices = data.get("choices", [])
                    if choices:
                        reply_text = choices[0].get("message", {}).get("content", "").strip()
                        latency = (time.time() - req_start_time) * 1000
                        OpenRouterTelemetryTracker.get_instance().record_request(
                            self.model_name, self.question, reply_text, latency, True
                        )
                        self.finished.emit(reply_text, True)
                    else:
                        latency = (time.time() - req_start_time) * 1000
                        OpenRouterTelemetryTracker.get_instance().record_request(
                            self.model_name, self.question, "", latency, False
                        )
                        self.finished.emit("No response received from OpenRouter API.", False)

        except urllib.error.HTTPError as http_err:
            try:
                err_detail = http_err.read().decode("utf-8")
                err_json = json.loads(err_detail)
                msg = err_json.get("error", {}).get("message", str(http_err))
            except Exception:
                msg = str(http_err)
            logger.error("OpenRouter HTTP error: %s", msg)
            OpenRouterTelemetryTracker.get_instance().record_request(
                self.model_name, self.question, "", 1000.0, False
            )
            self.finished.emit(f"OpenRouter Error ({http_err.code}): {msg}", False)

        except Exception as e:
            logger.error("OpenRouter request error: %s", e)
            OpenRouterTelemetryTracker.get_instance().record_request(
                self.model_name, self.question, "", 1000.0, False
            )
            self.finished.emit(f"Connection error: {str(e)}", False)
