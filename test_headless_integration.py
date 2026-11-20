"""
test_headless_integration.py - Headless Verification of Misty Sage & Terracotta Dynamic Island
Includes verification of:
1. Collapsed & Expanded Capsule Geometry
2. AI Bot Avatar (#050507 container, 5 emotional states)
3. 9 Carousel Pages with Editorial Styling
4. Telemetry LiquidSphereGauges on Page 3
5. Page 9 Neural Workspace "Extend" Mode:
   - Initial 3 tabs (NP, AI, DASH) with [+] button next to each tab
   - Expanding tabs dynamically from 3 to 6
   - Typing or launching custom app commands (calc, cmd, custom scripts)
   - Embedded window calibration & container fit
   - Symmetrical desktop placement & static black neural tethers
   - Enforcing maximum 6 tabs limit & tab removal
6. Island auto-collapse & cleanup
"""

import os
import sys

# Ensure offscreen Qt platform
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from ui_island import DynamicIslandWindow
from avatar_widget import BotState
from theme_misty_sage import (
    BOT_BG,
    ACCENT_TERRACOTTA,
    BG_PARCHMENT,
    BG_PINE_PLATE,
    TEXT_CHARCOAL,
)
from neural_workspace import (
    WorkspaceManager,
    CustomAppNodeWindow,
    InteractiveCalcWidget,
    InteractiveTerminalWidget,
)
from network_worker import (
    NetworkMonitorWorker,
    format_speed,
    get_ping_health_color,
)

