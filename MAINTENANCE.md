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

## Kartu repo unggulan otomatis

Di repo profil, buka **Settings → Secrets and variables → Actions → Variables → New repository variable**. Buat variabel `FEATURED_REPOSITORY` dengan nilai nama repo milik akun yang sama, tanpa awalan username. Gunakan variabel repo agar nama pilihan tidak perlu ditulis di README atau workflow sebelum repo itu publik.

Workflow mengecek GitHub tanpa autentikasi. Saat repo bisa dibaca publik, workflow membuat kartu dari nama dan deskripsi publiknya. Jika GitHub mengembalikan 404, workflow mengosongkan bagian di antara penanda `featured-repo` dan menghapus kartu otomatis. Bagian lain dari README tetap dikelola manual. Jalankan **Refresh profile contributions** dari tab **Actions** untuk mengecek tanpa menunggu jadwal berikutnya.

## Menerapkan ke repo profil

Jika repo sudah memiliki README, salin README lama sebagai cadangan dan simpan versi itu di Git sebelum menggantinya. Cek juga apakah repo sudah punya workflow yang memperbarui README atau grafik agar jadwalnya bisa disatukan.
