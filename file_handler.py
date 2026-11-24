
# file_handler.py - Bagian Raya
# Mengurus baca data, simpan data, dan cetak struk.

import json
import os
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDER_DATA = os.path.join(BASE_DIR, "data")
FOLDER_LAPORAN = os.path.join(BASE_DIR, "laporan")
FILE_DB = os.path.join(FOLDER_DATA, "db_panen.json")
FILE_BACKUP = os.path.join(FOLDER_DATA, "db_panen_backup.json")

KOLOM_WAJIB = [
    "id", "tanggal", "nama", "komoditas", "berat",
    "harga_per_kg", "total", "bagian_petani", "bagian_kas"
]


def siapkan_folder():
    os.makedirs(FOLDER_DATA, exist_ok=True)
    os.makedirs(FOLDER_LAPORAN, exist_ok=True)


# Validasi struktur setiap record
def validasi_data(data):
    if not isinstance(data, list):
        return False

    id_terdaftar = set()

    for record in data:
        if not isinstance(record, dict):
            return False

        if not all(kolom in record for kolom in KOLOM_WAJIB):
            return False

        if not isinstance(record["id"], str) or not record["id"]:
            return False

        if record["id"] in id_terdaftar:
            return False

        id_terdaftar.add(record["id"])

        kolom_angka = [
            "berat", "harga_per_kg", "total",
            "bagian_petani", "bagian_kas"
        ]

        for kolom in kolom_angka:
            if (
                isinstance(record[kolom], bool)
                or not isinstance(record[kolom], (int, float))
            ):
                return False

    return True


# 1. MEMUAT DATA JSON
def muat_data():
    siapkan_folder()

    if not os.path.exists(FILE_DB):
        simpan_data([])
        return []

    try:
        with open(FILE_DB, "r", encoding="utf-8") as file:
            data = json.load(file)

        if validasi_data(data):
            return data

        print("Peringatan: Format data tidak valid.")
        return []

    except (json.JSONDecodeError, UnicodeDecodeError):
        print("Peringatan: File JSON rusak atau tidak dapat dibaca.")
        return []


# 2. MENYIMPAN DATA JSON
def simpan_data(data):
    siapkan_folder()

    if not validasi_data(data):
        raise ValueError("Data tidak valid. Penyimpanan dibatalkan.")

    # Backup data lama sebelum ditimpa
    if os.path.exists(FILE_DB):
        shutil.copy2(FILE_DB, FILE_BACKUP)

    file_sementara = FILE_DB + ".tmp"

    try:
        with open(file_sementara, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        os.replace(file_sementara, FILE_DB)

    finally:
        if os.path.exists(file_sementara):
            os.remove(file_sementara)


# 3. MENCETAK STRUK KE FILE TXT
def cetak_struk(record):
    siapkan_folder()

    if not isinstance(record, dict):
        raise ValueError("Data struk tidak valid.")

    if not all(kolom in record for kolom in KOLOM_WAJIB):
        raise ValueError("Data struk tidak lengkap.")

    nama_file = "struk_" + record["id"] + ".txt"
    path = os.path.join(FOLDER_LAPORAN, nama_file)

    def rupiah(angka):
        return "Rp " + f"{angka:,.0f}".replace(",", ".")

    isi_struk = [
        "=" * 40,
        "STRUK PEMBAGIAN HASIL PANEN".center(40),
        "=" * 40,
        "ID Panen       : " + record["id"],
        "Tanggal        : " + record["tanggal"],
        "Nama Petani    : " + record["nama"],
        "Komoditas      : " + record["komoditas"],
        "Berat          : " + str(record["berat"]) + " kg",
        "Harga per kg   : " + rupiah(record["harga_per_kg"]),
        "-" * 40,
        "Total           : " + rupiah(record["total"]),
        "Bagian Petani   : " + rupiah(record["bagian_petani"]),
        "Bagian Kas      : " + rupiah(record["bagian_kas"]),
        "=" * 40,
        "Dicetak: " + datetime.now().strftime("%Y-%m-%d %H:%M"),
        "=" * 40
    ]

    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(isi_struk) + "\n")

    return path
