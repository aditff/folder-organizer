from pathlib import Path
from PIL import Image, ImageOps

# Plugin ini mendaftarkan decoder/encoder AVIF ke Pillow jika tersedia.
try:
    import pillow_avif  # noqa: F401
except ImportError:
    pass

from config import EXTENSION_RULES, IMAGE_EXTENSIONS

def convert_image(file_path, target_extension, log):
    """Konversi gambar sebenarnya menggunakan Pillow. Mengembalikan path hasil atau None."""
    source = Path(file_path)
    target = source.with_name(source.stem + target_extension)
    if source.suffix.lower() == target_extension.lower():
        return source
    if target.exists():
        log(f"[lewati konversi] Tujuan sudah ada: {target}")
        return None

    try:
        with Image.open(source) as original:
            image = ImageOps.exif_transpose(original)
            fmt = target_extension.lstrip(".").upper()
            if fmt == "JPG":
                fmt = "JPEG"
            if fmt == "JPEG" and image.mode in ("RGBA", "LA", "P"):
                rgba = image.convert("RGBA")
                background = Image.new("RGB", rgba.size, "white")
                background.paste(rgba, mask=rgba.getchannel("A"))
                image = background
            elif fmt in ("JPEG",) and image.mode != "RGB":
                image = image.convert("RGB")
            save_options = {"quality": 90} if fmt in ("JPEG", "WEBP", "AVIF") else {}
            image.save(target, format=fmt, **save_options)
        source.unlink()
        log(f"[konversi gambar] {source.name} ➔ {target.name}")
        return target
    except Exception as exc:
        log(f"[gagal konversi gambar] {source}: {exc}")
        return None

def change_extension_name(file_path, enabled_rules, log):
    """
    Mengubah nama ekstensi sesuai pilihan.
    CATATAN: ini hanya mengganti nama ekstensi, bukan mengonversi format/isi dokumen atau audio.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()
    new_suffix = suffix

    for label, rule in EXTENSION_RULES.items():
        if not enabled_rules.get(label, False):
            continue
        old_suffixes, replacement = rule
        if isinstance(old_suffixes, str):
            old_suffixes = (old_suffixes,)
        if suffix in old_suffixes:
            new_suffix = replacement
            break

    if new_suffix == suffix:
        return path

    target = path.with_name(path.stem + new_suffix)
    if target.exists():
        log(f"[lewati ubah ekstensi] Tujuan sudah ada: {target}")
        return path
    try:
        path.rename(target)
        log(f"[ubah nama ekstensi] {path.name} ➔ {target.name}")
        return target
    except OSError as exc:
        log(f"[gagal ubah ekstensi] {path}: {exc}")
        return path

def is_supported_image(path):
    return Path(path).suffix.lower() in IMAGE_EXTENSIONS
