# Tandur

**Tandur** adalah aplikasi berbasis terminal (CLI) yang dibuat menggunakan Python untuk membantu kelompok tani mencatat transaksi panen dan menghitung pembagian hasil secara otomatis dan transparan.

---

## Tujuan Proyek

Mempermudah pengurus kelompok tani dalam mendata hasil panen anggota, menghitung porsi pendapatan secara adil (**70% untuk petani** dan **30% untuk kas kelompok tani**), memantau statistik komoditas, serta mencetak bukti transaksi tanpa perlu aplikasi rumit.

---

## Fitur Utama

* **Tambah Data Panen:** Mencatat data panen baru lengkap dengan pembuatan ID otomatis (`PN-BB-XXX`) dan perhitungan bagi hasil instan.
* **Lihat Semua Data:** Menampilkan seluruh catatan panen dalam format tabel terminal yang rapi.
* **Cari Data:** Mencari transaksi spesifik berdasarkan ID panen atau nama petani.
* **Urutkan Data:** Mengurutkan daftar panen berdasarkan tanggal, nama petani (A–Z / Z–A), total nilai, maupun berat panen.
* **Ubah & Hapus Data:** Memperbarui data panen yang sudah tersimpan (nominal bagi hasil otomatis dihitung ulang) atau menghapus data.
* **Ringkasan & Statistik:** Menampilkan rekap total transaksi, berat panen, pembagian dana, serta grafik batang per komoditas dan per petani.
* **Cetak Struk:** Menghasilkan bukti transaksi pembagian hasil panen dalam format file `.txt` di folder `laporan/`.

---

## Cara Menjalankan

Pastikan Python 3 sudah terinstal, lalu jalankan perintah berikut di terminal pada folder proyek:

```bash
python main.py