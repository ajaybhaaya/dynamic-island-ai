# Windows 11 Desktop "Dynamic Island" AI Companion & Neural Workspace (v4.0)

<p align="center">
  <a href="https://github.com/ajaybhaaya/dynamic-island-ai/releases/latest/download/DynamicIsland.exe">
    <img src="https://img.shields.io/badge/⚡_Direct_Download-DynamicIsland.exe_(Standalone_x64)-B83B24?style=for-the-badge&logo=windows&logoColor=white" alt="Download Dynamic Island">
  </a>
  <a href="https://github.com/ajaybhaaya/dynamic-island-ai/releases/latest">
    <img src="https://img.shields.io/badge/📦_GitHub_Releases-v1.0.0-4A6B5D?style=for-the-badge&logo=github&logoColor=white" alt="Releases">
  </a>
  <img src="https://img.shields.io/badge/Platform-Windows_11_%2F_10_(64--bit)-1D4ED8?style=for-the-badge&logo=windows11" alt="Platform">
  <img src="https://img.shields.io/badge/GPU_Required-NONE_(CPU_60_FPS)-22C55E?style=for-the-badge" alt="CPU Only">
</p>

A standalone, lightweight, frameless desktop overlay application for **Windows 11** inspired by the organic, atmospheric aesthetic of the illustrated reference artwork (`stand out` misty forest & terracotta landscape). Features an expressive procedural AI companion in a pitch-black obsidian container, direct OpenRouter multimodal intelligence, a 7-page productivity carousel, and **Neural Workspace Expansion ("Extend" Mode)** with grounded charcoal tethers and terracotta anchor nodes.

Optimized strictly for a **CPU-only Windows 11 environment** (16GB RAM, no dedicated GPU required). Custom `QPainter` drawing, fluid dual-sine liquid sphere gauges, floating misty nodes, and static Bezier neural tethers run at a buttery-smooth **60 FPS** (`16ms` frame tick) with lightweight desktop compositing and 0% idle CPU overhead.

---

## 🚀 3 Quick Ways to Download & Run

Choose the option that best fits your workflow:

