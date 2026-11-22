# main.py - Bagian Maira
# Isi: menu utama, input yang aman dari error, dan penghubung semua file
# Jalankan dengan: python main.py

import math
import os
import re
from datetime import date, datetime

import algorithms as alg
import file_handler as fh
import ui_formatter as ui

# Tuple of tuple: pilihan pengurutan (nomor, nama, kolom, menurun?)
OPSI_URUT = (
    ("1", "Nama petani (A-Z)", "nama", False),
    ("2", "Nama petani (Z-A)", "nama", True),
    ("3", "Total panen tertinggi", "total", True),
    ("4", "Total panen terendah", "total", False),
    ("5", "Berat panen terbesar", "berat", True),
    ("6", "Tanggal terbaru", "tanggal", True),
    ("7", "Tanggal terlama", "tanggal", False),
)


# ---------------------------------------------------------------
# INPUT YANG AMAN (tidak crash kalau user salah ketik)
# ---------------------------------------------------------------

def input_teks(label, default=None, maks=30):
    while True:
        isi = ui.tanya(label, default).strip()
        if isi == "" and default is not None:
            return default
        if isi == "":
            print(ui.error("Isian tidak boleh kosong!"))
            continue
        if len(isi) > maks:
            print(ui.error("Maksimal " + str(maks) + " karakter!"))
            continue
        return isi


def ke_angka(isi):
    # mengerti format Indonesia: "6.000" = 6000, "120,5" = 120.5, "Rp 6.000" = 6000
    isi = isi.strip().lower().replace("rp", "").replace(" ", "")
    if "," in isi:
        isi = isi.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", isi):
        isi = isi.replace(".", "")
    return float(isi)


def input_angka(label, default=None, minimum=0, maksimum=1_000_000_000):
    while True:
        isi = ui.tanya(label, default).strip()
        if isi == "" and default is not None:
            return default
        try:
            angka = ke_angka(isi)
        except ValueError:
            print(ui.error("Harap masukkan angka yang valid!"))
            continue
        if not math.isfinite(angka):
            print(ui.error("Harap masukkan angka yang valid!"))
        elif angka < minimum:
            print(ui.error("Angka tidak boleh kurang dari " + str(minimum) + "!"))
        elif angka > maksimum:
            print(ui.error("Angka terlalu besar! Maksimal " + str(maksimum) + "."))
        else:
            return angka


def input_tanggal(label, default=None):
    while True:
        isi = ui.tanya(label + " (TTTT-BB-HH)", default).strip()
        if isi == "" and default is not None:
            return default
        for bentuk in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(isi, bentuk).date().isoformat()
            except ValueError:
                pass
        print(ui.error("Tanggal tidak valid! Contoh: 2026-10-24 atau 24-10-2026"))


def input_pilihan(label, valid):
    while True:
        isi = ui.tanya(label).strip()
        if isi in valid:
            return isi
        print(ui.error("Pilihan tidak valid! Pilih salah satu: " + ", ".join(valid)))


def input_id(label="Masukkan ID panen (contoh: PN-10-001)"):
    return input_teks(label, maks=20).upper()


def konfirmasi(label):
    while True:
        isi = ui.tanya(label + " (y/n)").strip().lower()
        if isi in ("y", "ya"):
            return True
        if isi in ("n", "t", "tidak"):
            return False
        print(ui.error("Jawab dengan y (ya) atau n (tidak)!"))


# ---------------------------------------------------------------
# FUNGSI BANTU
# ---------------------------------------------------------------

def data_kosong(data):
    if not data:
        print(ui.peringatan("Belum ada data panen. Tambahkan dulu lewat menu 1."))
        return True
    return False


def simpan(data):
    try:
        fh.simpan_data(data)
        ui.loading("Menyimpan data", 0.6)
        return True
    except OSError as e:
        print(ui.error("Gagal menyimpan data: " + str(e)))
        return False


# ---------------------------------------------------------------
# MENU
# ---------------------------------------------------------------

