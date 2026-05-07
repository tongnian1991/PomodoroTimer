#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pomodoro Timer — 桌面番茄钟
A feature-rich Pomodoro technique timer built with Python tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import json
import winsound
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────────────────────

CONFIG_FILE = Path.home() / ".pomodoro_config.json"
DEFAULT_CONFIG = {
    "work_duration": 25 * 60,
    "short_break": 5 * 60,
    "long_break": 15 * 60,
    "long_break_interval": 4,
    "auto_start_break": False,
    "auto_start_work": False,
    "sound_enabled": True,
    "always_on_top": False,
    "theme": "sakura",
}

THEMES = {
    "sakura": {
        "bg": "#FFF0F5",
        "fg": "#4A2C3A",
        "accent": "#E87A9B",
        "accent2": "#F4B4C2",
        "timer_bg": "#FFE4EC",
        "btn_bg": "#E87A9B",
        "btn_fg": "white",
        "btn_hover": "#D46A8A",
        "progress": "#E87A9B",
        "progress_bg": "#FFD6E0",
        "status": "#9B6B7E",
        "counter": "#C0808F",
        "font_family": "Microsoft YaHei",
        "flip_bg": "#FFF5F8",
        "flip_fg": "#4A2C3A",
        "flip_border": "#E8C8D4",
    },
    "ocean": {
        "bg": "#EFF6FF",
        "fg": "#1E3A5F",
        "accent": "#4A90D9",
        "accent2": "#A8C8F0",
        "timer_bg": "#E3EFFA",
        "btn_bg": "#4A90D9",
        "btn_fg": "white",
        "btn_hover": "#3A7BC8",
        "progress": "#4A90D9",
        "progress_bg": "#C8DFF5",
        "status": "#5A7A9A",
        "counter": "#7A9ABA",
        "font_family": "Microsoft YaHei",
        "flip_bg": "#F0F6FF",
        "flip_fg": "#1E3A5F",
        "flip_border": "#C8D8E8",
    },
    "forest": {
        "bg": "#F0F7F0",
        "fg": "#2D4A2D",
        "accent": "#5A9E5A",
        "accent2": "#A8D8A8",
        "timer_bg": "#E8F3E8",
        "btn_bg": "#5A9E5A",
        "btn_fg": "white",
        "btn_hover": "#4A8E4A",
        "progress": "#5A9E5A",
        "progress_bg": "#C8E8C8",
        "status": "#5A7A5A",
        "counter": "#7AAA7A",
        "font_family": "Microsoft YaHei",
        "flip_bg": "#F0F7F0",
        "flip_fg": "#2D4A2D",
        "flip_border": "#C8E0C8",
    },
    "sunset": {
        "bg": "#FFF5EE",
        "fg": "#4A3020",
        "accent": "#E87A3A",
        "accent2": "#F4B890",
        "timer_bg": "#FFEDE0",
        "btn_bg": "#E87A3A",
        "btn_fg": "white",
        "btn_hover": "#D06A2A",
        "progress": "#E87A3A",
        "progress_bg": "#FAD8C0",
        "status": "#9A7050",
        "counter": "#C09070",
        "font_family": "Microsoft YaHei",
        "flip_bg": "#FFF5EE",
        "flip_fg": "#4A3020",
        "flip_border": "#E8D0C0",
    },
    "midnight": {
        "bg": "#1A1A2E",
        "fg": "#E0E0E0",
        "accent": "#E94560",
        "accent2": "#2D2D44",
        "timer_bg": "#16213E",
        "btn_bg": "#E94560",
        "btn_fg": "white",
        "btn_hover": "#D13550",
        "progress": "#E94560",
        "progress_bg": "#2D2D44",
        "status": "#8899AA",
        "counter": "#8899AA",
        "font_family": "Microsoft YaHei",
        "flip_bg": "#0D0D1A",
        "flip_fg": "#E0E0E0",
        "flip_border": "#2D2D44",
    },
}


# ─── Application ─────────────────────────────────────────────────────────────

