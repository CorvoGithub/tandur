# ui_formatter.py - Bagian Maira
# Hanya mengurus tampilan terminal. Tidak ada perhitungan atau baca/tulis file.

import os
import re
import shutil
import sys
import time
from datetime import datetime

if os.name == "nt":
    os.system("")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

RESET = "\033[0m"
TEBAL = "\033[1m"
MERAH = "\033[91m"
HIJAU = "\033[92m"
KUNING = "\033[93m"
CYAN = "\033[96m"
ABU = "\033[90m"
COKELAT = "\033[33m"

LEBAR = 70
LEBAR_MINIMAL = 90

# animasi mati otomatis kalau output bukan terminal
ANIMASI = sys.stdout.isatty()

MENU = (
    ("1", "Tambah Data Panen"),
    ("2", "Lihat Semua Data"),
    ("3", "Cari Data"),
    ("4", "Urutkan Data"),
    ("5", "Ubah Data"),
    ("6", "Hapus Data"),
    ("7", "Ringkasan & Statistik"),
    ("8", "Cetak Struk"),
    ("0", "Keluar"),
)
NOMOR_MENU = tuple(m[0] for m in MENU)

# (judul, lebar, rata)
KOLOM_TABEL = (
    ("ID", 9, "kiri"),
    ("Tanggal", 10, "kiri"),
    ("Nama Petani", 16, "kiri"),
    ("Komoditas", 10, "kiri"),
    ("Berat (kg)", 10, "kanan"),
    ("Total", 13, "kanan"),
)

LOGO = (
    r"""ooooooooooooo                             .o8                      """,
    r"""8'   888   `8                            "888                      """,
    r"""     888       .oooo.   ooo. .oo.    .oooo888  oooo  oooo  oooo d8b""",
    r"""     888      `P  )88b  `888P"Y88b  d88' `888  `888  `888  `888""8P""",
    r"""     888       .oP"888   888   888  888   888   888   888   888    """,
    r"""     888      d8(  888   888   888  888   888   888   888   888    """,
    r"""    o888o     `Y888""8o o888o o888o `Y8bod88P"  `V88V"V8P' d888b   """,
)

TUNAS = (
    (TEBAL + HIJAU, "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣄⠀⠀⠀⠀⠀⠀⠀"),
    (TEBAL + HIJAU, "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⢿⣟⡆⠀⠀⠀⠀⠀⠀"),
    (TEBAL + HIJAU, "⣀⣤⣤⣤⣤⣤⣀⠀⠀⠀⢸⣇⣿⣿⡇⣀⠀⠀⠀⠀⠀"),
    (TEBAL + HIJAU, "⠹⢿⣿⣿⣷⣦⣎⢲⡀⠀⢸⣿⣿⣏⣿⠏⠀⠀⠀⠀⠀"),
    (HIJAU,         "⠀⠀⠙⢿⣿⣿⡿⣿⣿⡀⢸⣧⣿⣿⣿⢶⣶⣔⣦⢤⣀"),
    (HIJAU,         "⠀⠀⠀⠀⠙⢿⣿⣻⣿⢃⣾⢋⣿⣿⣿⣿⣿⣿⣟⡿⠋"),
    (HIJAU,         "⠀⠀⠀⠀⠀⠀⠈⠉⠹⣿⣻⡿⠿⠿⠿⡿⠿⠛⠋⠀⠀"),
    (HIJAU,         "⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"),
    (HIJAU,         "⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"),
    (HIJAU,         "⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀"),
)

TANAH = (
    (COKELAT,       "⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣶⣄⠀⠀⠀⠀⠀⠀⠀"),
    (COKELAT,       "⠀⠀⣠⣴⣶⣿⣿⣿⣿⣽⡏⣛⣿⡿⣷⣤⣄⠀⠀⠀⠀"),
    (COKELAT,       "⠀⠈⠛⠻⠿⢿⣿⣿⣿⣼⣧⣿⣿⣧⣷⠾⠿⠇⠀⠀⠀"),
)


