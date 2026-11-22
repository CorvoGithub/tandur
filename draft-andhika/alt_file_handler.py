# file_handler.py - Bagian Raya
# Isi: baca/tulis data JSON, backup, cetak struk, ekspor laporan
# File ini hanya mengurus file, tidak ada input() dan tidak ada perhitungan bagi hasil

import json
import os
import shutil
from datetime import datetime

import ui_formatter as ui

# semua lokasi dibuat dari lokasi file ini, jadi program bisa dijalankan dari folder mana saja
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDER_DATA = os.path.join(BASE_DIR, "data")
FOLDER_BACKUP = os.path.join(FOLDER_DATA, "backup")
FOLDER_LAPORAN = os.path.join(BASE_DIR, "laporan")
FILE_DB = os.path.join(FOLDER_DATA, "db_panen.json")

NAMA_KELOMPOK = "Kelompok Tani"
MAKS_BACKUP = 5
LEBAR_STRUK = 40

# Tuple: urutan kolom data panen
KOLOM = ("id", "tanggal", "nama", "komoditas", "berat",
         "harga_per_kg", "total", "bagian_petani", "bagian_kas")


def _cap_waktu():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def siapkan_folder():
    for folder in (FOLDER_DATA, FOLDER_BACKUP, FOLDER_LAPORAN):
        os.makedirs(folder, exist_ok=True)


# ---------------------------------------------------------------
# BACA & TULIS DATA (JSON)
# ---------------------------------------------------------------

def _rapikan_record(item):
    # memastikan 1 data lengkap dan tipenya benar, kalau tidak: None
    if not isinstance(item, dict):
        return None
    for kolom in KOLOM:
        if kolom not in item:
            return None
    try:
        return {
            "id": str(item["id"]).strip().upper(),
            "tanggal": str(item["tanggal"]),
            "nama": str(item["nama"]),
            "komoditas": str(item["komoditas"]),
            "berat": float(item["berat"]),
            "harga_per_kg": round(float(item["harga_per_kg"])),
            "total": round(float(item["total"])),
            "bagian_petani": round(float(item["bagian_petani"])),
            "bagian_kas": round(float(item["bagian_kas"])),
        }
    except (TypeError, ValueError):
        return None


def muat_data():
    siapkan_folder()
    if not os.path.exists(FILE_DB):
        simpan_data([])
        return []

    try:
        with open(FILE_DB, "r", encoding="utf-8") as f:
            isi = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        # file rusak: salinannya disimpan dulu supaya tidak hilang, lalu mulai dari data kosong
        shutil.copy(FILE_DB, os.path.join(FOLDER_DATA, "db_panen_rusak_" + _cap_waktu() + ".json"))
        return []

    if not isinstance(isi, list):
        return []

    data = []
    id_terpakai = set()    # Set: untuk membuang ID dobel
    for item in isi:
        record = _rapikan_record(item)
        if record is None or record["id"] in id_terpakai:
            continue
        id_terpakai.add(record["id"])
        data.append(record)
    return data


