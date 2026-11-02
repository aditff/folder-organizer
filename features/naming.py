import re

def apply_naming_style(name: str, style: str, custom_rule: str = "") -> str:
    """Mengubah nama tanpa mengubah ekstensi file."""
    
    # Normalisasi spasi dan pemisah umum
    clean_name = name.replace("_", " ").replace("-", " ")

    if style == "snake_case (lowercase)" or style == "snake_case (UPPERCASE)":
        first = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        second = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", first)
        result = re.sub(r"[\s\-]+", "_", second)
        result = re.sub(r"_+", "_", result).strip("_")
        return result.lower() if "lowercase" in style else result.upper()

    if style == "Capitalize Each Word":
        # Jika teks rapat tanpa spasi (misal: "lapor" atau "lapor pak"), 
        # pisahkan dulu berdasarkan perubahan huruf kapital atau biarkan title case per kata.
        words = clean_name.split()
        if len(words) == 1 and not any(c.isupper() for c in words[0]):
            # Jika satu kata utuh lowercase (seperti "lapor"), kita buat kapital di awal atau biarkan .title()
            # Jika ingin mendeteksi singkatan khusus, bisa disesuaikan. Untuk amannya pakai .title()
            return words[0].title()
        
        return " ".join(word.capitalize() for word in words)

    if style == "camelCase":
        words = re.findall(r"[a-zA-Z0-9]+", clean_name)
        if not words:
            return name
        return words[0].lower() + "".join(word.capitalize() for word in words[1:])

    if style == "lowercase":
        return name.lower()

    if style == "UPPERCASE":
        return name.upper()

    if style == "custom replace":
        if "," not in custom_rule:
            return name
        old, new = custom_rule.split(",", 1)
        return name.replace(old.strip(), new.strip())

    return name