def menu_tambah(data):
    ui.judul("TAMBAH DATA PANEN")
    nama = input_teks("Nama petani")
    komoditas = input_teks("Komoditas (contoh: Padi)")
    berat = input_angka("Berat panen (kg)", minimum=1, maksimum=1_000_000)
    harga = input_angka("Harga per kg (Rp)", minimum=1, maksimum=10_000_000)
    tanggal = input_tanggal("Tanggal panen", date.today().isoformat())

    record = alg.buat_record(data, tanggal, nama, komoditas, berat, harga)
    print()
    ui.tampil_detail(record)
    print()
    if not konfirmasi("Simpan data ini?"):
        print(ui.peringatan("Penambahan data dibatalkan."))
        return

    if alg.tambah_data(data, record):
        if simpan(data):
            print(ui.sukses("Data " + record["id"] + " berhasil ditambahkan!"))
    else:
        print(ui.error("ID sudah terpakai, data tidak ditambahkan!"))


def menu_lihat(data):
    ui.judul("SEMUA DATA PANEN")
    ui.tampil_tabel(data)


def menu_cari(data):
    ui.judul("CARI DATA PANEN")
    if data_kosong(data):
        return
    print("  " + ui.warna("[1]", ui.KUNING) + " Cari berdasarkan ID")
    print("  " + ui.warna("[2]", ui.KUNING) + " Cari berdasarkan nama petani")
    print()
    pilihan = input_pilihan("Pilih cara pencarian (1/2)", ("1", "2"))
    print()

    if pilihan == "1":
        id_panen = input_id()
        ui.loading("Mencari data", 0.5)
        record = alg.cari_id(data, id_panen)
        if record is None:
            print(ui.error("ID " + id_panen + " tidak ditemukan!"))
        else:
            print(ui.sukses("Data ditemukan!"))
            ui.tampil_detail(record)
    else:
        kata = input_teks("Masukkan nama petani (boleh sebagian)")
        ui.loading("Mencari data", 0.5)
        hasil = alg.cari_nama(data, kata)
        if not hasil:
            print(ui.error("Tidak ada petani dengan nama \"" + kata + "\"!"))
        else:
            print(ui.sukses("Ditemukan " + str(len(hasil)) + " data."))
            ui.tampil_tabel(hasil)


def menu_urutkan(data):
    ui.judul("URUTKAN DATA PANEN")
    if data_kosong(data):
        return
    for nomor, nama, kolom, menurun in OPSI_URUT:
        print("  " + ui.warna("[" + nomor + "]", ui.KUNING) + " " + nama)
    print()
    nomor_valid = tuple(opsi[0] for opsi in OPSI_URUT)
    pilihan = input_pilihan("Urutkan berdasarkan", nomor_valid)

    for nomor, nama, kolom, menurun in OPSI_URUT:
        if nomor == pilihan:
            ui.loading("Mengurutkan data", 0.5)
            hasil = alg.urutkan(data, kolom, menurun)
            print(ui.sukses("Diurutkan berdasarkan: " + nama))
            ui.tampil_tabel(hasil)
            print(ui.info("Ini hanya tampilan, urutan data asli tidak berubah."))


def menu_ubah(data):
    ui.judul("UBAH DATA PANEN")
    if data_kosong(data):
        return
    ui.tampil_tabel(data)
    print()
    record = alg.cari_id(data, input_id("ID panen yang akan diubah"))
    if record is None:
        print(ui.error("ID tidak ditemukan!"))
        return

    print()
    ui.tampil_detail(record)
    print(ui.info("Tekan Enter saja kalau tidak ingin mengubah isian."))
    print()
    perubahan = {
        "nama": input_teks("Nama petani", record["nama"]),
        "komoditas": input_teks("Komoditas", record["komoditas"]),
        "berat": float(input_angka("Berat panen (kg)", record["berat"], 1, 1_000_000)),
        "harga_per_kg": round(input_angka("Harga per kg (Rp)", record["harga_per_kg"], 1, 10_000_000)),
        "tanggal": input_tanggal("Tanggal panen", record["tanggal"]),
    }

    print()
    if not konfirmasi("Simpan perubahan?"):
        print(ui.peringatan("Perubahan dibatalkan."))
        return

    if alg.ubah_data(data, record["id"], perubahan) and simpan(data):
        print(ui.sukses("Data " + record["id"] + " berhasil diubah!"))
        ui.tampil_detail(record)


