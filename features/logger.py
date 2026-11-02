from pathlib import Path
from datetime import datetime

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    openpyxl = None
    HAS_OPENPYXL = False

def export_logs(root_dir, logs, log):
    root = Path(root_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    txt_path = root / f"organizer_log_{timestamp}.txt"
    try:
        txt_path.write_text("\\n".join(logs), encoding="utf-8")
        log(f"[info] Log TXT tersimpan: {txt_path}")
    except Exception as exc:
        log(f"[gagal simpan TXT] {exc}")

    if HAS_OPENPYXL:
        xlsx_path = root / f"organizer_log_{timestamp}.xlsx"
        try:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "Log Aktivitas"
            sheet.append(["No", "Aktivitas Log"])
            for number, line in enumerate(logs, start=1):
                sheet.append([number, line])
            sheet.column_dimensions["A"].width = 8
            sheet.column_dimensions["B"].width = 110
            sheet.freeze_panes = "A2"
            workbook.save(xlsx_path)
            log(f"[info] Log Excel tersimpan: {xlsx_path}")
        except Exception as exc:
            log(f"[gagal simpan Excel] {exc}")
    else:
        log("[info] openpyxl tidak tersedia; ekspor Excel dilewati.")