# ---------------------------------------------------------------
# Dasar
# ---------------------------------------------------------------

def warna(teks, kode):
    return kode + teks + RESET


def sukses(teks):
    return warna("[+] " + teks, HIJAU)


def error(teks):
    return warna("[x] " + teks, MERAH)


def info(teks):
    return warna("[i] " + teks, CYAN)


def peringatan(teks):
    return warna("[!] " + teks, KUNING)


def tanya(label, default=None):
    tampil = warna(label, KUNING)
    if default is not None:
        tampil += warna(" [" + str(default) + "]", ABU)
    sys.stdout.write(tampil + warna(" > ", CYAN))
    sys.stdout.flush()
    return input()


def jeda(detik):
    if ANIMASI:
        time.sleep(detik)


def bersihkan_layar():
    if ANIMASI:
        sys.stdout.write("\033[H\033[2J\033[3J")
        sys.stdout.flush()


def tekan_enter():
    print()
    tanya("Tekan Enter untuk kembali ke menu")


# ---------------------------------------------------------------
# Format teks
# ---------------------------------------------------------------

POLA_ANSI = re.compile(r"\033\[[0-9;]*m")


def panjang_tampil(teks):
    return len(POLA_ANSI.sub("", teks))


def pad_kanan(teks, lebar):
    return teks + " " * max(0, lebar - panjang_tampil(teks))


