"""
dummy_data.py - DATA CONTOH BERSAMA (patokan) untuk project Panen Kelompok Tani

Cara pakai (di file kamu sendiri, taruh dummy_data.py di folder yang sama):

    from dummy_data import data_baru
    data = data_baru()      # salinan baru, aman diubah-ubah (tambah/hapus/urutkan)

JANGAN edit file ini sendiri. Kalau mau ubah, kabari grup dulu, lalu kirim ke semua.

Hal-hal yang sengaja disiapkan buat ngetes:
- "Slamet" dan "Slamet Riyadi" -> cari_nama("slamet") harus nemu 2 data
- "Siti Aminah" dan "Budi Santoso" muncul 2 kali -> buat tes rekap per petani
- Padi, Jagung, Cabai muncul lebih dari sekali -> buat tes rekap per komoditas
- ID PN-10-003 sengaja TIDAK ADA (anggap sudah dihapus), jadi
  buat_id_baru(data, "2026-10-24") harus menghasilkan "PN-10-005", BUKAN "PN-10-004"
- Ada berat desimal (98.75, 175.25) buat tes perhitungan
"""

import copy

# DATA DUMMY & KOLOM (urutan harus sama dengan tabel di database)
DUMMY = [
    {"id": "PN-08-001", "tanggal": "2026-08-05", "nama": "Slamet", "komoditas": "Padi",
     "berat": 150.0, "harga_per_kg": 6000, "total": 900000,
     "bagian_petani": 630000, "bagian_kas": 270000},
    {"id": "PN-08-002", "tanggal": "2026-08-12", "nama": "Siti Aminah", "komoditas": "Jagung",
     "berat": 85.5, "harga_per_kg": 4500, "total": 384750,
     "bagian_petani": 269325, "bagian_kas": 115425},
    {"id": "PN-08-003", "tanggal": "2026-08-20", "nama": "Budi Santoso", "komoditas": "Cabai",
     "berat": 40.0, "harga_per_kg": 35000, "total": 1400000,
     "bagian_petani": 980000, "bagian_kas": 420000},
    {"id": "PN-08-004", "tanggal": "2026-08-27", "nama": "Wahyu Nugroho", "komoditas": "Padi",
     "berat": 98.75, "harga_per_kg": 6000, "total": 592500,
     "bagian_petani": 414750, "bagian_kas": 177750},
    {"id": "PN-09-001", "tanggal": "2026-09-03", "nama": "Slamet Riyadi", "komoditas": "Singkong",
     "berat": 200.0, "harga_per_kg": 1800, "total": 360000,
     "bagian_petani": 252000, "bagian_kas": 108000},
    {"id": "PN-09-002", "tanggal": "2026-09-10", "nama": "Dewi Lestari", "komoditas": "Tomat",
     "berat": 60.5, "harga_per_kg": 8000, "total": 484000,
     "bagian_petani": 338800, "bagian_kas": 145200},
    {"id": "PN-09-003", "tanggal": "2026-09-15", "nama": "Agus Prasetyo", "komoditas": "Padi",
     "berat": 175.25, "harga_per_kg": 6200, "total": 1086550,
     "bagian_petani": 760585, "bagian_kas": 325965},
    {"id": "PN-09-004", "tanggal": "2026-09-22", "nama": "Siti Aminah", "komoditas": "Cabai",
     "berat": 32.0, "harga_per_kg": 38000, "total": 1216000,
     "bagian_petani": 851200, "bagian_kas": 364800},
    {"id": "PN-09-005", "tanggal": "2026-09-28", "nama": "Joko Susilo", "komoditas": "Jagung",
     "berat": 110.0, "harga_per_kg": 4400, "total": 484000,
     "bagian_petani": 338800, "bagian_kas": 145200},
    {"id": "PN-10-001", "tanggal": "2026-10-02", "nama": "Sri Wahyuni", "komoditas": "Bawang Merah",
     "berat": 55.0, "harga_per_kg": 30000, "total": 1650000,
     "bagian_petani": 1155000, "bagian_kas": 495000},
    {"id": "PN-10-002", "tanggal": "2026-10-07", "nama": "Rahmat Hidayat", "komoditas": "Kacang Tanah",
     "berat": 70.5, "harga_per_kg": 15000, "total": 1057500,
     "bagian_petani": 740250, "bagian_kas": 317250},
    {"id": "PN-10-004", "tanggal": "2026-10-14", "nama": "Budi Santoso", "komoditas": "Jagung",
     "berat": 120.0, "harga_per_kg": 4300, "total": 516000,
     "bagian_petani": 361200, "bagian_kas": 154800},
]

KOLOM = ("id", "tanggal", "nama", "komoditas", "berat",
         "harga_per_kg", "total", "bagian_petani", "bagian_kas")


# PAKAI FUNGSI INI KALAU MAU AMBIL DATA DUMMY
def data_baru():
    """Mengembalikan salinan DUMMY supaya data asli tidak ikut berubah."""
    return copy.deepcopy(DUMMY)


# IGNORE INI, CUMAN BUAT CEK VALID DATA DUMMY
if __name__ == "__main__":
    # Cek: run "python dummy_data.py", harus muncul "OK"
    ids = set()
    for r in DUMMY:
        assert tuple(r.keys()) == KOLOM, "urutan/nama kolom salah: " + r["id"]
        assert r["id"] not in ids, "ID dobel: " + r["id"]
        ids.add(r["id"])
        assert isinstance(r["berat"], float)
        assert r["total"] == round(r["berat"] * r["harga_per_kg"]), "total salah: " + r["id"]
        assert r["bagian_petani"] == round(r["total"] * 0.7), "bagian petani salah: " + r["id"]
        assert r["bagian_kas"] == r["total"] - r["bagian_petani"], "bagian kas salah: " + r["id"]
    print("OK -", len(DUMMY), "data, semua valid")