### Option 1: 1-Click Standalone Executable (Recommended for Classmates & Users)
> **No Python, terminal, or command-line experience required!**
1. Download **[`DynamicIsland.exe`](https://github.com/ajaybhaaya/dynamic-island-ai/releases/latest/download/DynamicIsland.exe)** directly from the latest GitHub Release.
2. Double-click `DynamicIsland.exe` to run immediately!
   * *Protection & Privacy:* The code is pre-compiled into an encrypted binary archive. Zero raw code lines or API keys are exposed.
   * *Offline Ready:* Hardware Telemetry, Liquid Gauges, Live Network Sparkline, File Shelf, Focus Studio, Quick Notepad, and App Launchers work 100% locally with zero setup!

---

### Option 2: 1-Line PowerShell Command (Automatic Install & Launch)
Open Windows PowerShell and paste this single command:
```powershell
irm https://raw.githubusercontent.com/ajaybhaaya/dynamic-island-ai/main/install.ps1 | iex
```
*(This automatically clones into `dynamic-island-ai`, ensures Python is installed, installs dependencies, and launches the app!)*

---

### Option 3: Clone from GitHub & Run with 1-Click `run.bat`
If you prefer cloning the source code:
```powershell
git clone https://github.com/ajaybhaaya/dynamic-island-ai.git
cd dynamic-island-ai
.\run.bat
```
*(You can also simply double-click **`run.bat`** in Windows File Explorer!)*

> [!TIP]
> **Why did `cd windows_dynamic_island` or `pip install` fail previously?**
> 1. **Folder Name:** When cloning from GitHub, the folder is named **`dynamic-island-ai`**, so run `cd dynamic-island-ai`.
> 2. **Windows PATH:** On many Windows systems, `pip.exe` lives inside Python's `Scripts\` directory which is omitted from Windows PATH by default. Using **`python -m pip install -r requirements.txt`** (or simply using **`run.bat`**) automatically invokes the pip module through Python, eliminating the *"pip is not recognized"* error completely!

---

## 🔑 Setting Up Your OpenRouter API Key (Optional)

The app works **100% offline** without any API key for hardware monitoring, network speeds, recent files, timers, notepad, and app windows.

To enable **Screen Vision (Tab 1)** and **AI Assistant Chat (Tab 5)**:
1. Copy [`.env.example`](file:///.env.example) to `.env`:
   ```powershell
   copy .env.example .env
   ```
2. Open `.env` in Notepad and insert your key:
   ```env
   OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
   ```
3. Alternatively, set a Windows environment variable:
   ```powershell
   [System.Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "your-key", "User")
   ```
*(Your API key is excluded by `.gitignore` and is never committed or leaked).*

---

## 🎨 Misty Sage & Terracotta Design System & Unified Color Palette

Strictly extracted from the reference artwork:
* **Atmospheric Vertical Gradient (Main Capsule & Floating Windows):**
  * **Top Stop (`0.0`):** Muted Sage-Teal Mist (`#9CAFAA`)
  * **Middle Stop (`0.55`):** Soft Desaturated Fog Cream-Green (`#CBD2C4`)
  * **Bottom Stop (`1.0`):** Warm Dry-Grass Sand (`#D6CEB8`)
* **Recessed Wells / Inner Plates:** Deep Forest Pine Slate (`#5E6F68`, `rgba(94, 111, 104, 0.22)`) and Warm Parchment (`#EAE6DA` / `#FAF8F2`) with subtle `1.2px` borders in `#7A8B84`.
* **Primary CTA Accent:** Rich Terracotta Rust (`#B83B24`) hovering to Warm Burnt Sienna (`#D15238`), pressed `#962D1A`.
* **Micro-Accents:**
  * Warm Amber-Peach (`#E88D5A`): CPU telemetry fluid & prompt token metrics.
  * Mahogany Bark (`#6E2214`): Border outlines & shadows.
  * Forest Sage (`#4A6B5D`): Cache telemetry fluid & operational status badges.
* **AI Bot Avatar Module (`avatar_widget.py`):** Strictly **100% Pitch-Black (`#050507`)** with glowing white/cyan eyes (`#FFFFFF` / `#38BDF8`) and all 5 emotional triggers (`IDLE`, `SCARED`, `HAPPY`, `NERVOUS`, `SAD`) fully preserved.
* **Typography:**
  * **Display Headers:** Heavy Chalk White (`#FFFFFF`, `Segoe UI Variable Display` Bold/Black 800) with subtle dark drop-shadow.
  * **Navigation Pills:** Wide-Tracked Uppercase (`letter-spacing: 1.8px`, 700 weight).
  * **Body Copy:** Deep Charcoal-Pine (`#2B3531`) with high readability on Warm Parchment cards.
* **Neural Tethers:** Static solid Deep Charcoal/Black (`#141816`, `2.2px` stroke) connectors accented with Terracotta Rust (`#B83B24`) terminal nodes (`6px` diameter / `3.0px` radius) at both connection endpoints (Dynamic Island bottom anchor & window top-center anchors). 0% idle CPU polling.

---

## 7 Distinct Feature Tabs & Capabilities

The dynamic island houses **7 dedicated, swipeable and clickable pages**:

1. **Tab 1: AI Companion & OpenRouter Screen Vision**
   * Live procedural AI companion inside pitch-black 66x66 pod with dual glowing eyes and cursor gaze tracking.
   * **OpenRouter Vision Analysis:** `mss` screen capture downscaled to max 1280px, encoded to base64 JPEG, and streamed live via OpenRouter multimodal models (`Claude 3.5 Sonnet`, `GPT-4o`).
   * **Conversational Follow-Up:** 1-click `💬 CHAT` routing to Tab 5, retaining desktop vision context for follow-up questions.

2. **Tab 2: Media Center & Playback Control**
   * Deep Pine-Slate Plate (`#3E4A45`) with Chalk White display title and Fog Cream subtitle.
   * Terracotta animated audio equalizer bars.
   * High-contrast playback controls: **Previous**, **Play/Pause**, and **Next** using native Windows Media session virtual keys (`VK_MEDIA_*`).

3. **Tab 3: Hardware Telemetry & Live Network Latency Strip**
   * Triple **standalone spherical liquid gauges (58px diameter)** displaying **RAM %** (Terracotta Rust `#B83B24`), **CPU %** (Warm Amber-Peach `#E88D5A`), and **CACHE / Memory Available** (Forest Sage `#4A6B5D`) using live `psutil` sampling.
   * **Dual-sine wave fluid animation** with smooth float lerp (`diff * 0.15`) at 60 FPS.
   * Oversized Chalk White (`#FFFFFF`) display readouts with soft shadow for crisp readability against any liquid fill level.
   * **Recessed Live Network & Latency Strip Card (`net_strip`):**
     * **Left:** Live Download (`↓`) and Upload (`↑`) rates formatted with smart compact tabular numbers (`0K`, `420K`, `12.4M`), plus TCP handshake ping (`ms`) with connection health dot (`#22C55E` < 70ms, `#E88D5A` 70–160ms, `#B83B24` > 160ms/offline) and session peak download speed.
     * **Center:** 30-point rolling **`NetworkSparkline`** painted with smooth Terracotta (`#B83B24`) download curve and soft alpha gradient fill, paired with Pine Sage (`#4A6B5D`) upload curve.
     * **Right Controls:**
       * **`[NET / API]` Toggle:** Switch live TCP handshake latency checks between `1.1.1.1` (general web) and `openrouter.ai` (AI API endpoint).
       * **`[👁 / ✕]` Pill Ticker Toggle:** Toggle visibility of the live network ticker in the collapsed pill on/off on demand.

4. **Tab 4: Interactive Document Shelf (File Chips & Drop-Well)**
   * Drag and drop files from Windows Explorer onto the recessed pine drop-well (`rgba(94, 111, 104, 0.20)`).
   * **Clean FileChip Design:** Pill-shaped Warm Parchment chips (`#EAE6DA` fill, `1.2px` `#7A8B84` border, `16px` radius) with hover highlight.
   * **Dynamic File Iconography:** Left-aligned standard application badges (Red PDF badge, Blue Word DOCX badge, Green Excel XLSX badge, Orange PPTX badge, Cyan Code badge, or system icon provider).
   * **Truncated Typography:** Primary filename rendered in bold Charcoal (`#2B3531`), truncated with an ellipsis if exceeding `136px`.
   * **Native 1-Click Launching:** Clicking anywhere on the chip immediately opens the document in its default associated Windows application (`os.startfile`).
   * **Automatic 4-File FIFO Shelf:** Maintains up to 4 recent files in a balanced 2x2 grid; dropping a 5th file automatically evicts the oldest entry.

5. **Tab 5: Quick AI Assistant (Direct OpenRouter Chat)**
   * Clean, direct AI chat interface. Ask any question on any topic.
   * Model badge: `GPT-4O-MINI` in Chalk White; `Screen Aware` badge in Forest Sage.
   * Connected directly to **OpenRouter API** (`openai/gpt-4o-mini`).
   * Instant responses rendered in Warm Parchment cards with one-click clipboard copying.

6. **Tab 6: Focus & Productivity Studio (Pomodoro / Study & Meeting Timer)**
   * Dedicated focus and countdown timer for students studying, teachers timing quizzes/lectures, or professionals in sprint sessions.
   * Oversized Chalk White `25:00` display in Deep Pine-Slate plate (`#3E4A45`).
   * Presets: **25M FOCUS**, **50M DEEP**, **5M SHORT**, **15M LONG**.
   * Interactive **Sprint Task Checklist**: add items, toggle checkmarks, and delete completed tasks.

7. **Tab 7: Neural Workspace Expansion ("Extend" Mode & Dynamic 3-to-6 Tabs)**
   * Prominent Terracotta CTA button: **`⚡  EXTEND WORKSPACE`** (`260x38px`).
   * **Quick Notepad (`NP`) Fully Preserved in Extension Workspace:**
     * The dedicated, distraction-free **Quick Notepad (`NP`)** floating window remains anchored as Node 1 in the spawned Neural Workspace (`310x412px`, with word/char counters, timestamp insertion, auto-save to `workspace_np_notes.txt`, and clear/copy controls).
   * **Tactile `[+]` Expand Symbol Next to Every Extension Tab:**
     * A dedicated `[+]` button is positioned right next to **every single extension tab** (`NP`, `AI`, `DASH`, etc.) in Page 7, as well as on the header of each floating window.
     * Clicking any `[+]` button dynamically expands the workspace tabs from 3 up to **6 tabs** (`APP 4`, `APP 5`, `APP 6`).
     * Maximum limit of 6 extension tabs is strictly enforced, disabling `+` buttons with a helpful tooltip when the limit is reached.
     * Extra tabs can be closed individually with the `×` button, automatically re-indexing remaining tabs.
   * **Universal App Drag-and-Drop & Command Launcher:**
     * Custom extension windows (`CustomAppNodeWindow`) can host **any application**:
       * **Drag & Drop:** Drop `.exe` binaries, `.lnk` Windows shortcuts, scripts, or files directly into the window.
       * **Command / Name Typing:** Type any application command (`calc`, `notepad`, `cmd`, `mspaint`, or web URLs) into the search bar and press Enter or `⚡ OPEN`.
       * **Quick Chips:** Instant 1-click launchers for `[🔢 Calc]`, `[📝 Notepad]`, `[💻 Terminal]`, `[🎨 Paint]`, and `[🌐 Web]`.
   * **Pixel-Perfect Window Calibration:**
     * Automatically strips heavy OS title bars and thick window borders (`WS_CAPTION`, `WS_THICKFRAME`) using the Win32 API.
     * Embeds external processes seamlessly into the window's zero-margin container via `createWindowContainer(QWindow.fromWinId(hwnd))`.
     * Real-time calibration on window resize using `MoveWindow` keeps the app perfectly fitted inside the window.

---

## ⚡ Collapsed Pill Live Network Ticker (`network_worker.py`)

In its compact, collapsed pill state (`264x54px`), the Dynamic Island displays a live, non-blocking telemetry readout to the right of the Pitch-Black AI Bot avatar:
* **Top Micro-Row:** Monospace throughput readout in fixed-width tabular numerals (`Consolas`, `9.5px Bold`): `↓ 4.2M  ↑ 180K` (zero horizontal layout jitter).
* **Bottom Micro-Row:** Anti-aliased 6px connection health dot + TCP latency (`28ms`) + status subtitle (`• AI Online`).
  * `< 70ms` (Healthy): Crisp Forest Sage Green (`#22C55E`)
  * `70ms – 160ms` (Moderate): Warm Amber (`#E88D5A`)
  * `> 160ms` or Disconnected (`--ms`): Terracotta Rust (`#B83B24`) with `OFFLINE` status.
* **Non-Blocking Architecture:** Background `NetworkMonitorWorker(QThread)` computes `psutil` delta rates every 1.0s and real TCP port 443 handshakes every 3.0s without console flashes.
* **Toggleable Visibility:** Can be shown/hidden directly via the `[👁]` button in Tab 3.

---

## 🔒 Security & Privacy Commitments

1. **Zero Secret Leakage:** The application strictly sources OpenRouter API credentials from local `.env` files or system environment variables. No keys or tokens are ever embedded in binaries, commits, or git history.
2. **Encrypted Standalone Executable:** The downloadable `DynamicIsland.exe` bundles all Python bytecodes into a compiled CArchive format, preventing plaintext source code modification while running cleanly on any Windows 11 machine without external runtime dependencies.
3. **Local Privacy:** Document drop shelves, notes, and scratchpad entries remain 100% on the local filesystem (`%USERPROFILE%` / local folder) and are never uploaded to any cloud service.
