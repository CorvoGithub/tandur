# persentase bagi hasil
BAGI_HASIL = (0.7, 0.3)   # (petani, kas kelompok tani)

KOLOM_URUT = ("id", "tanggal", "nama", "komoditas", "berat",
              "harga_per_kg", "total", "bagian_petani", "bagian_kas")

KOLOM_BOLEH_UBAH = ("tanggal", "nama", "komoditas", "berat", "harga_per_kg")


def hitung_bagi_hasil(berat, harga_per_kg):

    total = round(berat * harga_per_kg)
    bagian_petani = round(total * BAGI_HASIL[0])
    bagian_kas = total - bagian_petani
    return {
        "total": total,
        "bagian_petani": bagian_petani,
        "bagian_kas": bagian_kas,
    }

def buat_id_baru(data, tanggal):
    bulan = tanggal[5:7]            # "2026-10-24" -> "10"
    awalan = "PN-" + bulan + "-"    # "PN-10-"

    # pakai nomor TERBESAR + 1, bukan jumlah data + 1,
    # supaya ID tidak dobel kalau ada data yang pernah dihapus
    nomor_terbesar = 0
    for record in data:
        if record["id"].startswith(awalan):
            try:
                nomor = int(record["id"][len(awalan):])
            except ValueError:
                continue
            if nomor > nomor_terbesar:
                nomor_terbesar = nomor

    return awalan + str(nomor_terbesar + 1).zfill(3)    # 5 -> "005"


def buat_record(data, tanggal, nama, komoditas, berat, harga_per_kg):
    # merakit 1 data panen lengkap, dipakai di menu Tambah Panen
    record = {
        "id": buat_id_baru(data, tanggal),
        "tanggal": tanggal,
        "nama": nama.strip(),
        "komoditas": komoditas.strip(),
        "berat": float(berat),
        "harga_per_kg": round(harga_per_kg),
    }
    record.update(hitung_bagi_hasil(record["berat"], record["harga_per_kg"]))
    return record


def tambah_data(data, record):
    # Set berisi semua ID yang sudah terpakai, untuk cek duplikat
    id_terpakai = set()
    for r in data:
        id_terpakai.add(r["id"])

    if record["id"] in id_terpakai:
        return False

    data.append(record)
    return True


def _cari_index(data, id_panen):
    id_panen = id_panen.strip().upper()
    for i in range(len(data)):
        if data[i]["id"] == id_panen:
            return i
    return -1


def ubah_data(data, id_panen, perubahan):
    i = _cari_index(data, id_panen)
    if i == -1:
        return False

    record = data[i]
    for kolom in KOLOM_BOLEH_UBAH:
        if kolom in perubahan:
            record[kolom] = perubahan[kolom]

    # hitung ulang karena berat atau harga mungkin berubah
    record.update(hitung_bagi_hasil(record["berat"], record["harga_per_kg"]))
    return True


def hapus_data(data, id_panen):
    # mengembalikan data yang dihapus, atau None kalau ID tidak ada
    i = _cari_index(data, id_panen)
    if i == -1:
        return None
    return data.pop(i)


def _nilai_urut(record, kunci):
    nilai = record[kunci]
    if isinstance(nilai, str):
        return nilai.lower()    # supaya huruf besar/kecil tidak mempengaruhi urutan
    return nilai


