import os
import re
import threading
import time
from pathlib import Path

import customtkinter
from PIL import Image

try:
    import speech_recognition as sr
except Exception:
    sr = None

try:
    import sounddevice as sd
    import numpy as np
except Exception:
    sd = None
    np = None


customtkinter.set_appearance_mode("Light")
customtkinter.set_default_color_theme("blue")

UI_STYLE = {
    "window_bg": "#EAF6FF",
    "panel_bg": "#FFF7E8",
    "card_bg": "#FFFFFF",
    "title_bg": "#7C4DFF",
    "title_text": "#FFFFFF",
    "subtitle_bg": "#5AC8FA",
    "subtitle_text": "#0B2A4A",
    "timer_bg": "#FF8A65",
    "timer_text": "#FFFFFF",
    "primary_btn": "#FFB74D",
    "primary_btn_hover": "#FFA726",
    "secondary_btn": "#81D4FA",
    "secondary_btn_hover": "#4FC3F7",
    "text_dark": "#1F2D3D",
    "entry_bg": "#FFFDE7",
    "entry_border": "#FFD54F",
}

BASE_DIR = Path(__file__).resolve().parent
LEVEL_DIR = BASE_DIR / "FILES" / "TEST_1000x1000"
DISPLAY_HALF = os.getenv("DISPLAY_HALF", "true").lower() == "true"
MAX_LEVEL = int(os.getenv("MAX_LEVEL", "8")) if os.getenv("MAX_LEVEL", "8").isdigit() else 8


def parse_gender_from_voice(text: str) -> str:
    normalized = text.lower().strip()
    if any(token in normalized for token in ["male", "laki", "pria", "cowok"]):
        return "male"
    if any(token in normalized for token in ["female", "perempuan", "wanita", "cewek"]):
        return "female"
    return ""


def parse_age_from_voice(text: str):
    normalized = text.lower().strip()
    match = re.search(r"\d+", normalized)
    if match:
        return int(match.group(0))

    angka = {
        "nol": 0,
        "satu": 1,
        "dua": 2,
        "tiga": 3,
        "empat": 4,
        "lima": 5,
        "enam": 6,
        "tujuh": 7,
        "delapan": 8,
        "sembilan": 9,
        "sepuluh": 10,
        "sebelas": 11,
        "dua belas": 12,
        "tiga belas": 13,
        "empat belas": 14,
        "lima belas": 15,
        "enam belas": 16,
        "tujuh belas": 17,
        "delapan belas": 18,
        "sembilan belas": 19,
        "dua puluh": 20,
    }
    for word, value in angka.items():
        if word in normalized:
            return value
    return None


class MyTextboxFrame(customtkinter.CTkFrame):
    def __init__(self, master, title: str):
        super().__init__(master, fg_color=UI_STYLE["card_bg"], corner_radius=14, border_width=2, border_color="#D9ECFF")
        self.grid_columnconfigure(0, weight=1)

        self.title = customtkinter.CTkLabel(
            self,
            text=title,
            fg_color=UI_STYLE["title_bg"],
            text_color=UI_STYLE["title_text"],
            font=("Helvetica", 24, "bold"),
            corner_radius=10,
        )
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        self.textbox = customtkinter.CTkTextbox(
            master=self,
            height=48,
            corner_radius=10,
            border_width=2,
            border_color=UI_STYLE["entry_border"],
            fg_color=UI_STYLE["entry_bg"],
            text_color=UI_STYLE["text_dark"],
            font=("Helvetica", 24, "bold"),
        )
        self.textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def get(self) -> str:
        return self.textbox.get("0.0", "end").strip()


