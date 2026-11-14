# Memelihara README profil

Kartu dirender dengan Python 3.9 atau lebih baru, menggunakan pustaka standar. README menampilkan SVG sebagai gambar. Animasi hanya aktif bila pengaturan sistem mengizinkan gerakan.

```sh
python3 scripts/fetch_contributions.py rkthooriq
python3 scripts/render_readme_cards.py
STATIC=1 python3 scripts/render_readme_cards.py --output /tmp/rkthooriq-static-cards
```

Perintah render biasa bisa dijalankan tanpa jaringan dengan snapshot yang sudah tersimpan. Mode statis menghapus CSS animasi dan menampilkan posisi akhir semua elemen.

Potret kartu pembuka berasal dari [avatar publik GitHub @rkthooriq](https://github.com/rkthooriq). Garis potret disimpan di `assets/portrait-rows.txt` dan disematkan langsung ke SVG saat render.

## Data dan jadwal

Snapshot mencakup 365 hari UTC yang sudah selesai. Hari tanpa kontribusi hanya dicatat sebagai nol bila kalender GitHub memang menyatakan demikian. Hitungan mengikuti kalender yang tersedia untuk pengunjung tanpa login, termasuk hitungan privat anonim bila pemilik profil sudah menampilkannya di GitHub. Bulan pertama dan terakhir pada grafik dapat berupa bulan parsial. Hari tersibuk dan bulan tersibuk memakai tanggal paling awal bila nilainya seri. Rentetan dihitung dalam jendela 365 hari yang sama.

Pengambilan data menggunakan HTML kalender publik GitHub. Bila struktur HTML berubah atau tanggal yang diminta tidak lengkap, pengambilan berhenti dan workflow mempertahankan snapshot yang terakhir berhasil.

Workflow berjalan di branch default setiap hari sekitar pukul 07.23 WIB dan bisa dijalankan manual dari tab **Actions**. Token bawaan Actions hanya dipakai untuk menyimpan perubahan ke repo profil. Pengaturan repo dan aturan branch harus mengizinkan penulisan oleh workflow.

## Repo publik terbaru dan Tech stack

Workflow memilih satu repo publik milik akun berdasarkan waktu push terakhir. Repo profil, fork, dan repo arsip dilewati. Kartu memakai nama serta deskripsi publik. Tech stack menampilkan hingga lima bahasa teratas berdasarkan jumlah byte menurut GitHub. Jika GitHub belum mendeteksi bahasa, README menampilkan keterangan itu. Framework, library, dan alat build tidak diperkirakan dari nama bahasa.

Bagian di antara penanda `featured-repo` diperbarui otomatis, sementara isi di luar penanda dikelola manual. Jalankan **Refresh profile contributions** dari tab **Actions** untuk mengecek repo terbaru tanpa menunggu jadwal harian. Untuk memperbarui bagian ini secara lokal, jalankan `python3 -B scripts/refresh_featured_repo.py`.

## Menerapkan ke repo profil

Jika repo sudah memiliki README, salin README lama sebagai cadangan dan simpan versi itu di Git sebelum menggantinya. Cek juga apakah repo sudah punya workflow yang memperbarui README atau grafik agar jadwalnya bisa disatukan.

## GitHub Stats dan Most Used Languages

Kedua kartu diperbarui oleh workflow yang sama. Stats memakai snapshot 365 hari untuk kontribusi dan hari aktif, serta daftar repo proyek publik untuk jumlah repo dan bintang. Most Used Languages menjumlahkan byte kode per bahasa di repo proyek publik. Cakupannya mengikuti filter kartu proyek, yang melewati repo profil, fork, dan arsip. Tech stack tetap mengikuti repo publik terbaru.