def _quick_sort(daftar, kunci):
    # Quick Sort: pilih 1 pivot, bagi jadi kiri (lebih kecil), tengah (sama),
    # kanan (lebih besar), lalu urutkan kiri dan kanan dengan cara yang sama (rekursi)
    if len(daftar) <= 1:
        return daftar

    pivot = _nilai_urut(daftar[len(daftar) // 2], kunci)
    kiri = [r for r in daftar if _nilai_urut(r, kunci) < pivot]
    tengah = [r for r in daftar if _nilai_urut(r, kunci) == pivot]
    kanan = [r for r in daftar if _nilai_urut(r, kunci) > pivot]

    return _quick_sort(kiri, kunci) + tengah + _quick_sort(kanan, kunci)


def urutkan(data, kunci, menurun=False):
    if kunci not in KOLOM_URUT:
        raise ValueError("Kolom tidak dikenal: " + str(kunci))

    # list(data) = salinan, jadi list asli tidak berubah
    hasil = _quick_sort(list(data), kunci)
    if menurun:
        hasil = hasil[::-1]
    return hasil


def cari_id(data, id_panen):
    # Binary Search: data harus sudah urut, jadi diurutkan dulu (salinan) berdasarkan ID
    id_panen = id_panen.strip().upper()
    terurut = _quick_sort(list(data), "id")

    kiri = 0
    kanan = len(terurut) - 1
    while kiri <= kanan:
        tengah = (kiri + kanan) // 2
        id_tengah = terurut[tengah]["id"]

        if id_tengah == id_panen:
            return terurut[tengah]
        elif id_panen < id_tengah:
            kanan = tengah - 1
        else:
            kiri = tengah + 1
    return None


def cari_nama(data, kata):
    # Linear Search: cek satu per satu dari awal, boleh sebagian nama
    kata = kata.strip().lower()
    hasil = []
    if kata == "":
        return hasil

    for record in data:
        if kata in record["nama"].lower():
            hasil.append(record)
    return hasil


def _tambah_rekap(rekap, nama, record):
    nama = nama.strip().title()    # "slamet" dan "Slamet" dianggap sama
    if nama not in rekap:
        rekap[nama] = {"berat": 0.0, "nilai": 0}
    rekap[nama]["berat"] += record["berat"]
    rekap[nama]["nilai"] += record["total"]


def ringkasan(data):
    hasil = {
        "jumlah_transaksi": len(data),
        "total_berat": 0.0,
        "total_nilai": 0,
        "total_petani": 0,
        "total_kas": 0,
        "per_komoditas": {},
        "per_petani": {},
    }

    for r in data:
        hasil["total_berat"] += r["berat"]
        hasil["total_nilai"] += r["total"]
        hasil["total_petani"] += r["bagian_petani"]
        hasil["total_kas"] += r["bagian_kas"]
        _tambah_rekap(hasil["per_komoditas"], r["komoditas"], r)
        _tambah_rekap(hasil["per_petani"], r["nama"], r)

    hasil["total_berat"] = round(hasil["total_berat"], 2)
    for rekap in (hasil["per_komoditas"], hasil["per_petani"]):
        for nama in rekap:
            rekap[nama]["berat"] = round(rekap[nama]["berat"], 2)

    return hasil


# Tes sendiri: jalankan "python algorithms.py" (butuh dummy_data.py di folder yang sama)
if __name__ == "__main__":
    from dummy_data import data_baru

    data = data_baru()

    assert hitung_bagi_hasil(120.5, 6000) == {
        "total": 723000, "bagian_petani": 506100, "bagian_kas": 216900}

    # PN-10-003 sengaja tidak ada di dummy, jadi harus PN-10-005
    assert buat_id_baru(data, "2026-10-24") == "PN-10-005"
    assert buat_id_baru(data, "2026-11-01") == "PN-11-001"

    baru = buat_record(data, "2026-10-24", "  Maman ", "Padi", 120.5, 6000)
    assert baru["id"] == "PN-10-005" and baru["nama"] == "Maman"
    assert baru["total"] == 723000
    assert tambah_data(data, baru) is True
    assert len(data) == 13
    assert tambah_data(data, baru) is False
    assert len(data) == 13

    assert ubah_data(data, "PN-08-001", {"berat": 100.0}) is True
    assert cari_id(data, "PN-08-001")["total"] == 600000
    assert ubah_data(data, "PN-99-999", {"berat": 1.0}) is False

    dihapus = hapus_data(data, "PN-08-002")
    assert dihapus is not None and dihapus["id"] == "PN-08-002"
    assert hapus_data(data, "PN-08-002") is None
    assert len(data) == 12

    assert cari_id(data, "PN-09-003")["nama"] == "Agus Prasetyo"
    assert cari_id(data, "pn-09-003") is not None
    assert cari_id(data, "PN-99-999") is None

    assert len(cari_nama(data, "slamet")) == 2
    assert len(cari_nama(data, "SITI")) == 1    # PN-08-002 sudah dihapus di atas
    assert cari_nama(data, "") == []

    urutan_awal = [r["id"] for r in data]
    termahal = urutkan(data, "total", menurun=True)
    assert termahal[0]["total"] == max(r["total"] for r in data)
    assert [r["id"] for r in data] == urutan_awal    # list asli tidak berubah
    assert urutkan(data, "nama")[0]["nama"] == "Agus Prasetyo"
    totals = [r["total"] for r in urutkan(data, "total")]
    assert all(totals[i] <= totals[i + 1] for i in range(len(totals) - 1))

    rk = ringkasan(data)
    assert rk["jumlah_transaksi"] == len(data)
    assert rk["total_nilai"] == sum(r["total"] for r in data)
    assert rk["total_nilai"] == rk["total_petani"] + rk["total_kas"]
    assert "Padi" in rk["per_komoditas"] and "Slamet Riyadi" in rk["per_petani"]

    print("OK - semua tes algorithms.py lulus")