class MyRadiobuttonFrame(customtkinter.CTkFrame):
    def __init__(self, master, title: str, values: list[str]):
        super().__init__(master, fg_color=UI_STYLE["card_bg"], corner_radius=14, border_width=2, border_color="#D9ECFF")
        self.grid_columnconfigure(0, weight=1)
        self.variable = customtkinter.StringVar(value="")

        self.title = customtkinter.CTkLabel(
            self,
            text=title,
            fg_color=UI_STYLE["title_bg"],
            text_color=UI_STYLE["title_text"],
            font=("Helvetica", 24, "bold"),
            corner_radius=10,
        )
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        for i, value in enumerate(values):
            customtkinter.CTkRadioButton(
                self,
                text=value,
                value=value,
                variable=self.variable,
                font=("Helvetica", 22, "bold"),
                text_color=UI_STYLE["text_dark"],
                fg_color=UI_STYLE["secondary_btn"],
                hover_color=UI_STYLE["secondary_btn_hover"],
                border_color="#64B5F6",
            ).grid(row=i + 1, column=0, padx=10, pady=8, sticky="w")

    def get(self) -> str:
        return self.variable.get().strip()

    def set(self, value: str):
        self.variable.set(value)


class TextFrame(customtkinter.CTkFrame):
    def __init__(self, master, title: str):
        super().__init__(master, fg_color=UI_STYLE["card_bg"], corner_radius=14, border_width=2, border_color="#CDE7FF")
        self.grid_columnconfigure(0, weight=1)
        self.title = customtkinter.CTkLabel(
            self,
            text=title,
            fg_color=UI_STYLE["subtitle_bg"],
            text_color=UI_STYLE["subtitle_text"],
            font=("Helvetica", 24, "bold"),
            corner_radius=10,
        )
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")


class ImageFrame(customtkinter.CTkFrame):
    def __init__(self, master, title: str):
        super().__init__(master, fg_color=UI_STYLE["card_bg"], corner_radius=14, border_width=2, border_color="#CDE7FF")
        self.grid_columnconfigure(0, weight=1)
        self.title = customtkinter.CTkLabel(
            self,
            text=title,
            fg_color=UI_STYLE["subtitle_bg"],
            text_color=UI_STYLE["subtitle_text"],
            font=("Helvetica", 22, "bold"),
            corner_radius=10,
        )
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")


class InputWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Input Pemain")
        self.geometry("760x620")
        self.configure(fg_color=UI_STYLE["window_bg"])
        self.resizable(False, False)

        self.player_data = None

        self.grid_columnconfigure((0, 1), weight=1)

        self.header = customtkinter.CTkLabel(
            self,
            text="🎨 BLOCK DESIGN TEST - GUI ONLY 🎨",
            font=("Helvetica", 26, "bold"),
            fg_color=UI_STYLE["subtitle_bg"],
            text_color=UI_STYLE["subtitle_text"],
            corner_radius=14,
        )
        self.header.grid(row=0, column=0, columnspan=2, padx=12, pady=(12, 0), sticky="ew")

        self.name_frame = MyTextboxFrame(self, "Nick Name")
        self.name_frame.grid(row=1, column=0, columnspan=2, padx=12, pady=(10, 0), sticky="nsew")

        self.age_frame = MyTextboxFrame(self, "Age")
        self.age_frame.grid(row=2, column=0, padx=12, pady=(10, 0), sticky="nsew")

        self.gender_frame = MyRadiobuttonFrame(self, "Gender", ["male", "female"])
        self.gender_frame.grid(row=2, column=1, padx=(0, 12), pady=(10, 0), sticky="nsew")

        self.mode_frame = MyRadiobuttonFrame(self, "Game Mode", ["1 Player", "2 Player"])
        self.mode_frame.grid(row=3, column=0, columnspan=2, padx=12, pady=(10, 0), sticky="nsew")

        self.voice_controls = customtkinter.CTkFrame(
            self,
            fg_color=UI_STYLE["card_bg"],
            corner_radius=14,
            border_width=2,
            border_color="#D9ECFF",
        )
        self.voice_controls.grid(row=4, column=0, padx=12, pady=(10, 0), sticky="nsew", columnspan=2)
        self.voice_controls.grid_columnconfigure((0, 1, 2), weight=1)

        self.voice_name_button = customtkinter.CTkButton(
            self.voice_controls,
            text="🎤 Nama",
            command=lambda: self.start_voice_fill("name"),
            fg_color=UI_STYLE["secondary_btn"],
            hover_color=UI_STYLE["secondary_btn_hover"],
            text_color=UI_STYLE["subtitle_text"],
            font=("Helvetica", 20, "bold"),
        )
        self.voice_name_button.grid(row=0, column=0, padx=8, pady=8, sticky="ew")

        self.voice_age_button = customtkinter.CTkButton(
            self.voice_controls,
            text="🎤 Umur",
            command=lambda: self.start_voice_fill("age"),
            fg_color=UI_STYLE["secondary_btn"],
            hover_color=UI_STYLE["secondary_btn_hover"],
            text_color=UI_STYLE["subtitle_text"],
            font=("Helvetica", 20, "bold"),
        )
        self.voice_age_button.grid(row=0, column=1, padx=8, pady=8, sticky="ew")

        self.voice_gender_button = customtkinter.CTkButton(
            self.voice_controls,
            text="🎤 Gender",
            command=lambda: self.start_voice_fill("gender"),
            fg_color=UI_STYLE["secondary_btn"],
            hover_color=UI_STYLE["secondary_btn_hover"],
            text_color=UI_STYLE["subtitle_text"],
            font=("Helvetica", 20, "bold"),
        )
        self.voice_gender_button.grid(row=0, column=2, padx=8, pady=8, sticky="ew")

        self.voice_status = customtkinter.CTkLabel(
            self,
            text="Tip: tekan tombol 🎤 lalu bicara 3-4 detik",
            font=("Helvetica", 18, "bold"),
            fg_color=UI_STYLE["card_bg"],
            text_color=UI_STYLE["text_dark"],
            corner_radius=10,
        )
        self.voice_status.grid(row=5, column=0, padx=12, pady=(8, 0), sticky="ew", columnspan=2)

        self.start_button = customtkinter.CTkButton(
            self,
            text="✅ MULAI (GUI ONLY)",
            command=self._submit,
            font=("Helvetica", 28, "bold"),
            corner_radius=14,
            height=58,
            fg_color=UI_STYLE["primary_btn"],
            hover_color=UI_STYLE["primary_btn_hover"],
            text_color=UI_STYLE["text_dark"],
        )
        self.start_button.grid(row=6, column=0, columnspan=2, padx=12, pady=12, sticky="ew")

    def _set_voice_status(self, message: str):
        self.voice_status.configure(text=message)

    def start_voice_fill(self, target: str):
        self._set_voice_status("🎧 Mendengarkan... silakan bicara")
        threading.Thread(target=self._voice_fill_worker, args=(target,), daemon=True).start()

    def _voice_fill_worker(self, target: str):
        import tkinter.messagebox as messagebox

        try:
            if sr is None:
                raise RuntimeError("Package SpeechRecognition belum terpasang")
            if sd is None or np is None:
                raise RuntimeError("Package sounddevice/numpy belum terpasang")

            recognizer = sr.Recognizer()
            duration = 4
            sample_rate = 16000

            audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="float32")
            sd.wait()
            audio_int16 = np.int16(np.clip(audio, -1.0, 1.0) * 32767)
            audio_data = sr.AudioData(audio_int16.tobytes(), sample_rate, 2)
            text = recognizer.recognize_google(audio_data, language="id-ID")

            def apply_result():
                text_clean = text.strip()
                if target == "name":
                    self.name_frame.textbox.delete("0.0", "end")
                    self.name_frame.textbox.insert("0.0", text_clean)
                    self._set_voice_status(f"✅ Nama terisi: {text_clean}")
                elif target == "age":
                    parsed_age = parse_age_from_voice(text_clean)
                    if parsed_age is None:
                        self._set_voice_status("⚠️ Umur tidak terbaca, coba ulang")
                    else:
                        self.age_frame.textbox.delete("0.0", "end")
                        self.age_frame.textbox.insert("0.0", str(parsed_age))
                        self._set_voice_status(f"✅ Umur terisi: {parsed_age}")
                elif target == "gender":
                    parsed_gender = parse_gender_from_voice(text_clean)
                    if not parsed_gender:
                        self._set_voice_status("⚠️ Gender tidak terbaca, ucapkan male/female")
                    else:
                        self.gender_frame.set(parsed_gender)
                        self._set_voice_status(f"✅ Gender terisi: {parsed_gender}")

            self.after(0, apply_result)
        except Exception as e:
            err_msg = str(e)

            def show_err():
                self._set_voice_status("❌ Voice input gagal")
                messagebox.showwarning("Voice Input", f"Voice input gagal: {err_msg}")

            self.after(0, show_err)

    def _submit(self):
        import tkinter.messagebox as messagebox

        name = self.name_frame.get()
        age = self.age_frame.get()
        gender = self.gender_frame.get()
        mode = self.mode_frame.get()

        if not name:
            messagebox.showerror("Input Error", "Nama tidak boleh kosong")
            return
        if not age.isdigit():
            messagebox.showerror("Input Error", "Usia harus angka")
            return
        if not gender:
            messagebox.showerror("Input Error", "Pilih gender")
            return
        if not mode:
            messagebox.showerror("Input Error", "Pilih game mode")
            return

        self.player_data = {
            "name": name,
            "age": int(age),
            "gender": gender,
            "mode": mode,
        }
        self.destroy()