def pad_tengah(teks, lebar):
    sisa = max(0, lebar - panjang_tampil(teks))
    return " " * (sisa // 2) + teks + " " * (sisa - sisa // 2)


def potong(teks, panjang):
    teks = str(teks)
    if len(teks) > panjang:
        return teks[:panjang - 3] + "..."
    return teks


def sel(teks, lebar, rata="kiri"):
    teks = potong(teks, lebar)
    if rata == "kanan":
        return teks.rjust(lebar)
    if rata == "tengah":
        return teks.center(lebar)
    return teks.ljust(lebar)


def format_rupiah(angka):
    return "Rp " + f"{int(angka):,}".replace(",", ".")


def format_berat(berat):
    # 1234.5 -> 1.234,50
    teks = f"{berat:,.2f}"
    return teks.replace(",", "_").replace(".", ",").replace("_", ".")


def salam():
    jam = datetime.now().hour
    if jam < 11:
        return "Selamat pagi"
    if jam < 15:
        return "Selamat siang"
    if jam < 18:
        return "Selamat sore"
    return "Selamat malam"


def lebar_cukup():
    return shutil.get_terminal_size((100, 30)).columns >= LEBAR_MINIMAL


def tengah(teks, kode=""):
    return " " * ((LEBAR - len(teks)) // 2) + kode + teks + (RESET if kode else "")


def baris_opsi(nomor, teks):
    kode = MERAH if nomor == "0" else KUNING
    return "  " + warna("[" + nomor + "]", kode) + " " + teks


# ---------------------------------------------------------------
# Kotak & judul
# ---------------------------------------------------------------

def kotak(baris, lebar=LEBAR, kode=CYAN):
    isi = lebar - 4
    print(kode + "╭" + "─" * (lebar - 2) + "╮" + RESET)
    for b in baris:
        print(kode + "│" + RESET + " " + pad_kanan(b, isi) + " " + kode + "│" + RESET)
    print(kode + "╰" + "─" * (lebar - 2) + "╯" + RESET)


def garis(lebar=LEBAR - 4):
    return warna("─" * lebar, ABU)


def judul(teks):
    print()
    print(warna("━━ " + teks + " ━━", TEBAL + HIJAU))
    print()


def subjudul(teks):
    print()
    print(warna("  " + teks, TEBAL + CYAN))


# ---------------------------------------------------------------
# Animasi
# ---------------------------------------------------------------

def ketik(teks, kode="", jeda_huruf=0.02):
    if not ANIMASI:
        print(kode + teks + RESET)
        return
    sys.stdout.write(kode)
    for huruf in teks:
        sys.stdout.write(huruf)
        sys.stdout.flush()
        time.sleep(jeda_huruf)
    sys.stdout.write(RESET + "\n")


def loading(pesan, durasi=0.8):
    if not ANIMASI:
        print(sukses(pesan + " selesai"))
        return
    putar = "|/-\\"
    akhir = time.time() + durasi
    i = 0
    while time.time() < akhir:
        sys.stdout.write("\r" + warna(putar[i % 4], CYAN) + " " + pesan + "...\033[K")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    sys.stdout.write("\r" + sukses(pesan + " selesai") + "\033[K\n")
    sys.stdout.flush()


def progress(pesan, durasi=1.0, lebar_bar=30):
    if not ANIMASI:
        print(sukses(pesan + " selesai"))
        return
    for i in range(lebar_bar + 1):
        bar = warna("█" * i, HIJAU) + warna("░" * (lebar_bar - i), ABU)
        sys.stdout.write("\r" + pesan + " " + bar + " " + str(i * 100 // lebar_bar).rjust(3) + "%")
        sys.stdout.flush()
        time.sleep(durasi / lebar_bar)
    sys.stdout.write("\n")
    sys.stdout.flush()


def gambar_tanaman(tumbuh):
    # tumbuh = jumlah baris tunas yang sudah muncul (dihitung dari bawah)
    indent = " " * ((LEBAR - len(TANAH[0][1])) // 2)
    hasil = []
    tinggi = len(TUNAS)
    for i, (kode, teks) in enumerate(TUNAS):
        if i >= tinggi - tumbuh:
            hasil.append(kode + indent + teks + RESET)
        else:
            hasil.append("")
    for kode, teks in TANAH:
        hasil.append(kode + indent + teks + RESET)
    return hasil


def animasi_tumbuh():
    if not ANIMASI:
        print("\n".join(gambar_tanaman(len(TUNAS))))
        return
    tinggi = len(TUNAS) + len(TANAH)
    for tumbuh in range(len(TUNAS) + 1):
        print("\n".join(b + "\033[K" for b in gambar_tanaman(tumbuh)))
        if tumbuh < len(TUNAS):
            sys.stdout.write("\033[" + str(tinggi) + "A")
            sys.stdout.flush()
        time.sleep(0.14)


def splash():
    bersihkan_layar()
    print()
    animasi_tumbuh()
    print()
    lebar_logo = max(len(b) for b in LOGO)
    for baris in LOGO:
        print(warna(tengah(baris.ljust(lebar_logo)), TEBAL + HIJAU))
        jeda(0.07)
    print()
    ketik(tengah("Sistem Pencatatan & Bagi Hasil Panen Kelompok Tani"), KUNING, 0.015)
    print(tengah("Oleh: Andhika, Maira, dan Raya", ABU))
    print()


def animasi_keluar():
    print()
    print("\n".join(gambar_tanaman(len(TUNAS))))
    print()
    ketik(tengah("Terima kasih sudah menggunakan Aplikasi Tandur!"), TEBAL + HIJAU)
    ketik(tengah("Sampai jumpa kembali"), KUNING)
    print()


# ---------------------------------------------------------------
# Tampilan data
# ---------------------------------------------------------------

def tampil_menu(jumlah_data):
    isi = LEBAR - 4
    baris = [
        pad_tengah(warna("M E N U   U T A M A", TEBAL + HIJAU), isi),
        pad_tengah(warna(salam() + "! " + str(jumlah_data) + " data panen tersimpan", ABU), isi),
        garis(),
    ]
    baris += [baris_opsi(nomor, nama) for nomor, nama in MENU]
    kotak(baris)


def tampil_tabel(data):
    if not data:
        print(peringatan("Belum ada data untuk ditampilkan."))
        return

    def batas(kiri, sambung, kanan):
        return warna(kiri + sambung.join("─" * (k[1] + 2) for k in KOLOM_TABEL) + kanan, ABU)

    sekat = warna("│", ABU)

    def baris(daftar_sel):
        return sekat + " " + (" " + sekat + " ").join(daftar_sel) + " " + sekat

    print(batas("┌", "┬", "┐"))
    print(baris([warna(sel(k[0], k[1], "tengah"), TEBAL + CYAN) for k in KOLOM_TABEL]))
    print(batas("├", "┼", "┤"))

    for r in data:
        nilai = (r["id"], r["tanggal"], r["nama"], r["komoditas"],
                 format_berat(r["berat"]), format_rupiah(r["total"]))
        daftar_sel = [sel(v, k[1], k[2]) for v, k in zip(nilai, KOLOM_TABEL)]
        daftar_sel[-1] = warna(daftar_sel[-1], HIJAU)
        print(baris(daftar_sel))

    print(batas("└", "┴", "┘"))
    print(warna(str(len(data)) + " data panen", ABU))


def tampil_detail(record):
    total = record["total"]
    persen_petani = round(record["bagian_petani"] * 100 / total) if total else 0
    persen_kas = 100 - persen_petani if total else 0

    lebar_bar = 40
    panjang = round(persen_petani * lebar_bar / 100)
    bar = warna("█" * panjang, HIJAU) + warna("█" * (lebar_bar - panjang), KUNING)

    def baris(label, nilai, kode=""):
        return label.ljust(15) + ": " + (warna(nilai, kode) if kode else nilai)

    kotak([
        pad_tengah(warna("DETAIL PANEN  " + record["id"], TEBAL + HIJAU), LEBAR - 4),
        garis(),
        baris("Tanggal", record["tanggal"]),
        baris("Nama petani", potong(record["nama"], 30)),
        baris("Komoditas", potong(record["komoditas"], 30)),
        baris("Berat", format_berat(record["berat"]) + " kg"),
        baris("Harga per kg", format_rupiah(record["harga_per_kg"])),
        garis(),
        baris("Total panen", format_rupiah(total), TEBAL + HIJAU),
        baris("Bagian petani", format_rupiah(record["bagian_petani"]) + " (" + str(persen_petani) + "%)", HIJAU),
        baris("Bagian kas", format_rupiah(record["bagian_kas"]) + " (" + str(persen_kas) + "%)", KUNING),
        "",
        "  " + bar,
        "  " + warna("█", HIJAU) + " Petani   " + warna("█", KUNING) + " Kas kelompok tani",
    ])


def grafik_batang(judul_grafik, rekap, lebar_bar=24):
    subjudul(judul_grafik)
    if not rekap:
        print(peringatan("Belum ada data."))
        return

    terbesar = max(v["nilai"] for v in rekap.values())
    for nama, v in rekap.items():
        panjang = round(v["nilai"] / terbesar * lebar_bar) if terbesar > 0 else 0
        if v["nilai"] > 0 and panjang == 0:
            panjang = 1
        bar = warna("█" * panjang, HIJAU) + warna("░" * (lebar_bar - panjang), ABU)
        print("  " + potong(nama, 16).ljust(16) + " " + bar + " "
              + format_rupiah(v["nilai"]).rjust(15) + "  "
              + (format_berat(v["berat"]) + " kg").rjust(13))


def tampil_ringkasan(r):
    def baris(label, nilai, kode=""):
        return label.ljust(22) + ": " + (warna(nilai, kode) if kode else nilai)

    kotak([
        pad_tengah(warna("RINGKASAN PANEN", TEBAL + HIJAU), LEBAR - 4),
        garis(),
        baris("Jumlah transaksi", str(r["jumlah_transaksi"]) + " panen"),
        baris("Total berat", format_berat(r["total_berat"]) + " kg"),
        baris("Total nilai panen", format_rupiah(r["total_nilai"]), TEBAL + HIJAU),
        baris("Bagian seluruh petani", format_rupiah(r["total_petani"]), HIJAU),
        baris("Kas kelompok tani", format_rupiah(r["total_kas"]), KUNING),
    ])

    grafik_batang("Nilai panen per komoditas", r["per_komoditas"])
    grafik_batang("Nilai panen per petani", r["per_petani"])