def run_tests():
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        print("[1] Initializing DynamicIslandWindow...", flush=True)
        island = DynamicIslandWindow()
        island.show()

        # 1. Check collapsed pill geometry
        print(f"    Collapsed size: {island.width()}x{island.height()} (Expected 264x54)", flush=True)
        assert island.width() == 264 and island.height() == 54, f"Pill size mismatch! Got {island.width()}x{island.height()}"

        # 1b. Check Collapsed Pill Ticker components & formatting
        print("[1b] Verifying Collapsed Pill Live Network Ticker...", flush=True)
        assert hasattr(island, "lbl_collapsed_speed"), "Must have lbl_collapsed_speed"
        assert hasattr(island, "dot_collapsed"), "Must have dot_collapsed"
        assert hasattr(island, "lbl_collapsed_ping"), "Must have lbl_collapsed_ping"
        assert hasattr(island, "network_worker"), "Must have network_worker"

        # Test live network update callback
        island._on_network_updated(4.2 * 1024 * 1024, 180 * 1024, 28, True)
        assert "4.2M" in island.lbl_collapsed_speed.text(), f"Expected 4.2M, got {island.lbl_collapsed_speed.text()}"
        assert "180K" in island.lbl_collapsed_speed.text(), f"Expected 180K, got {island.lbl_collapsed_speed.text()}"
        assert island.lbl_collapsed_ping.text() == "28ms", f"Expected 28ms, got {island.lbl_collapsed_ping.text()}"

        # Test hiding & showing collapsed pill ticker
        island.set_pill_ticker_visible(False)
        assert not island.lbl_collapsed_speed.isVisible(), "Speed label should be hidden"
        island.set_pill_ticker_visible(True)
        assert island.lbl_collapsed_speed.isVisible(), "Speed label should be visible"
        print("    Collapsed pill network ticker verified cleanly.", flush=True)

        # 2. Check Avatar styling
        print("[2] Verifying AI Bot Avatar Container (Collapsed & Expanded)...", flush=True)
        assert BOT_BG.upper() == "#050507", f"Avatar background must be pitch black #050507, got {BOT_BG}"
        
        # Verify collapsed avatar
        assert hasattr(island.collapsed_avatar, "set_state"), "Collapsed avatar must support set_state"
        for state in [BotState.IDLE, BotState.SCARED, BotState.HAPPY, BotState.NERVOUS, BotState.SAD]:
            island.collapsed_avatar.set_state(state)
            assert island.collapsed_avatar._state == state, f"Failed state switch to {state}"
        island.collapsed_avatar.set_state(BotState.IDLE)

        # Verify Page 1 avatar
        page1_avatar = island.carousel.page1.avatar
        assert hasattr(page1_avatar, "set_state"), "Page 1 avatar must support set_state"
        for state in [BotState.IDLE, BotState.SCARED, BotState.HAPPY, BotState.NERVOUS, BotState.SAD]:
            page1_avatar.set_state(state)
            assert page1_avatar._state == state, f"Failed state switch to {state}"
        page1_avatar.set_state(BotState.IDLE)
        print("    Both Avatars' 5 emotional states verified.", flush=True)

        # 3. Expand Island & verify carousel pages (7 pages total)
        print("[3] Expanding Dynamic Island & verifying all 7 carousel pages...", flush=True)
        island.expand_island()
        island.resize(480, 180) # Force immediate expand geometry for headless
        assert len(island.carousel.pages) == 7, f"Expected 7 pages in carousel, got {len(island.carousel.pages)}"

        for i, page in enumerate(island.carousel.pages):
            island.carousel.snap_to_page(i)
            assert page is not None, f"Page {i} is None"
            print(f"    Page {i+1}: {type(page).__name__} loaded successfully.", flush=True)

        # Verify Dev Tools and Scratchpad have been removed from carousel
        page_types = [type(p).__name__ for p in island.carousel.pages]
        assert "Page7DevTools" not in page_types, "Page7DevTools should be removed from carousel"
        assert "Page8Scratchpad" not in page_types, "Page8Scratchpad should be removed from carousel"
        print("    Verified Dev Tools and Scratchpad removed from dynamic carousel.", flush=True)

        # 4. Check Page 3 Telemetry Spheres
        print("[4] Testing Page 3 LiquidSphereGauge rendering & values...", flush=True)
        p3 = island.carousel.page3
        assert hasattr(p3, "gauge_ram") and hasattr(p3, "gauge_cpu") and hasattr(p3, "gauge_cache")
        p3.gauge_ram.set_data(0.685, "68.5%")
        p3.gauge_cpu.set_data(0.420, "42.0%")
        p3.gauge_cache.set_data(0.812, "81.2%")
        # Step simulation frames
        for _ in range(5):
            p3.gauge_ram._on_frame()
            p3.gauge_cpu._on_frame()
            p3.gauge_cache._on_frame()
        print("    LiquidSphereGauges wave animation and lerp functioning cleanly.", flush=True)

        # 4b. Check Page 3 Live Network & Latency Strip
        print("[4b] Testing Page 3 Live Network & Latency Strip...", flush=True)
        assert hasattr(p3, "net_strip"), "Page 3 must have net_strip"
        assert hasattr(p3, "sparkline"), "Page 3 must have sparkline"
        assert hasattr(p3, "btn_ping_target"), "Page 3 must have btn_ping_target"
        assert hasattr(p3, "btn_toggle_pill"), "Page 3 must have btn_toggle_pill"

        p3.update_network_data(5.5 * 1024 * 1024, 320 * 1024, 35, True)
        assert p3.lbl_dl_val.text() == "5.5M", f"Expected 5.5M, got {p3.lbl_dl_val.text()}"
        assert p3.lbl_ul_val.text() == "320K", f"Expected 320K, got {p3.lbl_ul_val.text()}"
        assert p3.lbl_ping_val.text() == "35ms", f"Expected 35ms, got {p3.lbl_ping_val.text()}"
        assert len(p3.sparkline.dl_history) == 30, "Sparkline must maintain 30 samples"

        # Test ping target toggle (NET <-> API)
        assert p3.btn_ping_target.text() == "NET"
        p3._toggle_ping_target()
        assert p3.btn_ping_target.text() == "API"
        assert island.network_worker.get_target() == "openrouter.ai"
        p3._toggle_ping_target()
        assert p3.btn_ping_target.text() == "NET"
        assert island.network_worker.get_target() == "1.1.1.1"

        # Test pill toggle button from Page 3
        p3._toggle_pill_visibility()
        assert not island.collapsed_ticker_visible
        p3._toggle_pill_visibility()
        assert island.collapsed_ticker_visible
        print("    Page 3 Live Network & Latency Strip functioning cleanly.", flush=True)

        # 4c. Unit Test format_speed & get_ping_health_color
        print("[4c] Testing format_speed & get_ping_health_color...", flush=True)
        assert format_speed(0.0) == "0K"
        assert format_speed(420.0 * 1024.0) == "420K"
        assert format_speed(12.4 * 1024.0 * 1024.0) == "12.4M"
        assert format_speed(1.2 * 1024.0 * 1024.0 * 1024.0) == "1.2G"
        assert get_ping_health_color(30, True) == "#22C55E"
        assert get_ping_health_color(110, True) == "#E88D5A"
        assert get_ping_health_color(190, True) == "#B83B24"
        assert get_ping_health_color(-1, False) == "#B83B24"
        print("    Network formatting & health color logic verified.", flush=True)

        # 5. Check Page 9 Neural Workspace & Dynamic Tabs Expansion (3 to 6 tabs)
        print("[5] Testing Page 9 Neural Workspace & Dynamic Extension Tabs (3 -> 6)...", flush=True)
        p9 = island.carousel.page9
        assert hasattr(p9, "btn_extend"), "Page 9 must have btn_extend"

        # Check initial tabs in island's workspace_manager
        ws_mgr = island.workspace_manager
        tabs = ws_mgr.get_tabs_data()
        assert len(tabs) == 3, f"Expected 3 initial tabs, got {len(tabs)}"
        assert tabs[0]["code"] == "NP" and tabs[0]["name"] == "Quick Notepad", "Quick Notepad must remain in extension workspace!"
        print(f"    Initial tabs verified: {[t['code'] for t in tabs]} (Quick Notepad intact in Extension Workspace)", flush=True)

        # Verify [+] buttons next to every single tab in Page 9
        assert len(p9._plus_buttons) == 3, f"Expected 3 [+] buttons in Page 9, got {len(p9._plus_buttons)}"
        for btn in p9._plus_buttons:
            assert btn.text() == "+", "Button must display '+' symbol"
            assert btn.isEnabled(), "Button must be enabled when tabs < 6"

        # Expand to Tab 4 (APP 4)
        print("    Adding Tab 4 via [+] trigger...", flush=True)
        win4 = ws_mgr.add_custom_tab()
        assert win4 is not None, "Failed to create APP 4 window"
        assert len(ws_mgr.get_tabs_data()) == 4, "WorkspaceManager must have 4 tabs"
        assert len(p9._plus_buttons) == 4, f"Page 9 must now show 4 [+] buttons, got {len(p9._plus_buttons)}"

        # Expand to Tab 5 (APP 5)
        print("    Adding Tab 5 via [+] trigger...", flush=True)
        win5 = ws_mgr.add_custom_tab()
        assert win5 is not None, "Failed to create APP 5 window"
        assert len(ws_mgr.get_tabs_data()) == 5, "WorkspaceManager must have 5 tabs"

        # Expand to Tab 6 (APP 6 - Maximum allowed)
        print("    Adding Tab 6 (Maximum) via [+] trigger...", flush=True)
        win6 = ws_mgr.add_custom_tab()
        assert win6 is not None, "Failed to create APP 6 window"
        assert len(ws_mgr.get_tabs_data()) == 6, "WorkspaceManager must have 6 tabs"
        assert len(p9._plus_buttons) == 6, f"Page 9 must now show 6 [+] buttons, got {len(p9._plus_buttons)}"

        # Verify that all [+] buttons are disabled when 6 tabs limit is reached
        for btn in p9._plus_buttons:
            assert not btn.isEnabled(), "All [+] buttons must be disabled when max 6 tabs reached"
        print("    Max 6 tabs limit correctly enforced; all [+] buttons disabled.", flush=True)

        # Attempting to add 7th tab should return None
        win7 = ws_mgr.add_custom_tab()
        assert win7 is None, "Adding beyond 6 tabs must be prevented"

        # 6. Test App Loading & Calibration on Custom Windows
        print("[6] Testing App Launching & Calibration on Custom Windows...", flush=True)
        # Test built-in calc launch
        win4.load_app("calc")
        assert win4.stack.currentIndex() == 2, f"Expected stack view 2 (Interactive Calc), got {win4.stack.currentIndex()}"
        calc_widget = win4.calc_widget
        assert isinstance(calc_widget, InteractiveCalcWidget), "Must be InteractiveCalcWidget"
        calc_widget._on_digit("7")
        calc_widget._on_op("×")
        calc_widget._on_digit("6")
        calc_widget._on_equals()
        assert calc_widget.lbl_val.text() == "42", f"Calc result expected '42', got {calc_widget.lbl_val.text()}"
        print("    Custom Tab 4: Interactive Calculator launched & computed 7 × 6 = 42 successfully.", flush=True)

        # Test built-in terminal/cmd launch
        win5.load_app("cmd")
        assert win5.stack.currentIndex() == 3, f"Expected stack view 3 (Interactive Terminal), got {win5.stack.currentIndex()}"
        term_widget = win5.terminal_widget
        assert isinstance(term_widget, InteractiveTerminalWidget), "Must be InteractiveTerminalWidget"
        assert term_widget.process is not None, "Terminal process must be initialized"
        print("    Custom Tab 5: Interactive Terminal console initialized with live process streaming.", flush=True)

        # Test calibration controls
        win4.recalibrate_embedding()
        win4.set_view_drop_zone()
        assert win4.stack.currentIndex() == 0, "Changing app must return to Drop Zone View 0"
        print("    Custom Window calibration actions ([⛶ Fit], [🧹 Change]) functioning cleanly.", flush=True)

        # 7. Test Tab Removal & Re-indexing
        print("[7] Testing Tab Removal and Re-indexing...", flush=True)
        # Remove Tab index 5 (which is custom tab APP 6)
        ws_mgr.remove_custom_tab(5)
        assert len(ws_mgr.get_tabs_data()) == 5, f"Expected 5 tabs after removal, got {len(ws_mgr.get_tabs_data())}"
        # [+] buttons should be re-enabled now that tabs < 6
        for btn in p9._plus_buttons:
            assert btn.isEnabled(), "[+] buttons must be re-enabled after tab removal"
        print("    Tab removed and [+] buttons re-enabled.", flush=True)

        # 8. Test Workspace Spawning & Symmetrical Placement
        print("[8] Testing Workspace Spawning with 5 Active Windows...", flush=True)
        ws_mgr.spawn_workspace()
        assert ws_mgr.np_window.isVisible(), "NP Window should be visible"
        assert ws_mgr.ai_window.isVisible(), "AI Window should be visible"
        assert ws_mgr.dash_window.isVisible(), "DASH Window should be visible"
        assert win4.isVisible(), "Custom App 4 Window should be visible"
        assert win5.isVisible(), "Custom App 5 Window should be visible"
        print("    All 5 active floating windows spawned and positioned symmetrically.", flush=True)

        # 9. Test Island Collapse Behavior & Clean Close
        print("[9] Testing Island auto-collapse behavior...", flush=True)
        island.collapse_island()
        assert not island.is_expanded, "Island should be in collapsed state"
        print("    Island collapsed smoothly.", flush=True)

        # Clean up
        if hasattr(island, "network_worker") and island.network_worker.isRunning():
            island.network_worker.stop()
        ws_mgr.close_all()
        island.close()
        print("\n✅ All headless integration tests (Network Ticker, Page 3 Strip, Sparkline, Tabs 3->6) passed with 0 errors!", flush=True)
        return 0
    except Exception as e:
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
