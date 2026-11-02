import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from config import (
    APP_NAME, APP_VERSION, DEFAULT_EXCLUDED_EXTENSIONS,
    EXTENSION_RULES, IMAGE_TARGETS, NAMING_OPTIONS, ARCHIVE_EXTRACT_OPTIONS,
    COMPRESS_LEVEL_OPTIONS,
)
from features.cleaner import run_cleaning_process

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class FolderCleanerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("960x990")
        self.minsize(860, 800)

        self.log_queue = queue.Queue()
        self.worker = None
        self.session_logs = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)

        # Header Title
        title = ctk.CTkLabel(
            self, text="🧹 Folder & Media Organizer Pro",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=(15, 8), sticky="w")

        # 1. Folder Target Frame
        self.dir_frame = ctk.CTkFrame(self)
        self.dir_frame.grid(row=1, column=0, padx=20, pady=4, sticky="ew")
        self.dir_frame.grid_columnconfigure(0, weight=1)
        
        self.dir_entry = ctk.CTkEntry(
            self.dir_frame, placeholder_text="Pilih folder target...", height=35
        )
        self.dir_entry.grid(row=0, column=0, padx=(12, 8), pady=10, sticky="ew")
        
        self.browse_btn = ctk.CTkButton(
            self.dir_frame, text="Pilih Folder", width=120, height=35, command=self.browse_directory
        )
        self.browse_btn.grid(row=0, column=1, padx=(0, 12), pady=10)

        # 2. Settings Container (Kolom Kiri & Kanan: Penamaan & Konversi)
        self.settings_container = ctk.CTkFrame(self, fg_color="transparent")
        self.settings_container.grid(row=2, column=0, padx=20, pady=4, sticky="ew")
        self.settings_container.grid_columnconfigure((0, 1), weight=1)

        # --- KOLOM KIRI: Penamaan & Rename ---
        self.left_settings_frame = ctk.CTkFrame(self.settings_container)
        self.left_settings_frame.grid(row=0, column=0, padx=(0, 8), pady=0, sticky="nsew")
        self.left_settings_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            self.left_settings_frame, text="Format Penamaan & Rename",
            font=ctk.CTkFont(weight="bold", size=13)
        ).grid(row=0, column=0, columnspan=2, padx=12, pady=(10, 6), sticky="w")

        self.naming_var = tk.StringVar(value="snake_case (lowercase)")
        self.naming_dropdown = ctk.CTkOptionMenu(
            self.left_settings_frame, values=NAMING_OPTIONS, variable=self.naming_var,
            command=self.toggle_custom_naming, height=32
        )
        self.naming_dropdown.grid(row=1, column=0, padx=12, pady=6, sticky="ew")

        self.custom_entry = ctk.CTkEntry(
            self.left_settings_frame, placeholder_text="teks_lama,teks_baru", height=32
        )
        self.custom_entry.grid(row=1, column=1, padx=(0, 12), pady=6, sticky="ew")
        self.custom_entry.configure(state="disabled")

        self.var_rename = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            self.left_settings_frame, text="Aktifkan Rename File & Folder Utama",
            variable=self.var_rename
        ).grid(row=2, column=0, columnspan=2, padx=12, pady=(4, 10), sticky="w")

        # --- KOLOM KANAN: Duplikat & Konversi Gambar ---
        self.right_settings_frame = ctk.CTkFrame(self.settings_container)
        self.right_settings_frame.grid(row=0, column=1, padx=(8, 0), pady=0, sticky="nsew")
        self.right_settings_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            self.right_settings_frame, text="Duplikat & Konversi Gambar",
            font=ctk.CTkFont(weight="bold", size=13)
        ).grid(row=0, column=0, columnspan=2, padx=12, pady=(10, 6), sticky="w")

        self.var_duplicate = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            self.right_settings_frame, text="Hapus File Duplikat (MD5)",
            variable=self.var_duplicate
        ).grid(row=1, column=0, padx=12, pady=6, sticky="w")

        self.var_convert = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self.right_settings_frame, text="Konversi Gambar",
            variable=self.var_convert
        ).grid(row=1, column=1, padx=12, pady=6, sticky="w")

        self.image_target_var = tk.StringVar(value=".avif")
        self.image_dropdown = ctk.CTkOptionMenu(
            self.right_settings_frame, values=IMAGE_TARGETS, variable=self.image_target_var, height=32
        )
        self.image_dropdown.grid(row=2, column=1, padx=12, pady=6, sticky="ew")

        # 3. Extension Rules Frame (Aturan Penggantian Ekstensi yang rapi 4 kolom)
        self.ext_frame = ctk.CTkFrame(self)
        self.ext_frame.grid(row=3, column=0, padx=20, pady=4, sticky="ew")
        self.ext_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(
            self.ext_frame, text="Aturan Penggantian Nama Ekstensi",
            font=ctk.CTkFont(weight="bold", size=13)
        ).grid(row=0, column=0, columnspan=4, padx=12, pady=(10, 6), sticky="w")

        self.ext_vars = {
            label: tk.BooleanVar(value=label in (
                ".doc ➔ .docx", ".xls/.xlx ➔ .xlsx", ".ppt ➔ .pptx", ".htm ➔ .html"
            ))
            for label in EXTENSION_RULES
        }
        for index, (label, variable) in enumerate(self.ext_vars.items()):
            row, col = divmod(index, 4)
            ctk.CTkCheckBox(
                self.ext_frame, text=label, variable=variable
            ).grid(row=row + 1, column=col, padx=12, pady=5, sticky="w")

        # Berikan jarak kecil di baris terakhir ext_frame
        ctk.CTkLabel(self.ext_frame, text="").grid(row=3, column=0, pady=2)

        # 4. Arsip Frame (Ekstrak & Kompres berdampingan)
        self.archive_frame = ctk.CTkFrame(self)
        self.archive_frame.grid(row=4, column=0, padx=20, pady=4, sticky="ew")
        self.archive_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            self.archive_frame, text="Manajemen Arsip (ZIP & RAR)",
            font=ctk.CTkFont(weight="bold", size=13)
        ).grid(row=0, column=0, columnspan=2, padx=12, pady=(10, 6), sticky="w")

        # Kiri: Ekstrak
        self.var_extract = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self.archive_frame, text="Ekstrak ZIP/RAR (Lalu Hapus Arsip)",
            variable=self.var_extract
        ).grid(row=1, column=0, padx=12, pady=4, sticky="w")

        self.extract_mode_var = tk.StringVar(value=ARCHIVE_EXTRACT_OPTIONS[0])
        self.extract_dropdown = ctk.CTkOptionMenu(
            self.archive_frame, values=ARCHIVE_EXTRACT_OPTIONS, variable=self.extract_mode_var, height=32
        )
        self.extract_dropdown.grid(row=2, column=0, padx=12, pady=(4, 12), sticky="ew")

        # Kanan: Kompresi
        self.var_compress = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self.archive_frame, text="Kompres Folder & Hapus Asli",
            variable=self.var_compress
        ).grid(row=1, column=1, padx=12, pady=4, sticky="w")

        self.comp_sub_frame = ctk.CTkFrame(self.archive_frame, fg_color="transparent")
        self.comp_sub_frame.grid(row=2, column=1, padx=8, pady=(4, 12), sticky="ew")
        self.comp_sub_frame.grid_columnconfigure((0, 1), weight=1)

        self.compress_target_var = tk.StringVar(value=".zip")
        self.compress_dropdown = ctk.CTkOptionMenu(
            self.comp_sub_frame, values=[".zip", ".rar"], variable=self.compress_target_var, height=32
        )
        self.compress_dropdown.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self.compress_level_var = tk.StringVar(value=COMPRESS_LEVEL_OPTIONS[0])
        self.compress_level_dropdown = ctk.CTkOptionMenu(
            self.comp_sub_frame, values=COMPRESS_LEVEL_OPTIONS, variable=self.compress_level_var, height=32
        )
        self.compress_level_dropdown.grid(row=0, column=1, padx=(4, 0), sticky="ew")

        # 5. Exclusions Frame
        self.exclude_frame = ctk.CTkFrame(self)
        self.exclude_frame.grid(row=5, column=0, padx=20, pady=4, sticky="ew")
        self.exclude_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self.exclude_frame, text="Pengecualian Ekstensi dari Rename",
            font=ctk.CTkFont(weight="bold", size=12)
        ).grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")
        
        self.exclude_entry = ctk.CTkEntry(
            self.exclude_frame, placeholder_text="Ekstensi dipisahkan koma", height=32
        )
        self.exclude_entry.grid(row=1, column=0, padx=12, pady=(2, 10), sticky="ew")
        self.exclude_entry.insert(0, DEFAULT_EXCLUDED_EXTENSIONS)

        # 6. Action & Log Frame
        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.grid(row=6, column=0, padx=20, pady=(6, 15), sticky="nsew")
        self.action_frame.grid_columnconfigure(0, weight=1)
        self.action_frame.grid_rowconfigure(1, weight=1)

        self.start_btn = ctk.CTkButton(
            self.action_frame, text="🚀 Mulai Proses",
            height=42, font=ctk.CTkFont(size=14, weight="bold"),
            command=self.start_process
        )
        self.start_btn.grid(row=0, column=0, padx=12, pady=10, sticky="ew")

        self.log_textbox = ctk.CTkTextbox(
            self.action_frame, state="disabled", font=("Consolas", 11)
        )
        self.log_textbox.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")

        self.after(100, self.poll_log_queue)

    def browse_directory(self):
        path = filedialog.askdirectory()
        if path:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, path)

    def toggle_custom_naming(self, choice):
        self.custom_entry.configure(
            state="normal" if choice == "custom replace" else "disabled"
        )

    def append_log(self, message):
        self.log_queue.put(("log", message))

    def poll_log_queue(self):
        try:
            while True:
                kind, payload = self.log_queue.get_nowait()
                if kind == "log":
                    self.session_logs.append(payload)
                    self.log_textbox.configure(state="normal")
                    self.log_textbox.insert("end", payload + "\n")
                    self.log_textbox.see("end")
                    self.log_textbox.configure(state="disabled")
                elif kind == "done":
                    self.start_btn.configure(state="normal", text="🚀 Mulai Proses")
                    messagebox.showinfo("Selesai", payload)
                elif kind == "error":
                    self.start_btn.configure(state="normal", text="🚀 Mulai Proses")
                    messagebox.showerror("Proses gagal", payload)
        except queue.Empty:
            pass
        self.after(100, self.poll_log_queue)

    def collect_options(self):
        raw_excludes = self.exclude_entry.get().lower()
        excluded = [
            item.strip() if item.strip().startswith(".") else "." + item.strip()
            for item in raw_excludes.split(",") if item.strip()
        ]
        return {
            "rename": self.var_rename.get(),
            "duplicate": self.var_duplicate.get(),
            "extract": self.var_extract.get(),
            "extract_mode": self.extract_mode_var.get(),
            "convert_images": self.var_convert.get(),
            "image_target": self.image_target_var.get(),
            "compress": self.var_compress.get(),
            "compress_target": self.compress_target_var.get(),
            "compress_level": self.compress_level_var.get(),
            "naming_style": self.naming_var.get(),
            "custom_rule": self.custom_entry.get().strip(),
            "excluded_extensions": excluded,
            "extension_rules": {key: var.get() for key, var in self.ext_vars.items()} if hasattr(self, 'ext_vars') else {},
        }

    def start_process(self):
        target = self.dir_entry.get().strip()
        if not target or not os.path.isdir(target):
            messagebox.showerror("Folder tidak valid", "Pilih folder target yang valid terlebih dahulu.")
            return

        options = self.collect_options()
        if options["compress"] and options["compress_target"] == ".rar":
            from config import WINRAR_EXE
            if not WINRAR_EXE:
                messagebox.showerror(
                    "WinRAR tidak ditemukan",
                    "Pilih ZIP atau instal WinRAR agar kompresi RAR dapat digunakan."
                )
                return

        warning = (
            "Operasi ini dapat mengubah nama, menghapus duplikat, mengekstrak arsip, "
            "dan/atau menghapus folder setelah kompresi berhasil. Sebaiknya uji pada "
            "salinan folder terlebih dahulu.\n\nLanjutkan?"
        )
        if not messagebox.askyesno("Konfirmasi proses", warning):
            return

        self.start_btn.configure(state="disabled", text="Sedang memproses...")
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        self.session_logs.clear()

        def worker():
            try:
                run_cleaning_process(target, options, self.append_log)
                self.log_queue.put(("done", "Proses perapihan selesai. Periksa log untuk detail."))
            except Exception as exc:
                self.log_queue.put(("error", str(exc)))

        self.worker = threading.Thread(target=worker, daemon=True)
        self.worker.start()