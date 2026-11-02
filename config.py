from pathlib import Path
import os
import shutil

APP_NAME = "Folder & Media Organizer Pro"
APP_VERSION = "2.0.0"

DEFAULT_EXCLUDED_EXTENSIONS = (
    ".php, .blade.php, .js, .ts, .tsx, .jsx, .mjs, .cjs, .json, .env, "
    ".env.example, .env.local, .html, .css, .scss, .sass, .less, .sql, "
    ".md, .yml, .yaml, .xml, .lock, .config.js, .config.ts, .sh, .bat, "
    ".py, .go, .java, .c, .cpp"
)

EXTENSION_RULES = {
    ".doc ➔ .docx": (".doc", ".docx"),
    ".xls/.xlx ➔ .xlsx": ((".xls", ".xlx", ".xlxs"), ".xlsx"),
    ".ppt ➔ .pptx": ((".ppt", ".pot"), ".pptx"),
    ".htm ➔ .html": (".htm", ".html"),
    ".jpeg ➔ .jpg": (".jpeg", ".jpg"),
    ".mpga ➔ .mp3": (".mpga", ".mp3"),
    ".txt ➔ .md": (".txt", ".md"),
    ".svg ➔ .png": (".svg", ".png"),
    ".m4a ➔ .mp3": (".m4a", ".mp3"),
    ".tiff ➔ .png": (".tiff", ".png"),
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}
IMAGE_TARGETS = [".avif", ".jpg", ".png", ".webp"]
NAMING_OPTIONS = [
    "snake_case (lowercase)",
    "snake_case (UPPERCASE)",
    "Capitalize Each Word",
    "camelCase",
    "lowercase",
    "UPPERCASE",
    "custom replace",
]

ARCHIVE_EXTRACT_OPTIONS = [
    "Ekstrak keseluruhan (di masing-masing lokasi)",
    "Ekstrak ke 1 folder khusus",
]

COMPRESS_LEVEL_OPTIONS = [
    "Mulai dari folder pertama (Root Utama)",
    "Mulai dari folder kedua (Sub-folder level 1)",
    "Mulai dari folder ketiga (Sub-folder level 2)",
]
def find_winrar():
    candidates = [
        shutil.which("WinRAR"),
        shutil.which("WinRAR.exe"),
        r"C:\Program Files\WinRAR\WinRAR.exe",
        r"C:\Program Files (x86)\WinRAR\WinRAR.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    return None

WINRAR_EXE = find_winrar()

def find_unrar():
    candidates = [
        shutil.which("UnRAR"),
        shutil.which("UnRAR.exe"),
        r"C:\Program Files\WinRAR\UnRAR.exe",
        r"C:\Program Files (x86)\WinRAR\UnRAR.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    return None

UNRAR_EXE = find_unrar()