def simpan_data(data):
    siapkan_folder()
    # tulis ke file sementara dulu, supaya file asli tidak rusak kalau program mati di tengah jalan
    sementara = FILE_DB + ".tmp"
    with open(sementara, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(sementara, FILE_DB)


def buat_backup():
    if not os.path.exists(FILE_DB):
        return None
    siapkan_folder()
    tujuan = os.path.join(FOLDER_BACKUP, "db_panen_" + _cap_waktu() + ".json")
    shutil.copy(FILE_DB, tujuan)

    semua = []
    for nama in os.listdir(FOLDER_BACKUP):
        if nama.startswith("db_panen_") and nama.endswith(".json"):
            semua.append(os.path.join(FOLDER_BACKUP, nama))
    semua.sort()    # nama file berisi waktu, jadi urut abjad = urut waktu

    # simpan hanya backup terbaru, yang lama dihapus
    for lama in semua[:-MAKS_BACKUP]:
        os.remove(lama)
    return tujuan


# ---------------------------------------------------------------
# STRUK PER PETANI
# ---------------------------------------------------------------

def _persen_petani(record):
    if record["total"] == 0:
        return 0
    return round(record["bagian_petani"] * 100 / record["total"])


def buat_teks_struk(record):
    garis = "=" * LEBAR_STRUK
    strip = "-" * LEBAR_STRUK
    persen_petani = _persen_petani(record)
    persen_kas = 100 - persen_petani

    def isi(label, nilai):
        return label.ljust(14) + ": " + str(nilai)

    def uang(label, nilai):
        rupiah = ui.format_rupiah(nilai)
        return label.ljust(LEBAR_STRUK - len(rupiah)) + rupiah

    baris = [
        garis,
        "STRUK PEMBAGIAN HASIL PANEN".center(LEBAR_STRUK),
        NAMA_KELOMPOK.center(LEBAR_STRUK),
        garis,
        isi("No. Panen", record["id"]),
        isi("Tanggal", record["tanggal"]),
        isi("Nama Petani", ui.potong(record["nama"], 24)),
        isi("Komoditas", ui.potong(record["komoditas"], 24)),
        isi("Berat", ui.format_berat(record["berat"]) + " kg"),
        isi("Harga per kg", ui.format_rupiah(record["harga_per_kg"])),
        strip,
        uang("Total hasil panen", record["total"]),
        uang("Bagian petani (" + str(persen_petani) + "%)", record["bagian_petani"]),
        uang("Bagian kas (" + str(persen_kas) + "%)", record["bagian_kas"]),
        garis,
        "Dicetak: " + datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Terima kasih atas kerja kerasnya!".center(LEBAR_STRUK),
        garis,
    ]
    return "\n".join(baris)


def cetak_struk(record):
    siapkan_folder()
    path = os.path.join(FOLDER_LAPORAN, "struk_" + record["id"] + ".txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(buat_teks_struk(record) + "\n")
    return path


# ---------------------------------------------------------------
# LAPORAN LENGKAP
# ---------------------------------------------------------------

def export_laporan(data, ringkasan):
    siapkan_folder()
    lebar = 104
    garis = "=" * lebar
    strip = "-" * lebar

    def isi(label, nilai):
        return label.ljust(24) + ": " + nilai

    def rekap(judul_rekap, kumpulan):
        hasil = [judul_rekap, strip]
        hasil.append("Nama".ljust(24) + "Berat (kg)".rjust(16) + "Nilai Panen".rjust(20))
        for nama, v in kumpulan.items():
            hasil.append(ui.potong(nama, 22).ljust(24)
                         + ui.format_berat(v["berat"]).rjust(16)
                         + ui.format_rupiah(v["nilai"]).rjust(20))
        hasil.append("")
        return hasil

    kolom = (("ID", 10, "kiri"), ("Tanggal", 10, "kiri"), ("Nama Petani", 16, "kiri"),
             ("Komoditas", 12, "kiri"), ("Berat (kg)", 10, "kanan"), ("Total", 13, "kanan"),
             ("Bag. Petani", 13, "kanan"), ("Bag. Kas", 13, "kanan"))

    def baris_kolom(nilai):
        return " ".join(ui.sel(v, k[1], k[2]) for v, k in zip(nilai, kolom))

    baris = [
        garis,
        "LAPORAN HASIL PANEN".center(lebar),
        NAMA_KELOMPOK.center(lebar),
        ("Dicetak: " + datetime.now().strftime("%Y-%m-%d %H:%M")).center(lebar),
        garis,
        "RINGKASAN",
        strip,
        isi("Jumlah transaksi", str(ringkasan["jumlah_transaksi"]) + " panen"),
        isi("Total berat", ui.format_berat(ringkasan["total_berat"]) + " kg"),
        isi("Total nilai panen", ui.format_rupiah(ringkasan["total_nilai"])),
        isi("Bagian seluruh petani", ui.format_rupiah(ringkasan["total_petani"])),
        isi("Kas kelompok tani", ui.format_rupiah(ringkasan["total_kas"])),
        "",
    ]
    baris += rekap("REKAP PER KOMODITAS", ringkasan["per_komoditas"])
    baris += rekap("REKAP PER PETANI", ringkasan["per_petani"])

    baris += ["DAFTAR SEMUA PANEN", strip,
              baris_kolom([k[0] for k in kolom]), strip]
    for r in data:
        baris.append(baris_kolom([
            r["id"], r["tanggal"], r["nama"], r["komoditas"],
            ui.format_berat(r["berat"]), ui.format_rupiah(r["total"]),
            ui.format_rupiah(r["bagian_petani"]), ui.format_rupiah(r["bagian_kas"]),
        ]))
    baris.append(garis)

    path = os.path.join(FOLDER_LAPORAN, "laporan_" + _cap_waktu() + ".txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(baris) + "\n")
    return path