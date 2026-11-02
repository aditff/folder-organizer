import hashlib
from pathlib import Path

def get_file_hash(file_path, algorithm="md5", chunk_size=1024 * 1024):
    """Menghitung hash secara streaming agar file besar tidak dimuat seluruhnya ke RAM."""
    hasher = hashlib.new(algorithm)
    try:
        with Path(file_path).open("rb") as file:
            for chunk in iter(lambda: file.read(chunk_size), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (OSError, ValueError):
        return None

def remove_duplicate(file_path, seen_hashes, log):
    digest = get_file_hash(file_path)
    if not digest:
        return False
    if digest in seen_hashes:
        try:
            Path(file_path).unlink()
            log(f"[hapus duplikat] {file_path} (sama dengan {seen_hashes[digest]})")
            return True
        except OSError as exc:
            log(f"[gagal hapus duplikat] {file_path}: {exc}")
            return False
    seen_hashes[digest] = str(file_path)
    return False
