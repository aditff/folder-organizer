# 📂 Folder Organizer

Aplikasi desktop berbasis Python untuk merapikan dan mengelola file di dalam folder secara otomatis berdasarkan kategori (ekstensi file), mendeteksi duplikat, serta membersihkan file sampah dengan antarmuka yang bersih dan mudah digunakan.

---

## ✨ Fitur Utama

- **File Organization (Archive):** Mengelompokkan file secara otomatis ke dalam folder spesifik (Dokumen, Gambar, Musik, Video, dll).
- **Cleaner:** Membersihkan file-file sampah atau tidak penting di dalam direktori.
- **Duplicate Finder:** Mendeteksi dan menghapus file duplikat untuk menghemat ruang penyimpanan.
- **Conversion & Naming:** Mengonversi format file tertentu dan merapikan pola penamaan (naming convention) file secara massal.
- **Custom Logger & Config:** Mencatat log aktivitas pemindahan/penataan file dan mendukung pengaturan konfigurasi yang fleksibel.

---

## 🛠️ Struktur Proyek

```text
folder-organizer/
│
├── assets/
│   └── icons/
│       └── icon.ico
├── features/
│   ├── __init__.py
│   ├── archive.py
│   ├── cleaner.py
│   ├── conversion.py
│   ├── duplicate.py
│   ├── logger.py
│   └── naming.py
├── app.py
├── main.py
├── config.py
└── requirements.txt
```