class PomodoroTimer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pomodoro Timer")
        self.root.geometry("480x620")
        self.root.minsize(420, 560)

        # Load config
        self.config = self._load_config()
        self.theme = THEMES[self.config["theme"]]

        # State
        self.mode = "work"  # work | short_break | long_break
        self.time_left = self.config["work_duration"]
        self.is_running = False
        self.is_paused = False
        self.pomodoros_done = self._load_today_count()
        self.update_job = None
        self._start_time = 0
        self._pause_remaining = 0

        # Icon data (window icon from base64)
        self._set_window_icon()

        # Build UI
        self._build_ui()
        self._apply_theme()
        self._update_display()
        self._center_window()

        # Window protocol
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind("<space>", lambda e: self.toggle())
        self.root.bind("<Escape>", lambda e: self.reset())
        self.root.bind("<Control-h>", lambda e: self._show_help())

        self.root.mainloop()

    # ── Config ───────────────────────────────────────────────────────────────

    def _load_config(self):
        if CONFIG_FILE.exists():
            try:
                saved = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                merged = DEFAULT_CONFIG.copy()
                merged.update(saved)
                return merged
            except Exception:
                pass
        return DEFAULT_CONFIG.copy()

    def _save_config(self):
        CONFIG_FILE.write_text(
            json.dumps(self.config, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _load_today_count(self):
        today = time.strftime("%Y-%m-%d")
        data_file = Path.home() / ".pomodoro_data.json"
        try:
            if data_file.exists():
                data = json.loads(data_file.read_text(encoding="utf-8"))
                return data.get(today, 0)
        except Exception:
            pass
        return 0

    # ── Icon ─────────────────────────────────────────────────────────────────

    def _set_window_icon(self):
        """Set a simple embedded icon using a tiny PhotoImage."""
        try:
            # 16x16 tomato icon as XBM bitmap
            icon_data = """
#define icon_width 16
#define icon_height 16
static unsigned char icon_bits[] = {
    0x00, 0x00, 0x80, 0x01, 0xC0, 0x03, 0xE0, 0x07,
    0xF0, 0x0F, 0xF8, 0x1F, 0xFC, 0x3F, 0xFC, 0x3F,
    0xFC, 0x3F, 0xFC, 0x3F, 0xF8, 0x1F, 0xF0, 0x0F,
    0xE0, 0x07, 0xC0, 0x03, 0x00, 0x00, 0x00, 0x00,
};
"""
            from tkinter import BitmapImage
            img = BitmapImage(data=icon_data)
            self.root.iconphoto(True, img)
        except Exception:
            pass

    # ── UI Build ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        T = self.theme
        self.root.configure(bg=T["bg"])

        # ── Top bar: title + theme selector ──
        top_frame = tk.Frame(self.root, bg=T["bg"])
        top_frame.pack(fill="x", padx=20, pady=(15, 0))

        title = tk.Label(top_frame, text="🍅 番茄钟", font=(T["font_family"], 16, "bold"),
                         bg=T["bg"], fg=T["fg"])
        title.pack(side="left")

        self.theme_var = tk.StringVar(value=self.config["theme"])
        theme_menu = ttk.Combobox(top_frame, textvariable=self.theme_var,
                                  values=list(THEMES.keys()), state="readonly",
                                  width=10, font=(T["font_family"], 10))
        theme_menu.pack(side="right")
        theme_menu.bind("<<ComboboxSelected>>", self._change_theme)

        # ── Status bar ──
        self.status_label = tk.Label(self.root, text="准备开始", font=(T["font_family"], 11),
                                     bg=T["bg"], fg=T["status"])
        self.status_label.pack(pady=(10, 0))

        # ── Timer display ──
        self.timer_frame = tk.Frame(self.root, bg=T["timer_bg"],
                                    highlightbackground=T["accent2"],
                                    highlightthickness=2)
        self.timer_frame.pack(padx=40, pady=10, fill="both", expand=True)

        # ── Flip clock canvas ──
        self.flip_canvas = tk.Canvas(self.timer_frame, width=380, height=210,
                                     bg=T["timer_bg"], highlightthickness=0)
        self.flip_canvas.pack(expand=True)

        self._build_flip_cards(T)

        # ── Count info ──
        self.count_frame = tk.Frame(self.root, bg=T["bg"])
        self.count_frame.pack(pady=(5, 10))

        self.count_label = tk.Label(self.count_frame, text=f"今日完成: {self.pomodoros_done} 个番茄",
                                    font=(T["font_family"], 11),
                                    bg=T["bg"], fg=T["counter"])
        self.count_label.pack()

        # ── Buttons ──
        btn_frame = tk.Frame(self.root, bg=T["bg"])
        btn_frame.pack(pady=10)

        btn_style = {"font": (T["font_family"], 12, "bold"), "relief": "flat",
                      "bd": 0, "cursor": "hand2", "width": 8, "height": 1}

        self.start_btn = self._make_btn(btn_frame, "▶ 开始", T["btn_bg"], T["btn_fg"],
                                        self.toggle, **btn_style)
        self.start_btn.pack(side="left", padx=5)

        self.reset_btn = self._make_btn(btn_frame, "↺ 重置", T["accent2"], T["fg"],
                                        self.reset, **btn_style)
        self.reset_btn.pack(side="left", padx=5)

        # ── Mode quick-switch ──
        mode_frame = tk.Frame(self.root, bg=T["bg"])
        mode_frame.pack(pady=(5, 5))

        mode_btn_style = {"font": (T["font_family"], 10), "relief": "flat",
                          "bd": 0, "cursor": "hand2", "width": 10}

        self.work_btn = self._make_btn(mode_frame, "🍅 工作", T["btn_bg"], T["btn_fg"],
                                        lambda: self.switch_mode("work"), **mode_btn_style)
        self.work_btn.pack(side="left", padx=3)

        self.short_btn = self._make_btn(mode_frame, "🌿 短休", T["accent2"], T["fg"],
                                         lambda: self.switch_mode("short_break"), **mode_btn_style)
        self.short_btn.pack(side="left", padx=3)

        self.long_btn = self._make_btn(mode_frame, "🌳 长休", T["accent2"], T["fg"],
                                        lambda: self.switch_mode("long_break"), **mode_btn_style)
        self.long_btn.pack(side="left", padx=3)

        # ── Settings button ──
        bottom_frame = tk.Frame(self.root, bg=T["bg"])
        bottom_frame.pack(fill="x", padx=20, pady=(5, 15))

        # Gear button for settings
        self.settings_btn = self._make_btn(bottom_frame, "⚙", T["bg"], T["status"],
                                            self._show_settings,
                                            font=(T["font_family"], 16), relief="flat",
                                            bd=0, cursor="hand2", width=2)
        self.settings_btn.pack(side="right", padx=(0, 5))

        self.stats_btn = self._make_btn(bottom_frame, "📊", T["bg"], T["status"],
                                         self._show_stats,
                                         font=(T["font_family"], 14), relief="flat",
                                         bd=0, cursor="hand2", width=2)
        self.stats_btn.pack(side="right", padx=(0, 5))

        self.help_btn = self._make_btn(bottom_frame, "⌨  快捷键 | ⚙ 设置",
                                       T["bg"], T["status"], self._show_help,
                                       font=(T["font_family"], 9), relief="flat",
                                       bd=0, cursor="hand2", anchor="w")
        self.help_btn.pack(side="left", fill="x", expand=True)

    def _make_btn(self, parent, text, bg, fg, command, **kwargs):
        btn = tk.Button(parent, text=text, bg=bg, fg=fg, command=command, **kwargs)
        return btn

    # ── Flip Clock ──────────────────────────────────────────────────────────

    def _build_flip_cards(self, T):
        """Draw flip-clock-style digit panels on self.flip_canvas."""
        cw, ch = 380, 210
        self.flip_canvas.delete("all")

        card_w, card_h, gap = 68, 140, 5
        colon_w = 14
        total_w = 4 * card_w + 2 * gap + colon_w + 2 * gap
        start_x = (cw - total_w) // 2
        start_y = (ch - card_h) // 2 - 4

        self._flip_digits = []
        x = start_x

        for i in range(4):
            if i == 2:
                cx = x + colon_w // 2
                cy = start_y + card_h // 2
                self.flip_canvas.create_text(
                    cx, cy,
                    text=":", font=(T["font_family"], 36, "bold"),
                    fill=T["flip_fg"], anchor="center",
                    tags="flip_colon"
                )
                x += colon_w + gap

            self.flip_canvas.create_rectangle(
                x, start_y, x + card_w, start_y + card_h,
                fill=T["flip_bg"], outline=T["flip_border"],
                width=2, tags=f"card{i}_bg"
            )
            mid_y = start_y + card_h // 2
            self.flip_canvas.create_line(
                x + 8, mid_y, x + card_w - 8, mid_y,
                fill=T["flip_border"], width=2, tags=f"card{i}_seam"
            )
            tid = self.flip_canvas.create_text(
                x + card_w // 2, start_y + card_h // 4,
                text="8", font=(T["font_family"], 42, "bold"),
                fill=T["flip_fg"], anchor="center",
                tags=f"card{i}_top"
            )
            bid = self.flip_canvas.create_text(
                x + card_w // 2, start_y + 3 * card_h // 4,
                text="8", font=(T["font_family"], 42, "bold"),
                fill=T["flip_fg"], anchor="center",
                tags=f"card{i}_btm"
            )
            self._flip_digits.extend([tid, bid])
            x += card_w + gap

        # Mode label below flip cards
        self._flip_mode_text = self.flip_canvas.create_text(
            cw // 2, start_y + card_h + 20,
            text="准备开始", font=(T["font_family"], 12),
            fill=T["status"], anchor="center",
            tags="flip_mode"
        )

    # ── Theme ────────────────────────────────────────────────────────────────

    def _apply_theme(self):
        T = self.theme
        self.root.configure(bg=T["bg"])
        for widget in [self.timer_frame, self.count_frame]:
            widget.configure(bg=T["bg"])
        self.timer_frame.configure(bg=T["timer_bg"],
                                    highlightbackground=T["accent2"])
        self.flip_canvas.configure(bg=T["timer_bg"])
        self._build_flip_cards(T)
        self.status_label.configure(bg=T["bg"], fg=T["status"])
        self.count_label.configure(bg=T["bg"], fg=T["counter"])
        self._update_display()

        # Update button colors
        self.start_btn.configure(bg=T["btn_bg"], fg=T["btn_fg"])
        self.reset_btn.configure(bg=T["accent2"], fg=T["fg"])

        # Mode buttons
        self.work_btn.configure(bg=T["btn_bg"], fg=T["btn_fg"])
        self.short_btn.configure(bg=T["accent2"], fg=T["fg"])
        self.long_btn.configure(bg=T["accent2"], fg=T["fg"])

        self.help_btn.configure(bg=T["bg"], fg=T["status"])
        self.settings_btn.configure(bg=T["bg"], fg=T["status"])
        self.stats_btn.configure(bg=T["bg"], fg=T["status"])

        # ── Rebind hover effects using current theme colors ──
        hover_map = [
            (self.start_btn, T["btn_bg"], T["btn_hover"]),
            (self.reset_btn, T["accent2"], T.get("btn_hover", T["accent2"])),
            (self.work_btn, T["btn_bg"], T["btn_hover"]),
            (self.short_btn, T["accent2"], T.get("btn_hover", T["accent2"])),
            (self.long_btn, T["accent2"], T.get("btn_hover", T["accent2"])),
            (self.help_btn, T["bg"], T["bg"]),
            (self.settings_btn, T["bg"], T["bg"]),
            (self.stats_btn, T["bg"], T["bg"]),
        ]
        for btn, nbg, hbg in hover_map:
            btn.configure(bg=nbg)
            btn.unbind("<Enter>")
            btn.unbind("<Leave>")
            btn.bind("<Enter>", lambda e, b=btn, h=hbg: b.configure(bg=h))
            btn.bind("<Leave>", lambda e, b=btn, n=nbg: b.configure(bg=n))

    def _change_theme(self, event=None):
        name = self.theme_var.get()
        if name in THEMES:
            self.config["theme"] = name
            self.theme = THEMES[name]
            self._apply_theme()
            self._save_config()

    # ── Timer Logic ──────────────────────────────────────────────────────────

    def _get_mode_duration(self):
        return {
            "work": self.config["work_duration"],
            "short_break": self.config["short_break"],
            "long_break": self.config["long_break"],
        }[self.mode]

    def _get_mode_label(self):
        return {
            "work": "专注工作",
            "short_break": "短时休息",
            "long_break": "长时休息",
        }[self.mode]

    def switch_mode(self, mode):
        if self.is_running:
            return
        self.mode = mode
        self.time_left = self._get_mode_duration()
        self.is_paused = False
        self._update_display()
        self.status_label.configure(text={
            "work": "点击 ▶ 开始专注",
            "short_break": "休息一下吧 🌿",
            "long_break": "辛苦了，多休息会儿 🌳",
        }[mode])
        self._highlight_mode_btn()

    def _highlight_mode_btn(self):
        T = self.theme
        btns = {
            "work": self.work_btn,
            "short_break": self.short_btn,
            "long_break": self.long_btn,
        }
        for mode, btn in btns.items():
            if mode == self.mode:
                btn.configure(bg=T["btn_bg"], fg=T["btn_fg"])
            else:
                btn.configure(bg=T["accent2"], fg=T["fg"])

    def toggle(self):
        if self.is_running and not self.is_paused:
            self.pause()
        else:
            self.start()

    def start(self):
        if self.is_running and not self.is_paused:
            return
        if self.is_paused:
            self.is_paused = False
            self.is_running = True
            self._start_time = time.time()
            self.start_btn.configure(text="⏸ 暂停")
            self.status_label.configure(text="进行中...")
            self._tick()
            return

        if self.time_left <= 0:
            self.reset()

        self.is_running = True
        self.is_paused = False
        self._start_time = time.time()
        self._pause_remaining = self.time_left
        self.start_btn.configure(text="⏸ 暂停")
        self.status_label.configure(text="进行中...")
        self._tick()

    def pause(self):
        if not self.is_running:
            return
        self._pause_remaining = self.time_left
        self.is_paused = True
        self.is_running = False
        if self.update_job:
            self.root.after_cancel(self.update_job)
            self.update_job = None
        self.start_btn.configure(text="▶ 继续")
        self.status_label.configure(text="已暂停")

    def reset(self):
        self.is_running = False
        self.is_paused = False
        if self.update_job:
            self.root.after_cancel(self.update_job)
            self.update_job = None
        self.time_left = self._get_mode_duration()
        self._update_display()
        self.start_btn.configure(text="▶ 开始")
        self.status_label.configure(text="已重置")

    def _tick(self):
        if not self.is_running or self.is_paused:
            return

        elapsed = time.time() - self._start_time
        self.time_left = max(0, int(self._pause_remaining - elapsed))
        self._update_display()

        if self.time_left <= 0:
            self._on_timer_end()
            return

        # Align next tick to the next second boundary to minimize drift
        now = time.time()
        next_sec = int(now) + 1
        delay = max(50, int((next_sec - now) * 1000))
        self.update_job = self.root.after(delay, self._tick)

    def _on_timer_end(self):
        self.is_running = False
        self.start_btn.configure(text="▶ 开始")

        if self.config["sound_enabled"]:
            self._play_alarm()

        if self.mode == "work":
            self.pomodoros_done += 1
            self.count_label.configure(text=f"今日完成: {self.pomodoros_done} 个番茄")
            self._save_daily_count()

            # Flash window
            self._flash_window("🎉 专注完成！")

            # Auto-switch to break
            if self.pomodoros_done % self.config["long_break_interval"] == 0:
                next_mode = "long_break"
            else:
                next_mode = "short_break"

            if self.config["auto_start_break"]:
                self.switch_mode(next_mode)
                self.start()
            else:
                self.switch_mode(next_mode)
                self.status_label.configure(text={
                    "short_break": "专注完成! 点击 ▶ 开始休息 🌿",
                    "long_break": "专注完成! 点击 ▶ 开始长休 🌳",
                }[next_mode])
        else:
            self._flash_window("☕ 休息结束！")
            if self.config["auto_start_work"]:
                self.switch_mode("work")
                self.start()
            else:
                self.switch_mode("work")
                self.status_label.configure(text="休息结束! 点击 ▶ 开始专注")

    def _play_alarm(self):
        """Play notification sound."""
        try:
            # Windows beep
            for freq in [880, 1100, 880, 1100]:
                winsound.Beep(freq, 150)
        except Exception:
            try:
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            except Exception:
                pass

    def _flash_window(self, message):
        """Show a top-level notification window."""
        top = tk.Toplevel(self.root)
        top.title("Pomodoro")
        top.geometry("300x120")
        top.configure(bg=self.theme["bg"])

        # Center on parent
        x = self.root.winfo_x() + (self.root.winfo_width() - 300) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 120) // 2
        top.geometry(f"+{x}+{y}")

        top.attributes("-topmost", True)

        tk.Label(top, text=message, font=(self.theme["font_family"], 18, "bold"),
                 bg=self.theme["bg"], fg=self.theme["accent"]).pack(expand=True)

        top.after(2000, top.destroy)

    # ── Display ──────────────────────────────────────────────────────────────

    def _update_display(self):
        mins = self.time_left // 60
        secs = self.time_left % 60
        digits = f"{mins:02d}{secs:02d}"

        for i, d in enumerate(digits):
            if self._flip_digits and i * 2 + 1 < len(self._flip_digits):
                self.flip_canvas.itemconfig(self._flip_digits[i * 2], text=d)
                self.flip_canvas.itemconfig(self._flip_digits[i * 2 + 1], text=d)

        self.flip_canvas.itemconfig(self._flip_mode_text, text=self._get_mode_label())

        # Window title
        if self.is_running:
            title = f"🍅 {mins:02d}:{secs:02d} - Pomodoro"
        else:
            title = "🍅 Pomodoro Timer"
        self.root.title(title)

    # ── Persistence ──────────────────────────────────────────────────────────

    def _save_daily_count(self):
        today = time.strftime("%Y-%m-%d")
        data_file = Path.home() / ".pomodoro_data.json"
        try:
            if data_file.exists():
                data = json.loads(data_file.read_text(encoding="utf-8"))
            else:
                data = {}
            data[today] = self.pomodoros_done
            # Keep only last 90 days
            keys = sorted(data.keys(), reverse=True)[:90]
            data = {k: data[k] for k in keys}
            data_file.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                                  encoding="utf-8")
        except Exception:
            pass

    # ── Help ─────────────────────────────────────────────────────────────────

    def _show_help(self):
        msg = (
            "🍅 番茄钟使用说明\n\n"
            "快捷键:\n"
            "  Space  — 开始/暂停\n"
            "  Esc    — 重置计时器\n"
            "  Ctrl+H — 帮助\n"
            "  ⚙ 按钮 — 设置(自定义时长、主题等)\n"
            "  📊 按钮 — 历史统计\n\n"
            "工作周期:\n"
            f"  工作 {self.config['work_duration']//60}分 → 短休 {self.config['short_break']//60}分\n"
            f"  每 {self.config['long_break_interval']} 个番茄 → 长休 {self.config['long_break']//60}分\n\n"
            "番茄工作法建议:\n"
            "  1. 确定任务\n"
            "  2. 专注 25 分钟\n"
            "  3. 休息 5 分钟\n"
            "  4. 重复 4 轮后长休"
        )
        messagebox.showinfo("🍅 帮助", msg)

    # ── Settings Dialog ──────────────────────────────────────────────────────

    def _show_settings(self):
        if hasattr(self, "_settings_win") and self._settings_win.winfo_exists():
            self._settings_win.lift()
            return

        win = tk.Toplevel(self.root)
        win.title("⚙ 设置")
        win.geometry("400x450")
        win.configure(bg=self.theme["bg"])
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        self._settings_win = win

        x = self.root.winfo_x() + (self.root.winfo_width() - 400) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 450) // 2
        win.geometry(f"+{x}+{y}")

        T = self.theme

        # ── Flip-style time pickers ──

        def make_flip_row(parent, label, min_val, max_val, initial, suffix=""):
            """A row with up/down arrows flanking a numeric display (翻页模式)."""
            frame = tk.Frame(parent, bg=T["bg"])
            frame.pack(fill="x", padx=25, pady=3)

            tk.Label(frame, text=label, font=(T["font_family"], 10),
                     bg=T["bg"], fg=T["fg"]).pack(side="left")

            var = tk.IntVar(value=initial)

            def up(event=None):
                if var.get() < max_val:
                    var.set(var.get() + 1)

            def down(event=None):
                if var.get() > min_val:
                    var.set(var.get() - 1)

            right = tk.Frame(frame, bg=T["bg"])
            right.pack(side="right")

            # ── flip card: ▲ number ▼ ──
            up_lbl = tk.Label(right, text="▲", bg=T["accent2"], fg=T["fg"],
                              font=(T["font_family"], 12, "bold"), cursor="hand2",
                              padx=4, pady=0)
            up_lbl.pack(side="left")
            up_lbl.bind("<Button-1>", up)
            up_lbl.bind("<Enter>", lambda e: up_lbl.configure(bg=T.get("btn_hover", T["accent2"])))
            up_lbl.bind("<Leave>", lambda e: up_lbl.configure(bg=T["accent2"]))

            num_lbl = tk.Label(right, textvariable=var, bg="white", fg=T["fg"],
                               font=(T["font_family"], 16, "bold"),
                               width=3, relief="solid", bd=1, anchor="center")
            num_lbl.pack(side="left", padx=2)

            dn_lbl = tk.Label(right, text="▼", bg=T["accent2"], fg=T["fg"],
                              font=(T["font_family"], 12, "bold"), cursor="hand2",
                              padx=4, pady=0)
            dn_lbl.pack(side="left")
            dn_lbl.bind("<Button-1>", down)
            dn_lbl.bind("<Enter>", lambda e: dn_lbl.configure(bg=T.get("btn_hover", T["accent2"])))
            dn_lbl.bind("<Leave>", lambda e: dn_lbl.configure(bg=T["accent2"]))

            if suffix:
                tk.Label(right, text=suffix, font=(T["font_family"], 10),
                         bg=T["bg"], fg=T["status"]).pack(side="left", padx=(5, 0))

            return var

        self._settings_vars = {}
        self._settings_vars["work"] = make_flip_row(win, "🍅 专注时间", 1, 120, self.config["work_duration"] // 60, "分钟")
        self._settings_vars["short"] = make_flip_row(win, "🌿 短休息", 1, 60, self.config["short_break"] // 60, "分钟")
        self._settings_vars["long"] = make_flip_row(win, "🌳 长休息", 1, 120, self.config["long_break"] // 60, "分钟")

        # Long break interval
        self._settings_vars["interval"] = make_flip_row(win, "🔁 长休间隔", 1, 10, self.config["long_break_interval"], "个番茄后")

        # Separator
        ttk.Separator(win, orient="horizontal").pack(fill="x", padx=25, pady=10)

        # Options
        tk.Label(win, text="🎛 其他选项", font=(T["font_family"], 13, "bold"),
                 bg=T["bg"], fg=T["fg"]).pack(anchor="w", padx=25, pady=(0, 5))

        self._settings_vars["auto_break"] = tk.BooleanVar(value=self.config["auto_start_break"])
        cb1 = tk.Checkbutton(win, text="专注结束后自动开始休息",
                             variable=self._settings_vars["auto_break"],
                             font=(T["font_family"], 10),
                             bg=T["bg"], fg=T["fg"],
                             selectcolor=T["timer_bg"], activebackground=T["bg"])
        cb1.pack(anchor="w", padx=25, pady=2)

        self._settings_vars["auto_work"] = tk.BooleanVar(value=self.config["auto_start_work"])
        cb2 = tk.Checkbutton(win, text="休息结束后自动开始专注",
                             variable=self._settings_vars["auto_work"],
                             font=(T["font_family"], 10),
                             bg=T["bg"], fg=T["fg"],
                             selectcolor=T["timer_bg"], activebackground=T["bg"])
        cb2.pack(anchor="w", padx=25, pady=2)

        self._settings_vars["sound"] = tk.BooleanVar(value=self.config["sound_enabled"])
        cb3 = tk.Checkbutton(win, text="启用提示音",
                             variable=self._settings_vars["sound"],
                             font=(T["font_family"], 10),
                             bg=T["bg"], fg=T["fg"],
                             selectcolor=T["timer_bg"], activebackground=T["bg"])
        cb3.pack(anchor="w", padx=25, pady=2)

        self._settings_vars["ontop"] = tk.BooleanVar(value=self.config["always_on_top"])
        cb4 = tk.Checkbutton(win, text="窗口置顶",
                             variable=self._settings_vars["ontop"],
                             font=(T["font_family"], 10),
                             bg=T["bg"], fg=T["fg"],
                             selectcolor=T["timer_bg"], activebackground=T["bg"])
        cb4.pack(anchor="w", padx=25, pady=2)

        # Save button
        btn_frame = tk.Frame(win, bg=T["bg"])
        btn_frame.pack(pady=15)

        def save_settings():
            self.config["work_duration"] = self._settings_vars["work"].get() * 60
            self.config["short_break"] = self._settings_vars["short"].get() * 60
            self.config["long_break"] = self._settings_vars["long"].get() * 60
            self.config["long_break_interval"] = self._settings_vars["interval"].get()
            self.config["auto_start_break"] = self._settings_vars["auto_break"].get()
            self.config["auto_start_work"] = self._settings_vars["auto_work"].get()
            self.config["sound_enabled"] = self._settings_vars["sound"].get()
            self.config["always_on_top"] = self._settings_vars["ontop"].get()
            self.root.attributes("-topmost", self.config["always_on_top"])
            self._save_config()
            # Reset current mode with new duration
            self.time_left = self._get_mode_duration()
            self._update_display()
            win.destroy()

        tk.Button(btn_frame, text="✓ 保存", command=save_settings,
                  font=(T["font_family"], 11, "bold"),
                  bg=T["btn_bg"], fg=T["btn_fg"],
                  relief="flat", bd=0, cursor="hand2", padx=20, pady=4).pack()

    # ── Statistics ───────────────────────────────────────────────────────────

    def _show_stats(self):
        if hasattr(self, "_stats_win") and self._stats_win.winfo_exists():
            self._stats_win.lift()
            return

        win = tk.Toplevel(self.root)
        win.title("📊 统计")
        win.geometry("380x400")
        win.configure(bg=self.theme["bg"])
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        self._stats_win = win

        x = self.root.winfo_x() + (self.root.winfo_width() - 380) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 400) // 2
        win.geometry(f"+{x}+{y}")

        T = self.theme

        # Load data
        data_file = Path.home() / ".pomodoro_data.json"
        data = {}
        if data_file.exists():
            try:
                data = json.loads(data_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        today = time.strftime("%Y-%m-%d")
        today_count = data.get(today, 0)
        total = sum(data.values())
        week_total = sum(v for k, v in data.items()
                         if k >= time.strftime("%Y-%m-%d",
                           time.localtime(time.time() - 7 * 86400)))
        # Active days (last 30)
        active_days = sum(1 for k, v in data.items()
                          if k >= time.strftime("%Y-%m-%d",
                            time.localtime(time.time() - 30 * 86400)) and v > 0)
        # Average per active day (last 30)
        avg = round(total / max(active_days, 1), 1)
        work_mins = self.config["work_duration"] // 60
        total_focus_hours = round(total * work_mins / 60, 1)

        tk.Label(win, text="📊 番茄统计", font=(T["font_family"], 16, "bold"),
                 bg=T["bg"], fg=T["fg"]).pack(pady=(15, 10))

        stats_frame = tk.Frame(win, bg=T["timer_bg"],
                                highlightbackground=T["accent2"],
                                highlightthickness=1)
        stats_frame.pack(padx=30, pady=5, fill="x")

        stats = [
            ("今日完成", f"{today_count} 个🍅"),
            ("本周完成", f"{week_total} 个🍅"),
            ("总计", f"{total} 个🍅"),
            ("专注时长", f"{total_focus_hours} 小时"),
            ("日均 (活跃日)", f"{avg} 个🍅"),
            ("活跃天数 (近30天)", f"{active_days} 天"),
        ]

        for i, (label, value) in enumerate(stats):
            row = tk.Frame(stats_frame, bg=T["timer_bg"])
            row.pack(fill="x", padx=20, pady=6)
            tk.Label(row, text=label, font=(T["font_family"], 11),
                     bg=T["timer_bg"], fg=T["status"]).pack(side="left")
            tk.Label(row, text=value, font=(T["font_family"], 11, "bold"),
                     bg=T["timer_bg"], fg=T["accent"]).pack(side="right")

        # Recent days mini chart
        if data:
            tk.Label(win, text="\n最近记录", font=(T["font_family"], 11),
                     bg=T["bg"], fg=T["status"]).pack()

            recent = sorted(data.items(), reverse=True)[:7]
            recent.reverse()
            chart_frame = tk.Frame(win, bg=T["bg"])
            chart_frame.pack(padx=30, pady=5, fill="x")

            max_count = max(v for _, v in recent) if recent else 1
            for day, count in recent:
                bar = tk.Frame(chart_frame, bg=T["bg"])
                bar.pack(fill="x", pady=1)

                short_day = day[-5:]  # MM-DD
                tk.Label(bar, text=short_day, font=(T["font_family"], 8),
                         bg=T["bg"], fg=T["status"], width=6, anchor="w").pack(side="left")

                w = int((count / max_count) * 150) if max_count > 0 else 0
                if w > 0:
                    tk.Frame(bar, bg=T["accent"], width=w, height=14).pack(side="left", padx=2)
                tk.Label(bar, text=str(count), font=(T["font_family"], 8),
                         bg=T["bg"], fg=T["fg"]).pack(side="left", padx=3)

        tk.Button(win, text="关闭", command=win.destroy,
                  font=(T["font_family"], 10),
                  bg=T["accent2"], fg=T["fg"],
                  relief="flat", bd=0, cursor="hand2", padx=15, pady=3).pack(pady=15)

    def _on_close(self):
        self.root.destroy()

    # ── Window ───────────────────────────────────────────────────────────────

    def _center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"+{x}+{y}")

        if self.config["always_on_top"]:
            self.root.attributes("-topmost", True)


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    PomodoroTimer()
