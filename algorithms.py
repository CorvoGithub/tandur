# algorithms.py: hitung bagi hasil, tambah/ubah/hapus, cari, urutkan, ringkasan

BAGI_HASIL = (0.7, 0.3)   # (bagian petani, bagian kas kelompok tani)
KOLOM_URUT = ("id", "tanggal", "nama", "komoditas", "berat",
              "harga_per_kg", "total", "bagian_petani", "bagian_kas")
KOLOM_BOLEH_UBAH = ("tanggal", "nama", "komoditas", "berat", "harga_per_kg")


def hitung_bagi_hasil(berat, harga_per_kg):
    # /hitung pembagian penghasilan petani & kas
    total = round(berat * harga_per_kg)
    bagian_petani = round(total * BAGI_HASIL[0])
    bagian_kas = total - bagian_petani
    return {
        "total": total,
        "bagian_petani": bagian_petani,
        "bagian_kas": bagian_kas,
    }

def buat_id_baru(data, tanggal):
    # /buat id baru buat suatu record
    bulan = tanggal[5:7]            # 2026-10-24 -> 10
    awalan = "PN-" + bulan + "-"    # PN-(bulan)-(urutan)

    nomor_terbesar = 0
    for record in data:
        if record["id"].startswith(awalan):
            try:
                nomor = int(record["id"][len(awalan):])
            except ValueError:
                continue
            nomor_terbesar = max(nomor_terbesar, nomor)

    return awalan + str(nomor_terbesar + 1).zfill(3)    # zfill: 5 -> 005

def buat_record(data, tanggal, nama, komoditas, berat, harga_per_kg):
    # /buat record baru buat nanti tambah ke list data
    record = {
        "id": buat_id_baru(data, tanggal),
        "tanggal": tanggal,
        "nama": nama.strip(),
        "komoditas": komoditas.strip(),
        "berat": float(berat),
        "harga_per_kg": round(harga_per_kg),
    }
    # tambah key total, bagian petani, sama bagian kas ke dictionary record
    record.update(hitung_bagi_hasil(record["berat"], record["harga_per_kg"]))
    return record

def tambah_data(data, record):
    # /tambah record ke list data (cek duplikat id dulu)
    id_terpakai = set()
    for r in data:
        id_terpakai.add(r["id"])

    if record["id"] in id_terpakai:
        return False

    # record masuk ke data
    data.append(record)
    return True

def _cari_index(data, id_panen):
    # /cari index suatu record di list data
    id_panen = id_panen.strip().upper()
    for i in range(len(data)):
        if data[i]["id"] == id_panen:
            return i
    return -1

def ubah_data(data, id_panen, perubahan):
    # /ubah value suatu key dalam record di list data
    i = _cari_index(data, id_panen)
    if i == -1:
        return False

    record = data[i]
    for kolom in KOLOM_BOLEH_UBAH:
        if kolom in perubahan:
            record[kolom] = perubahan[kolom]

    # hitung ulang berat/harga in case diubah
    record.update(hitung_bagi_hasil(record["berat"], record["harga_per_kg"]))
    return True

def hapus_data(data, id_panen):
    # /hapus suatu record di list data
    i = _cari_index(data, id_panen)
    if i == -1:
        return None
    return data.pop(i)

def _nilai_urut(record, kunci):
    # /read value suatu key dalam record, jadi str & lower
    nilai = record[kunci]

    # is nilai == str?
    if isinstance(nilai, str):
        return nilai.lower()
    return nilai

def _quick_sort(daftar, kunci):
    # /pengurutan quicksort dari hasil return _nilai_urut
    if len(daftar) <= 1:
        return daftar

    pivot = _nilai_urut(daftar[len(daftar) // 2], kunci)
    kiri = [r for r in daftar if _nilai_urut(r, kunci) < pivot]
    tengah = [r for r in daftar if _nilai_urut(r, kunci) == pivot]
    kanan = [r for r in daftar if _nilai_urut(r, kunci) > pivot]

    return _quick_sort(kiri, kunci) + tengah + _quick_sort(kanan, kunci)

def urutkan(data, kunci, menurun=False):
    # /return list data yang udah di sort
    if kunci not in KOLOM_URUT:
        raise ValueError("Kolom tidak dikenal: " + str(kunci))

    # list(data) dipake supaya 'data' asli gak berubah
    hasil = _quick_sort(list(data), kunci)
    # if descending
    if menurun:
        hasil = hasil[::-1]
    return hasil

def cari_id(data, id_panen):
    # /cari id panen dengan binary search
    id_panen = id_panen.strip().upper()
    terurut = _quick_sort(list(data), "id")

    # index
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
    # /cari nama dengan linear search
    kata = kata.strip().lower()
    hasil = []
    if kata == "":
        return hasil

    for record in data:
        if kata in record["nama"].lower():
            hasil.append(record)
    return hasil

def _tambah_rekap(rekap, nama, record):
    # /menambah total rekap berat & harga ke rekap (khusus per komoditas &/ petani)
    nama = nama.strip().title()
    if nama not in rekap:
        rekap[nama] = {"berat": 0.0, "nilai": 0}
    rekap[nama]["berat"] += record["berat"]
    rekap[nama]["nilai"] += record["total"]

def ringkasan(data):
    # /ringkasan semua data di tandur

    # inisialisasi data akumulasi
    hasil = {
        "jumlah_transaksi": len(data),
        "total_berat": 0.0,
        "total_nilai": 0,
        "total_petani": 0,
        "total_kas": 0,
        "per_komoditas": {}, # padi,jangung,dst
        "per_petani": {}, # orang a,b,c,dst
    }

    # penjumlahan setiap data
    for r in data:
        hasil["total_berat"] += r["berat"]
        hasil["total_nilai"] += r["total"]
        hasil["total_petani"] += r["bagian_petani"]
        hasil["total_kas"] += r["bagian_kas"]
        _tambah_rekap(hasil["per_komoditas"], r["komoditas"], r)
        _tambah_rekap(hasil["per_petani"], r["nama"], r)

    hasil["total_berat"] = round(hasil["total_berat"], 2) # 1.2345 ke 1.23

    # pembulatan untuk per komoditas &/ petani
    for rekap in (hasil["per_komoditas"], hasil["per_petani"]):
        for nama in rekap:
            rekap[nama]["berat"] = round(rekap[nama]["berat"], 2)

    return hasil