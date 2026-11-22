# ui_formatter.py - Bagian Maira
# Isi: tampilan terminal (warna, ASCII art, animasi, tabel, format teks)
# File ini hanya mengurus tampilan, tidak ada perhitungan atau baca/tulis file data

import os
import re
import shutil
import sys
import time
from datetime import datetime

if os.name == "nt":
    os.system("")    # mengaktifkan warna ANSI di terminal Windows

try:
    sys.stdout.reconfigure(encoding="utf-8")    # supaya karakter kotak/blok tampil benar
except (AttributeError, ValueError):
    pass

# ---------------------------------------------------------------
# KODE WARNA ANSI
# ---------------------------------------------------------------

RESET = "\033[0m"
TEBAL = "\033[1m"
MERAH = "\033[91m"
HIJAU = "\033[92m"
KUNING = "\033[93m"
CYAN = "\033[96m"
UNGU = "\033[95m"
ABU = "\033[90m"
COKELAT = "\033[33m"

LEBAR = 68

# animasi otomatis mati kalau output bukan terminal
ANIMASI_AKTIF = getattr(sys.stdout, "isatty", lambda: False)()

# Tuple of tuple: daftar menu utama (nomor, nama)
MENU = (
    ("1", "Tambah Data Panen"),
    ("2", "Lihat Semua Data Panen"),
    ("3", "Cari Data Panen"),
    ("4", "Urutkan Data Panen"),
    ("5", "Ubah Data Panen"),
    ("6", "Hapus Data Panen"),
    ("7", "Ringkasan & Statistik"),
    ("8", "Cetak Struk Petani"),
    ("9", "Ekspor Laporan"),
    ("0", "Keluar"),
)
NOMOR_MENU = tuple(nomor for nomor, nama in MENU)

# kolom tabel: (judul, lebar, rata)
KOLOM_TABEL = (
    ("No", 3, "kanan"),
    ("ID", 9, "kiri"),
    ("Tanggal", 10, "kiri"),
    ("Nama Petani", 14, "kiri"),
    ("Komoditas", 12, "kiri"),
    ("Berat (kg)", 10, "kanan"),
    ("Total", 13, "kanan"),
)

# ---------------------------------------------------------------
# ASCII ART
# ---------------------------------------------------------------

LOGO = (
    r"""ooooooooooooo                             .o8                      """,
    r"""8'   888   `8                            "888                      """,
    r"""     888       .oooo.   ooo. .oo.    .oooo888  oooo  oooo  oooo d8b""",
    r"""     888      `P  )88b  `888P"Y88b  d88' `888  `888  `888  `888""8P""",
    r"""     888       .oP"888   888   888  888   888   888   888   888    """,
    r"""     888      d8(  888   888   888  888   888   888   888   888    """,
    r"""    o888o     `Y888""8o o888o o888o `Y8bod88P"  `V88V"V8P' d888b   """,
)

# tunas digambar dari atas ke bawah, tiap baris punya warna sendiri
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
# FUNGSI DASAR
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
    # print + input dipisah supaya warna tidak mengganggu input()
    tampil = warna(label, KUNING)
    if default is not None:
        tampil += warna(" [" + str(default) + "]", ABU)
    sys.stdout.write(tampil + warna(" > ", CYAN))
    sys.stdout.flush()
    return input()


def jeda(detik):
    if ANIMASI_AKTIF:
        time.sleep(detik)


def bersihkan_layar():
    if ANIMASI_AKTIF:
        sys.stdout.write("\033[H\033[2J\033[3J")
        sys.stdout.flush()


def tekan_enter():
    print()
    tanya("Tekan Enter untuk kembali ke menu")


# ---------------------------------------------------------------
# FORMAT TEKS
# ---------------------------------------------------------------

POLA_ANSI = re.compile(r"\033\[[0-9;]*m")


def panjang_tampil(teks):
    # panjang teks yang terlihat (kode warna tidak dihitung)
    return len(POLA_ANSI.sub("", teks))


def pad_kanan(teks, lebar):
    return teks + " " * max(0, lebar - panjang_tampil(teks))


def pad_tengah(teks, lebar):
    sisa = max(0, lebar - panjang_tampil(teks))
    kiri = sisa // 2
    return " " * kiri + teks + " " * (sisa - kiri)


def potong(teks, panjang):
    teks = str(teks)
    if len(teks) > panjang:
        return teks[:panjang - 3] + "..."
    return teks


def sel(teks, lebar, rata="kiri"):
    # meratakan teks dalam kolom selebar 'lebar'
    teks = potong(teks, lebar)
    if rata == "kanan":
        return teks.rjust(lebar)
    if rata == "tengah":
        return teks.center(lebar)
    return teks.ljust(lebar)


def format_rupiah(angka):
    # 1234567 -> "Rp 1.234.567"
    return "Rp " + f"{int(angka):,}".replace(",", ".")


def format_berat(berat):
    # 1234.5 -> "1.234,50" (titik untuk ribuan, koma untuk desimal)
    teks = f"{berat:,.2f}"
    return teks.replace(",", "_").replace(".", ",").replace("_", ".")


