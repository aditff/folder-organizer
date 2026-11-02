import os
from pathlib import Path

from config import IMAGE_EXTENSIONS
from features.naming import apply_naming_style
from features.duplicate import remove_duplicate
from features.conversion import convert_image, change_extension_name
from features.archive import extract_archives, compress_folders_by_depth
from features.logger import export_logs

def _is_excluded(filename, excluded_extensions):
    lower_name = filename.lower()
    return any(lower_name.endswith(ext.lower()) for ext in excluded_extensions)

def run_cleaning_process(root_dir, options, log):
    """
    Alur utama. options adalah dictionary dari GUI.
    Seluruh operasi berjalan pada worker thread; callback log harus thread-safe.
    """
    root = Path(root_dir).resolve()
    logs = []

    def record(message):
        logs.append(message)
        log(message)

    record(f"=== MEMULAI PROSES: {root} ===")
    seen_hashes = {}

    if options["extract"]:
        record(f"[tahap] Ekstraksi arsip (Mode: {options['extract_mode']})")
        extract_archives(root, options["extract_mode"], record)

    record("[tahap] Pemrosesan file dan folder")
    # bottom-up: isi subfolder diproses sebelum folder induknya.
    for current, dirnames, filenames in os.walk(root, topdown=False):
        current_path = Path(current)

        for filename in filenames:
            file_path = current_path / filename
            if not file_path.is_file():
                continue

            if options["duplicate"]:
                if remove_duplicate(file_path, seen_hashes, record):
                    continue

            # Konversi gambar .
            if options["convert_images"] and file_path.suffix.lower() in IMAGE_EXTENSIONS:
                converted = convert_image(file_path, options["image_target"], record)
                if converted:
                    file_path = converted

            # Perbaikan nama ekstensi sesuai checkbox.
            file_path = change_extension_name(file_path, options["extension_rules"], record)

            # Rename nama file.
            if options["rename"] and not _is_excluded(file_path.name, options["excluded_extensions"]):
                new_stem = apply_naming_style(
                    file_path.stem, options["naming_style"], options["custom_rule"]
                )
                new_path = file_path.with_name(new_stem + file_path.suffix)
                if new_path != file_path:
                    if new_path.exists():
                        record(f"[lewati rename] Nama tujuan sudah ada: {new_path}")
                    else:
                        try:
                            old_name = file_path.name
                            file_path.rename(new_path)
                            file_path = new_path
                            record(f"[rename file] {old_name} ➔ {new_path.name}")
                        except OSError as exc:
                            record(f"[gagal rename file] {file_path}: {exc}")

        if options["rename"]:
            for dirname in dirnames:
                old_path = current_path / dirname
                if not old_path.exists() or not old_path.is_dir():
                    continue
                new_name = apply_naming_style(
                    dirname, options["naming_style"], options["custom_rule"]
                )
                new_path = current_path / new_name
                if new_path == old_path:
                    continue
                if new_path.exists():
                    record(f"[lewati rename folder] Nama tujuan sudah ada: {new_path}")
                    continue
                try:
                    old_path.rename(new_path)
                    record(f"[rename folder] {dirname} ➔ {new_name}")
                except OSError as exc:
                    record(f"[gagal rename folder] {old_path}: {exc}")

    # Kompresi folder berdasarkan level kedalaman yang dipilih user di GUI
    if options["compress"] and root.exists():
        record(f"[tahap] Kompresi folder (Level: {options['compress_level']})")
        compress_folders_by_depth(root, options["compress_target"], options["compress_level"], record)

    record("=== PROSES SELESAI ===")
    export_logs(root, logs, record)
    return logs