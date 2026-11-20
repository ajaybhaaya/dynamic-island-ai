# Windows 11 Desktop "Dynamic Island" AI Companion & Neural Workspace (v4.0)

<p align="center">
  <a href="https://github.com/ajaybhaaya/dynamic-island-ai/releases/latest/download/DynamicIsland-Windows-x64-Portable.zip">
    <img src="https://img.shields.io/badge/⚡_Download_Portable_Zip-Windows_x64-B83B24?style=for-the-badge&logo=windows&logoColor=white" alt="Download Dynamic Island Portable Zip">
  </a>
  <a href="https://github.com/ajaybhaaya/dynamic-island-ai/releases/latest/download/DynamicIsland.exe">
    <img src="https://img.shields.io/badge/Standalone_EXE-DynamicIsland.exe-2B3531?style=for-the-badge&logo=windows11&logoColor=white" alt="Download Single EXE">
  </a>
  <a href="https://github.com/ajaybhaaya/dynamic-island-ai/releases/latest">
    <img src="https://img.shields.io/badge/📦_All_Releases-v1.0.0-4A6B5D?style=for-the-badge&logo=github&logoColor=white" alt="Releases">
  </a>
  <img src="https://img.shields.io/badge/GPU_Required-NONE_(CPU_60_FPS)-22C55E?style=for-the-badge" alt="CPU Only">
</p>

A standalone, lightweight, frameless desktop overlay application for **Windows 11** inspired by the organic, atmospheric aesthetic of the illustrated reference artwork (`stand out` misty forest & terracotta landscape). Features an expressive procedural AI companion in a pitch-black obsidian container, direct OpenRouter multimodal intelligence, a 7-page productivity carousel, and **Neural Workspace Expansion ("Extend" Mode)** with grounded charcoal tethers and terracotta anchor nodes.

Optimized strictly for a **CPU-only Windows 11 environment** (16GB RAM, no dedicated GPU required). Custom `QPainter` drawing, fluid dual-sine liquid sphere gauges, floating misty nodes, and static Bezier neural tethers run at a buttery-smooth **60 FPS** (`16ms` frame tick) with lightweight desktop compositing and 0% idle CPU overhead.

---

## 🚀 3 Simple Ways to Download & Run

Choose the option that fits your setup:

### Option 1: 1-Click Portable Download (Recommended for Classmates & Users)
> **No Python, terminal, or command prompt required!**
1. Download **[`DynamicIsland-Windows-x64-Portable.zip`](https://github.com/ajaybhaaya/dynamic-island-ai/releases/latest/download/DynamicIsland-Windows-x64-Portable.zip)** (or the single [**`DynamicIsland.exe`**](https://github.com/ajaybhaaya/dynamic-island-ai/releases/latest/download/DynamicIsland.exe)).
2. Extract the ZIP folder anywhere (e.g. your Desktop or Downloads).
3. Inside the folder, double-click **`START.bat`** (or `DynamicIsland.exe`)!
4. *(Optional)* Double-click **`Create_Desktop_Shortcut.bat`** to instantly add Dynamic Island to your **Windows Start Menu** and **Desktop**.

> [!NOTE]
> **Windows Defender SmartScreen Notice:**
> Because this is a fresh open-source release without a commercial Microsoft EV certificate, Windows Defender SmartScreen may display a blue dialog (*"Windows protected your PC"*).
> **To run:** Click **"More info"** $\rightarrow$ Click **"Run anyway"**.
> The application runs completely in user mode, requires zero admin privileges, and contains 0 telemetry spyware.

---

### Option 2: 1-Line PowerShell Command (Automatic Setup)
Open **PowerShell** (press `Win + X` $\rightarrow$ `Terminal` or `PowerShell`) and paste:
```powershell
irm https://raw.githubusercontent.com/ajaybhaaya/dynamic-island-ai/main/install.ps1 | iex
```
*(This automatically downloads the repo, verifies Python & dependencies, pins the shortcut to your Windows Start Menu, and starts the app!)*

---

### Option 3: Clone from GitHub & Run with `START.bat`
If you want to view and edit the Python source code directly:
```powershell
git clone https://github.com/ajaybhaaya/dynamic-island-ai.git
cd dynamic-island-ai
.\START.bat
```
*(You can also simply double-click **`START.bat`** or **`run.bat`** in Windows File Explorer!)*

> [!TIP]
> **Troubleshooting common Windows errors:**
> * **`Cannot find path 'windows_dynamic_island'`:** The repository is cloned as `dynamic-island-ai`. Run `cd dynamic-island-ai`.
> * **`pip : The term 'pip' is not recognized`:** On Windows, `pip.exe` lives in Python's `Scripts\` folder which is omitted from Windows PATH by default. Running **`.\START.bat`** or **`python -m pip install -r requirements.txt`** solves this automatically!

---

## 🔑 OpenRouter AI Vision & Chat Setup (Optional)

The entire application runs **100% offline** without any API key for:
* Hardware Monitoring (RAM %, CPU %, Cache fluid gauges)
* Live Network Sparkline & TCP Ping Ticker
* Recent Document Shelf with 1-click execution chips
* Focus Studio & Sprint Timer
* Distraction-free Quick Notepad (`NP`)
* Universal App Windows (`calc`, `notepad`, `cmd`, etc.)

To activate **Screen Vision (Tab 1)** and **AI Assistant Chat (Tab 5)**:
1. Copy [`.env.example`](file:///.env.example) to `.env`:
   ```powershell
   copy .env.example .env
   ```
2. Open `.env` in Notepad and insert your key:
   ```env
   OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
   ```
3. Alternatively, set a Windows user environment variable:
   ```powershell
   [System.Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "your-key", "User")
   ```
*(Your API key is never committed or published).*

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
   * **Recessed Live Network & Latency Strip Card (`net_strip`):**
     * **Left:** Live Download (`↓`) and Upload (`↑`) rates formatted with compact tabular numbers, plus TCP handshake ping (`ms`) with connection health dot and session peak download speed.
     * **Center:** 30-point rolling **`NetworkSparkline`** painted with smooth Terracotta (`#B83B24`) download curve and Pine Sage (`#4A6B5D`) upload curve.
     * **Right Controls:** Toggle ping target host (`1.1.1.1` vs `openrouter.ai`) and toggle collapsed pill ticker visibility.

4. **Tab 4: Interactive Document Shelf (File Chips & Drop-Well)**
   * Drag and drop files from Windows Explorer onto the recessed pine drop-well.
   * **Clean FileChip Design:** Pill-shaped Warm Parchment chips (`#EAE6DA` fill, `1.2px` `#7A8B84` border, `16px` radius).
   * **Dynamic File Iconography:** Left-aligned standard application badges (PDF, Word, Excel, PPTX, Code, or system icon).
   * **Native 1-Click Launching:** Clicking anywhere on the chip opens the document in its default Windows app (`os.startfile`).
   * **FIFO Shelf:** Maintains up to 4 recent files in a balanced 2x2 grid.

5. **Tab 5: Quick AI Assistant (Direct OpenRouter Chat)**
   * Clean, direct AI chat interface. Connected to **OpenRouter API** (`openai/gpt-4o-mini`).
   * Instant responses rendered in Warm Parchment cards with one-click clipboard copying.

6. **Tab 6: Focus & Productivity Studio (Pomodoro / Study & Meeting Timer)**
   * Oversized Chalk White `25:00` display with presets: **25M FOCUS**, **50M DEEP**, **5M SHORT**, **15M LONG**.
   * Interactive **Sprint Task Checklist**: add items, toggle checkmarks, and delete completed tasks.

7. **Tab 7: Neural Workspace Expansion ("Extend" Mode & Dynamic 3-to-6 Tabs)**
   * Prominent Terracotta CTA button: **`⚡ EXTEND WORKSPACE`** (`260x38px`).
   * **Quick Notepad (`NP`):** Distraction-free floating notepad with real-time stats and auto-save.
   * **Tactile `[+]` Expand Symbol Next to Every Extension Tab:** Dynamically expands workspace tabs from 3 up to **6 tabs** (`APP 4`, `APP 5`, `APP 6`).
   * **Universal App Host:** Host any Windows application (`calc`, `notepad`, `cmd`, etc.) inside calibrated workspace windows with 1-click launcher chips.

---

## ⚡ Collapsed Pill Live Network Ticker

In its compact pill state (`264x54px`), the Dynamic Island displays a live, non-blocking telemetry readout to the right of the Pitch-Black AI Bot avatar:
* **Top Micro-Row:** Fixed-width throughput: `↓ 4.2M  ↑ 180K` (zero horizontal jitter).
* **Bottom Micro-Row:** Anti-aliased 6px connection health dot + TCP latency (`28ms`) + status subtitle (`• AI Online`).

---

## 🔒 Security & Privacy Commitments

1. **Zero Secret Leakage:** The application strictly sources OpenRouter API credentials from local `.env` files or system environment variables. No keys or tokens are ever embedded in binaries, commits, or git history.
2. **Encrypted Standalone Executable:** The downloadable `DynamicIsland.exe` bundles all Python bytecodes into a compiled CArchive format, preventing plaintext source code modification while running cleanly on any Windows 11 machine without external runtime dependencies.
3. **Local Privacy:** Document drop shelves, notes, and scratchpad entries remain 100% on the local filesystem (`%USERPROFILE%` / local folder) and are never uploaded to any cloud service.