def menu_hapus(data):
    ui.judul("HAPUS DATA PANEN")
    if data_kosong(data):
        return
    ui.tampil_tabel(data)
    print()
    record = alg.cari_id(data, input_id("ID panen yang akan dihapus"))
    if record is None:
        print(ui.error("ID tidak ditemukan!"))
        return

    print()
    ui.tampil_detail(record)
    print()
    print(ui.peringatan("Data yang dihapus tidak bisa dikembalikan!"))
    if not konfirmasi("Yakin ingin menghapus data ini?"):
        print(ui.peringatan("Penghapusan dibatalkan."))
        return

    dihapus = alg.hapus_data(data, record["id"])
    if dihapus is not None and simpan(data):
        print(ui.sukses("Data " + dihapus["id"] + " (" + dihapus["nama"] + ") berhasil dihapus!"))


def menu_ringkasan(data):
    ui.judul("RINGKASAN & STATISTIK")
    if data_kosong(data):
        return
    ui.loading("Menghitung ringkasan", 0.6)
    print()
    ui.tampil_ringkasan(alg.ringkasan(data))


def menu_struk(data):
    ui.judul("CETAK STRUK PETANI")
    if data_kosong(data):
        return
    ui.tampil_tabel(data)
    print()
    record = alg.cari_id(data, input_id("ID panen yang akan dicetak"))
    if record is None:
        print(ui.error("ID tidak ditemukan!"))
        return

    try:
        path = fh.cetak_struk(record)
    except OSError as e:
        print(ui.error("Gagal membuat struk: " + str(e)))
        return

    ui.loading("Mencetak struk", 0.8)
    print()
    ui.kotak(fh.buat_teks_struk(record).split("\n"), fh.LEBAR_STRUK + 4, ui.KUNING)
    print()
    print(ui.sukses("Struk tersimpan di: " + os.path.relpath(path, fh.BASE_DIR)))


def menu_ekspor(data):
    ui.judul("EKSPOR LAPORAN")
    if data_kosong(data):
        return
    try:
        path = fh.export_laporan(data, alg.ringkasan(data))
    except OSError as e:
        print(ui.error("Gagal membuat laporan: " + str(e)))
        return

    ui.loading("Menyusun laporan", 1.0)
    print(ui.sukses("Laporan tersimpan di: " + os.path.relpath(path, fh.BASE_DIR)))


# Dictionary: nomor menu -> fungsi yang dijalankan
AKSI = {
    "1": menu_tambah,
    "2": menu_lihat,
    "3": menu_cari,
    "4": menu_urutkan,
    "5": menu_ubah,
    "6": menu_hapus,
    "7": menu_ringkasan,
    "8": menu_struk,
    "9": menu_ekspor,
}


# ---------------------------------------------------------------
# PROGRAM UTAMA
# ---------------------------------------------------------------

def main():
    ui.splash()
    if not ui.lebar_cukup():
        print(ui.peringatan("Jendela terminal terlalu sempit, tabel bisa berantakan."))
        print(ui.peringatan("Perlebar jendela terminal (minimal 95 kolom)."))
        print()

    ui.progress("Memuat data", 1.0)
    try:
        data = fh.muat_data()
        fh.buat_backup()
    except OSError as e:
        print(ui.error("Gagal membuka file data: " + str(e)))
        return
    print(ui.sukses(str(len(data)) + " data panen berhasil dimuat."))
    ui.jeda(0.8)

    while True:
        ui.bersihkan_layar()
        ui.tampil_menu(len(data))
        print()
        pilihan = input_pilihan("Pilih menu (0-9)", ui.NOMOR_MENU)

        if pilihan == "0":
            print()
            if konfirmasi("Yakin ingin keluar?"):
                break
            continue

        ui.bersihkan_layar()
        try:
            AKSI[pilihan](data)
        except Exception as e:
            print(ui.error("Terjadi kesalahan: " + str(e)))
        ui.tekan_enter()

    ui.bersihkan_layar()
    ui.animasi_keluar()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
        print(ui.info("Program dihentikan. Data yang sudah disimpan aman."))