class GameWindow(customtkinter.CTk):
    def __init__(self, player_data: dict):
        super().__init__()
        self.title("Block Design Test - GUI Only")
        self.geometry("960x560" if DISPLAY_HALF else "1200x800")
        self.configure(fg_color=UI_STYLE["window_bg"])

        self.player_data = player_data
        self.level = 1
        self.max_level = 8
        self.timer_running = False
        self.start_time = 0.0
        self.after_job = None

        if DISPLAY_HALF:
            self.grid_rowconfigure(0, weight=4)
            self.grid_rowconfigure(1, weight=1)
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)
        else:
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)

        root_panel = customtkinter.CTkFrame(self, fg_color=UI_STYLE["panel_bg"], corner_radius=18)
        if DISPLAY_HALF:
            root_panel.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 140))
        else:
            root_panel.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        root_panel.grid_columnconfigure(0, weight=1)
        root_panel.grid_columnconfigure(1, weight=1)
        root_panel.grid_rowconfigure(1, weight=1)

        info = f"Pemain: {player_data['name']} | Umur: {player_data['age']} | Gender: {player_data['gender']} | Mode: {player_data['mode']}"
        self.info_label = customtkinter.CTkLabel(
            root_panel,
            text=info,
            font=("Helvetica", 20, "bold"),
            fg_color=UI_STYLE["subtitle_bg"],
            text_color=UI_STYLE["subtitle_text"],
            corner_radius=12,
        )
        self.info_label.grid(row=0, column=0, columnspan=2, padx=12, pady=12, sticky="ew")

        left = customtkinter.CTkFrame(root_panel, fg_color=UI_STYLE["panel_bg"], corner_radius=14)
        left.grid(row=1, column=0, padx=(12, 6), pady=(0, 12), sticky="nsew")
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(1, weight=1)

        right = customtkinter.CTkFrame(root_panel, fg_color=UI_STYLE["panel_bg"], corner_radius=14)
        right.grid(row=1, column=1, padx=(6, 12), pady=(0, 12), sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(0, weight=1)

        self.design_title = TextFrame(left, "Block Design")
        self.design_title.grid(row=0, column=0, padx=0, pady=(0, 6), sticky="ew")

        self.timer_label = customtkinter.CTkLabel(
            left,
            text="00:00.00",
            font=("Helvetica", 32 if DISPLAY_HALF else 42, "bold"),
            fg_color=UI_STYLE["timer_bg"],
            text_color=UI_STYLE["timer_text"],
            corner_radius=12,
            height=88,
        )
        self.timer_label.grid(row=1, column=0, padx=12, pady=(4, 8), sticky="ew")

        self.design_image_frame = ImageFrame(left, "")
        self.design_image_frame.grid(row=2, column=0, padx=0, pady=0, sticky="nsew")
        self.design_image_frame.grid_rowconfigure(1, weight=1)
        self.design_image_frame.grid_columnconfigure(0, weight=1)

        self.image_label = customtkinter.CTkLabel(self.design_image_frame, text="", anchor="center")
        self.image_label.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")

        self.camera_title = TextFrame(right, "Upper Table Camera")
        self.camera_title.grid(row=0, column=0, padx=0, pady=(0, 6), sticky="ew")

        self.camera_placeholder_frame = ImageFrame(right, "")
        self.camera_placeholder_frame.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")
        self.camera_placeholder_frame.grid_rowconfigure(1, weight=1)
        self.camera_placeholder_frame.grid_columnconfigure(0, weight=1)

        self.status_label = customtkinter.CTkLabel(
            self.camera_placeholder_frame,
            text="Placeholder area (tanpa kamera / CV)",
            font=("Helvetica", 24, "bold"),
            text_color=UI_STYLE["text_dark"],
        )
        self.status_label.grid(row=1, column=0, padx=12, pady=12, sticky="nsew")

        controls = customtkinter.CTkFrame(root_panel, fg_color=UI_STYLE["panel_bg"], corner_radius=0)
        controls.grid(row=2, column=0, columnspan=2, padx=12, pady=(0, 12), sticky="ew")
        controls.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.start_btn = customtkinter.CTkButton(controls, text="(START)", command=self.start_timer)
        self.start_btn.grid(row=0, column=0, padx=6, pady=6, sticky="ew")

        self.stop_btn = customtkinter.CTkButton(controls, text="Stop Timer", command=self.stop_timer)
        self.stop_btn.grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        self.current_level_button = customtkinter.CTkButton(
            controls,
            text=f"Current Level: {self.level}",
            command=lambda: None,
            fg_color=UI_STYLE["secondary_btn"],
            hover_color=UI_STYLE["secondary_btn_hover"],
            text_color=UI_STYLE["subtitle_text"],
        )
        self.current_level_button.grid(row=0, column=2, padx=6, pady=6, sticky="ew")

        self.next_btn = customtkinter.CTkButton(controls, text="Next Level", command=self.next_level)
        self.next_btn.grid(row=0, column=3, padx=6, pady=6, sticky="ew")

        self.exit_btn = customtkinter.CTkButton(controls, text="Exit", command=self.destroy)
        self.exit_btn.grid(row=0, column=4, padx=6, pady=6, sticky="ew")

        self.bind("<Return>", lambda _: self.next_level())
        self._load_level_image(self.level)

    def _level_image_path(self, level: int) -> Path:
        if level == 0:
            return LEVEL_DIR / "00.jpg"
        return LEVEL_DIR / f"{level:02d}.jpg"

    def _load_level_image(self, level: int):
        path = self._level_image_path(level)
        if not path.exists():
            self.image_label.configure(text=f"Image tidak ditemukan:\n{path.name}", image=None)
            return

        size = (400, 400) if DISPLAY_HALF else (520, 520)
        image = Image.open(path).resize(size, Image.Resampling.LANCZOS)
        self.ctk_image = customtkinter.CTkImage(light_image=image, size=size)
        self.image_label.configure(image=self.ctk_image, text="")

    def start_timer(self):
        if self.timer_running:
            return
        self.timer_running = True
        self.start_time = time.time()
        self._update_timer()

    def stop_timer(self):
        self.timer_running = False
        if self.after_job:
            self.after_cancel(self.after_job)
            self.after_job = None

    def _update_timer(self):
        if not self.timer_running:
            return
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        hundredths = int((elapsed - int(elapsed)) * 100)
        self.timer_label.configure(text=f"{minutes:02d}:{seconds:02d}.{hundredths:02d}")
        self.after_job = self.after(30, self._update_timer)

    def next_level(self):
        self.level += 1
        if self.level > self.max_level:
            self.stop_timer()
            self.status_label.configure(text="Selesai (GUI only)")
            self.current_level_button.configure(text="Current Level: Done")
            return
        self.stop_timer()
        self.timer_label.configure(text="00:00.00")
        self.current_level_button.configure(text=f"Current Level: {self.level}")
        self._load_level_image(self.level)


def main():
    input_window = InputWindow()
    input_window.mainloop()

    if input_window.player_data is None:
        return

    app = GameWindow(input_window.player_data)
    app.mainloop()


if __name__ == "__main__":
    main()
