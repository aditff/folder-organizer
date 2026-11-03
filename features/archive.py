import os
import shutil
import subprocess
import zipfile
from pathlib import Path, PurePosixPath

try:
    import rarfile
    HAS_RARFILE = True
except ImportError:
    rarfile = None
    HAS_RARFILE = False

from config import WINRAR_EXE, UNRAR_EXE

def _safe_member_path(destination, member_name):
    destination = Path(destination).resolve()
    normalized = str(member_name).replace("\\", "/")
    member = PurePosixPath(normalized)
    if member.is_absolute() or any(part == ".." for part in member.parts):
        raise ValueError(f"Path tidak aman di dalam arsip: {member_name}")
    target = (destination / Path(*member.parts)).resolve()
    if target != destination and destination not in target.parents:
        raise ValueError(f"Path keluar dari folder tujuan: {member_name}")
    return target

def safe_extract_zip(archive_path, destination, log):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path, "r") as archive:
        for info in archive.infolist():
            _safe_member_path(destination, info.filename)
            archive.extract(info, destination)
            log(f"   ↳ [membongkar] {info.filename}")

def safe_extract_rar(archive_path, destination, log):
    if not HAS_RARFILE:
        raise RuntimeError("Library rarfile belum terpasang. Jalankan: pip install rarfile")
    if UNRAR_EXE:
        rarfile.UNRAR_TOOL = UNRAR_EXE
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    with rarfile.RarFile(archive_path, "r") as archive:
        for info in archive.infolist():
            _safe_member_path(destination, info.filename)
            archive.extract(info, destination)
            log(f"   ↳ [membongkar rar] {info.filename}")

def _flatten_single_folder(destination_path, log):
    dest = Path(destination_path)
    if not dest.exists() or not dest.is_dir():
        return

    items = list(dest.iterdir())
    if len(items) == 1 and items[0].is_dir():
        inner_folder = items[0]
        try:
            temp_dir = dest.parent / f"_temp_flatten_{dest.name}"
            inner_folder.rename(temp_dir)
            for child in temp_dir.iterdir():
                child.rename(dest / child.name)
            shutil.rmtree(temp_dir)
            log(f"[meratakan folder] Menghilangkan folder kembar berlapis di: {dest.name}")
        except Exception as exc:
            log(f"[peringatan] Gagal meratakan folder {dest.name}: {exc}")

def extract_archives(root_dir, extract_mode, log):
    root = Path(root_dir)
    
    target_base_dir = root
    if "1 folder khusus" in extract_mode:
        target_base_dir = root / "Hasil_Ekstraksi"
        target_base_dir.mkdir(parents=True, exist_ok=True)

    max_loops = 20
    loop_count = 0
    total_extracted_count = 0

    while loop_count < max_loops:
        loop_count += 1
        found_archives = []

        for current, _, filenames in os.walk(root):
            current_path = Path(current)
            if "Hasil_Ekstraksi" in current_path.parts:
                continue

            for filename in filenames:
                archive_path = current_path / filename
                suffix = archive_path.suffix.lower()
                if suffix in (".zip", ".rar"):
                    found_archives.append(archive_path)

        if not found_archives:
            break

        extracted_any = False
        for archive_path in found_archives:
            if not archive_path.exists():
                continue

            suffix = archive_path.suffix.lower()
            if "1 folder khusus" in extract_mode:
                destination = target_base_dir / archive_path.stem
            else:
                destination = archive_path.parent / archive_path.stem

            try:
                log(f"[proses ekstrak] Membuka arsip: {archive_path.name}")
                if suffix == ".zip":
                    safe_extract_zip(archive_path, destination, log)
                elif suffix == ".rar":
                    safe_extract_rar(archive_path, destination, log)
                
                _flatten_single_folder(destination, log)
                
                archive_path.unlink()
                extracted_any = True
                total_extracted_count += 1
                log(f"[sukses] Arsip diekstrak & dihapus ➔ {destination.name}")
            except Exception as exc:
                log(f"[gagal ekstrak] {archive_path.name}: {exc}")

        if not extracted_any:
            break

    log(f"[info] Proses ekstrak selesai.")

def compress_main_folder(folder_path, output_format, log):
    folder = Path(folder_path)
    archive_path = folder.with_suffix(output_format)
    if archive_path.exists():
        log(f"[lewati kompresi] Arsip sudah ada: {archive_path.name}")
        return False

    try:
        log(f"[proses kompres] Menyiapkan arsip {output_format} untuk folder: {folder.name}")
        if output_format == ".zip":
            with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for current, _, filenames in os.walk(folder):
                    current_path = Path(current)
                    for filename in filenames:
                        full_path = current_path / filename
                        rel_path = full_path.relative_to(folder.parent)
                        archive.write(full_path, rel_path)
                        log(f"   ↳ [memasukkan] {rel_path}")
        elif output_format == ".rar":
            if not WINRAR_EXE:
                raise RuntimeError("WinRAR.exe tidak ditemukan. Instal WinRAR atau pilih ZIP.")
            
            parent_dir = folder.parent
            folder_name = folder.name
            
            log(f"   ↳ [menjalankan WinRAR] Mengemas folder {folder_name}...")
            subprocess.run(
                [WINRAR_EXE, "a", "-ibck", "-r", str(archive_path), folder_name],
                cwd=str(parent_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
        else:
            raise ValueError("Format arsip tidak didukung.")

        if not archive_path.exists() or archive_path.stat().st_size == 0:
            raise RuntimeError("Arsip tidak terbentuk atau kosong.")
            
        log(f"[kompres sukses] Berhasil membuat arsip: {archive_path.name}")
        return True
    except Exception as exc:
        try:
            if archive_path.exists():
                archive_path.unlink()
        except OSError:
            pass
        log(f"[gagal kompres] {folder.name}: {exc}")
        return False

def compress_folders_by_depth(root_dir, output_format, level_option, log):
    root = Path(root_dir).resolve()
    
    if "kedua" in level_option:
        target_depth = 1
    elif "ketiga" in level_option:
        target_depth = 2
    else:
        target_depth = 0

    if target_depth == 0:
        if compress_main_folder(root, output_format, log):
            try:
                shutil.rmtree(root)
                log(f"[info] Folder utama '{root.name}' berhasil dihapus setelah kompresi.")
                return True
            except OSError as exc:
                log(f"[peringatan] Gagal menghapus folder utama: {exc}")
        else:
                log("[info] Tidak ada file yang terkompresi.")
        return False

    folders_to_compress = []
    for current, _, _ in os.walk(root):
        current_path = Path(current).resolve()
        if current_path == root:
            continue
        try:
            rel_parts = current_path.relative_to(root).parts
            if len(rel_parts) == target_depth:
                folders_to_compress.append(current_path)
        except ValueError:
            continue

    if not folders_to_compress:
        log(f"[info] Tidak ada file yang terkompresi (tidak ditemukan folder pada level kedalaman yang dipilih di dalam {root.name}).")
        return False

    success_count = 0
    for folder_path in folders_to_compress:
        if not folder_path.exists():
            continue
        if compress_main_folder(folder_path, output_format, log):
            try:
                shutil.rmtree(folder_path)
                log(f"[info] Folder '{folder_path.name}' dihapus setelah kompresi berhasil.")
                success_count += 1
            except OSError as exc:
                log(f"[peringatan] Gagal menghapus folder {folder_path.name}: {exc}")

    if success_count == 0:
        log("[info] Tidak ada file yang terkompresi.")
        return False

    return success_count > 0