def salam():
    jam = datetime.now().hour
    if jam < 11:
        return "Selamat pagi"
    elif jam < 15:
        return "Selamat siang"
    elif jam < 18:
        return "Selamat sore"
    return "Selamat malam"


def lebar_cukup(minimal=95):
    return shutil.get_terminal_size((100, 30)).columns >= minimal


# ---------------------------------------------------------------
# KOTAK & JUDUL
# ---------------------------------------------------------------

def kotak(baris, lebar=LEBAR, kode=CYAN):
    isi = lebar - 4
    print(kode + "╔" + "═" * (lebar - 2) + "╗" + RESET)
    for b in baris:
        print(kode + "║" + RESET + " " + pad_kanan(b, isi) + " " + kode + "║" + RESET)
    print(kode + "╚" + "═" * (lebar - 2) + "╝" + RESET)


def judul(teks):
    print()
    print(warna((" " + teks + " ").center(LEBAR, "═"), TEBAL + HIJAU))
    print()


def subjudul(teks):
    print()
    print(warna("  " + teks, TEBAL + CYAN))


# ---------------------------------------------------------------
# ANIMASI
# ---------------------------------------------------------------

def ketik(teks, jeda_huruf=0.02, kode="", indent=""):
    # efek mesin ketik: huruf muncul satu per satu
    if not ANIMASI_AKTIF:
        print(indent + kode + teks + RESET)
        return
    sys.stdout.write(indent + kode)
    for huruf in teks:
        sys.stdout.write(huruf)
        sys.stdout.flush()
        time.sleep(jeda_huruf)
    sys.stdout.write(RESET + "\n")


def loading(pesan, durasi=0.8):
    if not ANIMASI_AKTIF:
        print(sukses(pesan + " selesai"))
        return
    putaran = "|/-\\"
    selesai = time.time() + durasi
    i = 0
    while time.time() < selesai:
        sys.stdout.write("\r" + warna(putaran[i % 4], CYAN) + " " + pesan + "...\033[K")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    sys.stdout.write("\r" + sukses(pesan + " selesai") + "\033[K\n")
    sys.stdout.flush()


def progress(pesan, durasi=1.0, lebar_bar=30):
    if not ANIMASI_AKTIF:
        print(sukses(pesan + " selesai"))
        return
    for i in range(lebar_bar + 1):
        persen = int(i * 100 / lebar_bar)
        bar = warna("█" * i, HIJAU) + warna("░" * (lebar_bar - i), ABU)
        sys.stdout.write("\r" + pesan + " " + bar + " " + str(persen).rjust(3) + "%")
        sys.stdout.flush()
        time.sleep(durasi / lebar_bar)
    sys.stdout.write("\n")
    sys.stdout.flush()


