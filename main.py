import customtkinter as ctk
import pyautogui
import keyboard
import threading
import time
import json
import os
import sys
from datetime import datetime

# Configuration
CONFIG_FILE = "settings.json"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class CobbleAbuserGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Cobble Abuser 9000")
        self.geometry("450x600")
        
        # Set Window Icon
        try:
            icon_p = resource_path("v2.ico")
            if os.path.exists(icon_p):
                self.after(200, lambda: self.iconbitmap(icon_p))
        except:
            pass

        # UI Theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initial Settings
        self.settings = self.load_settings()
        
        self.running = False
        self.paused = True
        self.bot_thread = None
        self.monitor_thread = None
        self.capturing = False
        
        pyautogui.FAILSAFE = True
        self.setup_ui()
        self.bind_hotkey()

    def load_settings(self):
        default_settings = {
            "toggle_key": "z",
            "sell_enabled": True,
            "sell_interval": 1.0,  # in minutes
            "last_used": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return {**default_settings, **json.load(f)}
            except:
                return default_settings
        return default_settings

    def save_settings(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.settings, f, indent=4)

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.title_label = ctk.CTkLabel(self, text="Cobble Abuser 9000", font=("Roboto", 28, "bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 5))
        
        self.subtitle_label = ctk.CTkLabel(self, text="Professional Mining Automation", font=("Roboto", 14), text_color="gray")
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 15))

        # Status Indicator (Top Rightish)
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.grid(row=2, column=0, padx=20, pady=5)
        
        self.status_dot = ctk.CTkLabel(self.status_frame, text="●", font=("Roboto", 18), text_color="red")
        self.status_dot.grid(row=0, column=0, padx=5)
        
        self.status_text = ctk.CTkLabel(self.status_frame, text="Status: STOPPED", font=("Roboto", 16, "bold"))
        self.status_text.grid(row=0, column=1, padx=5)

        # Settings Container (2 Columns)
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.grid(row=3, column=0, padx=20, pady=15, sticky="nsew")
        self.settings_frame.grid_columnconfigure((0, 1), weight=1)

        # Left Column Settings
        # Toggle Key
        key_label = ctk.CTkLabel(self.settings_frame, text="Pause Key:")
        key_label.grid(row=0, column=0, padx=(15, 5), pady=(10, 5), sticky="w")
        self.key_button = ctk.CTkButton(self.settings_frame, text=self.settings["toggle_key"].upper(), width=80, height=28, command=self.start_key_capture)
        self.key_button.grid(row=0, column=1, padx=(5, 15), pady=(10, 5), sticky="e")

        # Sell Toggle
        sell_label = ctk.CTkLabel(self.settings_frame, text="Auto Sell:")
        sell_label.grid(row=1, column=0, padx=(15, 5), pady=5, sticky="w")
        self.sell_switch = ctk.CTkSwitch(self.settings_frame, text="", command=self.on_settings_change)
        if self.settings["sell_enabled"]:
            self.sell_switch.select()
        self.sell_switch.grid(row=1, column=1, padx=(5, 15), pady=5, sticky="e")

        # Interval Setting
        interval_label = ctk.CTkLabel(self.settings_frame, text="Every (min):")
        interval_label.grid(row=2, column=0, padx=(15, 5), pady=(5, 10), sticky="w")
        self.interval_entry = ctk.CTkEntry(self.settings_frame, width=80, height=28)
        self.interval_entry.insert(0, str(self.settings["sell_interval"]))
        self.interval_entry.grid(row=2, column=1, padx=(5, 15), pady=(5, 10), sticky="e")
        self.interval_entry.bind("<KeyRelease>", lambda e: self.on_settings_change())

        # Logs Section
        self.log_textbox = ctk.CTkTextbox(self, height=150, font=("Consolas", 11))
        self.log_textbox.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.log_textbox.configure(state="disabled")

        # Control Section
        self.control_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.control_frame.grid(row=5, column=0, padx=20, pady=(5, 20), sticky="ew")
        self.control_frame.grid_columnconfigure(0, weight=1)

        self.action_button = ctk.CTkButton(self.control_frame, text="START BOT", font=("Roboto", 18, "bold"), height=50, 
                                          fg_color="#2ecc71", hover_color="#27ae60", command=self.toggle_bot)
        self.action_button.grid(row=0, column=0, sticky="ew")

        self.info_label = ctk.CTkLabel(self.control_frame, text=f"Press [{self.settings['toggle_key'].upper()}] to Toggle", font=("Roboto", 11), text_color="gray")
        self.info_label.grid(row=1, column=0, pady=(5, 0))

    def start_key_capture(self):
        self.key_button.configure(text="...", state="disabled")
        threading.Thread(target=self.capture_key, daemon=True).start()

    def capture_key(self):
        self.capturing = True
        event = keyboard.read_event(suppress=True)
        if event.event_type == "down":
            key = event.name
            self.settings["toggle_key"] = key
            self.save_settings()
            self.after(0, self.update_key_ui)
        self.capturing = False

    def bind_hotkey(self):
        # We use a separate thread to monitor the key to avoid modifier issues (like CTRL being held)
        if self.monitor_thread and self.monitor_thread.is_alive():
            return
        self.monitor_thread = threading.Thread(target=self.hotkey_monitor, daemon=True)
        self.monitor_thread.start()

    def add_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.after(0, self._append_log, formatted_message)

    def _append_log(self, text):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", text)
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def on_settings_change(self):
        self.settings["sell_enabled"] = self.sell_switch.get()
        try:
            val = float(self.interval_entry.get())
            if val > 0:
                self.settings["sell_interval"] = val
        except ValueError:
            pass
            
        self.save_settings()
        
        # Update UI state
        if self.sell_switch.get():
            self.interval_entry.configure(state="normal")
        else:
            self.interval_entry.configure(state="disabled")

    def update_key_ui(self):
        self.key_button.configure(text=self.settings["toggle_key"].upper(), state="normal")
        self.info_label.configure(text=f"Press [{self.settings['toggle_key'].upper()}] to Pause/Unpause")

    def hotkey_monitor(self):
        last_state = False
        while True:
            if not self.capturing:
                try:
                    # Check if key is pressed, ignoring modifiers
                    is_pressed = keyboard.is_pressed(self.settings["toggle_key"])
                    if is_pressed and not last_state:
                        # Key just pressed
                        self.after(0, self.toggle_pause)
                    last_state = is_pressed
                except:
                    pass
            time.sleep(0.05)

    def toggle_pause(self):
        if not self.running:
            return
            
        self.paused = not self.paused
        if self.paused:
            self.status_text.configure(text="Status: PAUSED", text_color="orange")
            self.status_dot.configure(text_color="orange")
            self.add_log("Bot paused.")
            self.cleanup_bot()
        else:
            self.status_text.configure(text="Status: RUNNING", text_color="#2ecc71")
            self.status_dot.configure(text_color="#2ecc71")
            self.add_log("Bot unpaused.")

    def toggle_bot(self):
        if self.running:
            self.stop_bot()
        else:
            self.start_bot()

    def start_bot(self):
        if self.running: return # Already running
        
        if self.sell_switch.get():
            try:
                interval = float(self.interval_entry.get())
                if interval <= 0:
                    raise ValueError
                self.settings["sell_interval"] = interval
            except ValueError:
                self.status_text.configure(text="INVALID INTERVAL", text_color="orange")
                return

        self.running = True
        self.paused = True # Start in paused state as requested
        self.status_text.configure(text="Status: WAITING...", text_color="orange")
        self.status_dot.configure(text_color="orange")
        self.action_button.configure(text="STOP BOT", fg_color="#e74c3c", hover_color="#c0392b")
        self.save_settings()
        
        self.add_log(f"Bot active. Press {self.settings['toggle_key'].upper()} to begin.")
        self.bot_thread = threading.Thread(target=self.bot_loop, daemon=True)
        self.bot_thread.start()

    def stop_bot(self):
        if not self.running: return # Already stopped
        self.running = False
        self.paused = True
        self.status_text.configure(text="Status: STOPPED", text_color="#e74c3c")
        self.status_dot.configure(text_color="#e74c3c")
        self.action_button.configure(text="START BOT", fg_color="#2ecc71", hover_color="#27ae60")
        
        # Immediate cleanup
        self.cleanup_bot()


    def cleanup_bot(self):
        pyautogui.mouseUp(button='left')
        pyautogui.keyUp('w')
        pyautogui.keyUp('ctrl')

    def bot_loop(self):
        # Coordinates from engine/abuser.py
        MINING_CAT = [743, 319]
        COBBLE = [851, 321]
        ENCHANTED_COBBLE = [1014, 371]
        SELL = [850, 483]
        CONFIRM = [850, 405]

        start_time = None
        last_sell_time = time.time()
        
        while self.running:
            # Wait if paused
            if self.paused:
                time.sleep(0.1)
                continue
                
            if start_time is None:
                start_time = time.time()
                self.add_log("Mining started.")

            # Start Mining
            pyautogui.keyDown('ctrl')
            pyautogui.keyDown('w')
            pyautogui.mouseDown(button='left')
            
            interval_sec = self.settings["sell_interval"] * 60
            
            # Keep mining until it's time to sell or bot stopped/paused
            while self.running and not self.paused:
                if self.settings["sell_enabled"] and (time.time() - last_sell_time >= interval_sec):
                    break
                time.sleep(0.1)
            
            if not self.running or self.paused:
                self.cleanup_bot()
                if not self.running: break
                continue # Loop back to wait in the paused state
                
            # Stop Mining to Sell
            self.cleanup_bot()
            self.add_log("Executing sell routine...")
            time.sleep(0.5)
            
            # Selling Logic
            pyautogui.press('/')
            pyautogui.typewrite("bz")
            pyautogui.press('enter')
            time.sleep(1.2)
            
            # Clicks
            for loc in [MINING_CAT, COBBLE, ENCHANTED_COBBLE, SELL, CONFIRM]:
                if not self.running or self.paused: break
                pyautogui.click(loc[0], loc[1])
                time.sleep(0.8)
            
            if not self.running or self.paused:
                self.cleanup_bot()
                continue

            pyautogui.press('esc')
            time.sleep(1)
            last_sell_time = time.time()
            self.add_log("Sold items. Resuming...")
            
        if start_time:
            runtime = time.time() - start_time
            self.add_log(f"Session ended. Runtime: {int(runtime//60)}m {int(runtime%60)}s")
        else:
            self.add_log("Session ended (no mining performed).")

if __name__ == "__main__":
    app = CobbleAbuserGUI()
    app.mainloop()