def gambar_tanaman(tampil, indent=" " * ((LEBAR - len(TANAH[0][1])) // 2)):
    # tampil = jumlah baris tunas yang sudah "tumbuh" (dihitung dari bawah)
    baris = []
    tinggi = len(TUNAS)
    for i in range(tinggi):
        kode, teks = TUNAS[i]
        if i >= tinggi - tampil:
            baris.append(kode + indent + teks + RESET)
        else:
            baris.append("")
    for kode, teks in TANAH:
        baris.append(kode + indent + teks + RESET)
    return baris


def animasi_tumbuh():
    total_baris = len(TUNAS) + len(TANAH)
    if not ANIMASI_AKTIF:
        print("\n".join(gambar_tanaman(len(TUNAS))))
        return

    for tampil in range(len(TUNAS) + 1):
        print("\n".join(b + "\033[K" for b in gambar_tanaman(tampil)))
        if tampil < len(TUNAS):
            # naik ke baris paling atas, lalu gambar ulang di tempat yang sama
            sys.stdout.write("\033[" + str(total_baris) + "A")
            sys.stdout.flush()
        time.sleep(0.14)


def splash():
    bersihkan_layar()
    print()
    animasi_tumbuh()
    print()
    for baris in LOGO:
        print(warna(baris.center(LEBAR), TEBAL + HIJAU))
        jeda(0.07)
    print()
    teks = "Sistem Pencatatan & Bagi Hasil Panen Kelompok Tani"
    ketik(teks, 0.015, KUNING, " " * ((LEBAR - len(teks)) // 2))
    print(warna("Oleh: Andhika, Maira, dan Raya".center(LEBAR), ABU))
    print()


def animasi_keluar():
    print()
    print("\n".join(gambar_tanaman(len(TUNAS))))
    print()
    for teks, kode in (("Terima kasih sudah menggunakan Aplikasi Tandur!", TEBAL + HIJAU),
                       ("Sampai jumpa kembali", KUNING)):
        ketik(teks, 0.02, kode, " " * ((LEBAR - len(teks)) // 2))
    print()


# ---------------------------------------------------------------
# TAMPILAN DATA
# ---------------------------------------------------------------

def tampil_menu(jumlah_data):
    isi = LEBAR - 4
    baris = [
        pad_tengah(warna("M E N U   U T A M A", TEBAL + HIJAU), isi),
        pad_tengah(warna(salam() + "! " + str(jumlah_data) + " data panen tersimpan", ABU), isi),
        warna("─" * isi, ABU),
    ]
    for nomor, nama in MENU:
        kode = MERAH if nomor == "0" else KUNING
        baris.append("   " + warna("[" + nomor + "]", kode) + "  " + nama)
    kotak(baris, LEBAR, CYAN)


def tampil_tabel(data):
    if not data:
        print(peringatan("Belum ada data untuk ditampilkan."))
        return

    def garis_tabel(kiri, tengah, kanan):
        potongan = ["─" * (k[1] + 2) for k in KOLOM_TABEL]
        return warna(kiri + tengah.join(potongan) + kanan, ABU)

    pemisah = warna("│", ABU)

    def baris_tabel(daftar_sel):
        return pemisah + " " + (" " + pemisah + " ").join(daftar_sel) + " " + pemisah

    print(garis_tabel("┌", "┬", "┐"))
    header = [warna(sel(k[0], k[1], "tengah"), TEBAL + CYAN) for k in KOLOM_TABEL]
    print(baris_tabel(header))
    print(garis_tabel("├", "┼", "┤"))

    for nomor, r in enumerate(data, 1):
        nilai = (nomor, r["id"], r["tanggal"], r["nama"], r["komoditas"],
                 format_berat(r["berat"]), format_rupiah(r["total"]))
        daftar_sel = [sel(v, k[1], k[2]) for v, k in zip(nilai, KOLOM_TABEL)]
        daftar_sel[-1] = warna(daftar_sel[-1], HIJAU)
        print(baris_tabel(daftar_sel))

    print(garis_tabel("└", "┴", "┘"))
    print(warna("Menampilkan " + str(len(data)) + " data panen", ABU))


def tampil_detail(record):
    isi = LEBAR - 4
    total = record["total"]
    persen_petani = round(record["bagian_petani"] * 100 / total) if total else 0
    persen_kas = 100 - persen_petani if total else 0

    lebar_bar = 40
    panjang_petani = round(persen_petani / 100 * lebar_bar)
    bar = (warna("█" * panjang_petani, HIJAU)
           + warna("█" * (lebar_bar - panjang_petani), KUNING))

    def baris(label, nilai, kode=""):
        if kode:
            nilai = warna(nilai, kode)
        return label.ljust(15) + ": " + nilai

    kotak([
        pad_tengah(warna("DETAIL PANEN  " + record["id"], TEBAL + HIJAU), isi),
        warna("─" * isi, ABU),
        baris("Tanggal", record["tanggal"]),
        baris("Nama petani", potong(record["nama"], 30)),
        baris("Komoditas", potong(record["komoditas"], 30)),
        baris("Berat", format_berat(record["berat"]) + " kg"),
        baris("Harga per kg", format_rupiah(record["harga_per_kg"])),
        warna("─" * isi, ABU),
        baris("Total panen", format_rupiah(total), TEBAL + HIJAU),
        baris("Bagian petani", format_rupiah(record["bagian_petani"]) + " (" + str(persen_petani) + "%)", HIJAU),
        baris("Bagian kas", format_rupiah(record["bagian_kas"]) + " (" + str(persen_kas) + "%)", KUNING),
        "",
        "  " + bar,
        "  " + warna("█", HIJAU) + " Petani    " + warna("█", KUNING) + " Kas kelompok tani",
    ], LEBAR, CYAN)


def grafik_batang(judul_grafik, rekap, lebar_bar=24):
    subjudul(judul_grafik)
    if not rekap:
        print(peringatan("Belum ada data."))
        return

    nilai_terbesar = max(v["nilai"] for v in rekap.values())
    for nama, v in rekap.items():
        panjang = round(v["nilai"] / nilai_terbesar * lebar_bar) if nilai_terbesar > 0 else 0
        if v["nilai"] > 0 and panjang == 0:
            panjang = 1
        bar = warna("█" * panjang, HIJAU) + warna("░" * (lebar_bar - panjang), ABU)
        print("  " + potong(nama, 16).ljust(16) + " " + bar + " "
              + format_rupiah(v["nilai"]).rjust(15) + "  "
              + (format_berat(v["berat"]) + " kg").rjust(13))


def tampil_ringkasan(r):
    isi = LEBAR - 4

    def baris(label, nilai, kode=""):
        if kode:
            nilai = warna(nilai, kode)
        return label.ljust(22) + ": " + nilai

    kotak([
        pad_tengah(warna("RINGKASAN PANEN", TEBAL + HIJAU), isi),
        warna("─" * isi, ABU),
        baris("Jumlah transaksi", str(r["jumlah_transaksi"]) + " panen"),
        baris("Total berat", format_berat(r["total_berat"]) + " kg"),
        baris("Total nilai panen", format_rupiah(r["total_nilai"]), TEBAL + HIJAU),
        baris("Bagian seluruh petani", format_rupiah(r["total_petani"]), HIJAU),
        baris("Kas kelompok tani", format_rupiah(r["total_kas"]), KUNING),
    ], LEBAR, CYAN)

    grafik_batang("Nilai panen per komoditas", r["per_komoditas"])
    grafik_batang("Nilai panen per petani", r["per_petani"])