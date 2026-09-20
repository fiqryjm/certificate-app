# Dokumen Spesifikasi Teknis & Desain Sistem

**Nama Proyek:** Aplikasi Manajemen dan Validasi Sertifikat Pelatihan (PT Fiqry Jaya Manunggal)
**Versi:** 1.1 (Pembaruan Logika QR & Sertifikat)

## 1. Pendahuluan

Aplikasi ini dirancang untuk mengotomatisasi pembuatan sertifikat pelatihan dan Surat Keputusan (SK) Direksi. Sistem ini menyediakan fitur validasi keaslian sertifikat melalui pemindaian QR Code tunggal per pelatihan, yang akan mengarahkan pengguna ke halaman verifikasi berbasis web berisi dokumen SK Direksi dan daftar peserta sah untuk pelatihan tersebut.

## 2. Kebutuhan Fungsional (Functional Requirements)

Sistem harus mampu melakukan hal-hal berikut:

1. **Manajemen Pelatihan:** Menambah, mengubah, dan menghapus data pelatihan (Judul, Tempat, Tanggal, Nama Instruktur, Nomor Sertifikat). **Satu Nomor Sertifikat berlaku untuk satu pelatihan/batch.**

2. **Manajemen SK Direksi:** Membuat nomor surat dan tanggal surat untuk setiap batch pelatihan.

3. **Manajemen Peserta:** Mengimpor atau memasukkan data peserta (Nama, Perusahaan) yang terikat pada satu pelatihan tertentu.

4. **Pembuatan QR Code:** Menghasilkan **satu QR Code unik per pelatihan**. QR Code ini merujuk pada 1 Surat Keputusan yang menaungi seluruh peserta pada batch tersebut.

5. **Pembuatan Dokumen (Generate PDF):**

   * Men-generate Sertifikat format PDF untuk seluruh peserta (mendukung Tanda Tangan Digital/Basah & lampiran Silabus).

   * Men-generate SK Direksi format PDF beserta Lampiran Daftar Peserta.

6. **Portal Validasi (Publik):** Halaman web publik yang menampilkan SK Direksi dan tabel daftar seluruh peserta sah saat QR Code di-scan.

## 3. Arsitektur Sistem

Aplikasi ini dibangun menggunakan arsitektur berbasis Web (Client-Server).

* **Frontend (Admin Panel):** Dashboard untuk admin mengelola data dan mengunduh PDF.

* **Frontend (Halaman Validasi):** Halaman web yang diakses publik via pemindaian QR Code pada sertifikat.

* **Backend:** Server yang memproses CRUD data, men-generate QR Code tunggal per pelatihan, dan merender PDF menggunakan *framework* Antigravity.

* **Database:** Penyimpanan relasional untuk menjaga integritas data pelatihan dan peserta.

## 4. Desain Struktur Database (ERD)

**Tabel `pelatihans`**
*(Nomor sertifikat dan QR Code sekarang diletakkan di tabel ini karena berlaku sama untuk 1 pelatihan)*

| Kolom | Tipe Data | Keterangan | 
 | ----- | ----- | ----- | 
| id | INT (PK) | ID Pelatihan | 
| judul | VARCHAR(255) | Contoh: "Training Basic Drilling & Well Completion" | 
| tempat | VARCHAR(255) | Contoh: "PHR - Rumbai Training Center" | 
| tgl_mulai | DATE | Tanggal mulai pelatihan | 
| tgl_selesai | DATE | Tanggal selesai pelatihan | 
| nama_instruktur | VARCHAR(255) | Contoh: "Ir. Arwansyah Johan" | 
| silabus_teks | TEXT | Teks atau daftar materi untuk halaman belakang |
| nomor_sertifikat | VARCHAR(100) | Contoh: "FJM/276-BD&WC/VII/2025" (Sama untuk semua) |
| qr_code_hash | VARCHAR(255) | String unik untuk URL validasi pelatihan | 

**Tabel `sk_direksi`**

| Kolom | Tipe Data | Keterangan | 
 | ----- | ----- | ----- | 
| id | INT (PK) | ID Surat Keputusan | 
| pelatihan_id | INT (FK) | Relasi ke tabel pelatihans | 
| nomor_surat | VARCHAR(100) | Nomor SK (Input manual/Otomatis) | 
| tanggal_surat | DATE | Tanggal SK dikeluarkan | 
| direktur | VARCHAR(255) | Default: "Ir. Dudus Ruhul Kudus" | 

**Tabel `peserta`**
*(Lebih ringkas karena tidak lagi menyimpan QR dan Nomor Sertifikat secara individual)*

| Kolom | Tipe Data | Keterangan | 
 | ----- | ----- | ----- | 
| id | INT (PK) | ID Peserta | 
| pelatihan_id | INT (FK) | Relasi ke batch pelatihan | 
| nama_peserta | VARCHAR(255) | Nama lengkap peserta | 
| perusahaan | VARCHAR(255) | Asal perusahaan peserta | 

## 5. Alur Kerja Sistem (System Workflow)

### 5.1. Alur Pembuatan Sertifikat & SK (Admin)

1. **Create Training & SK:** Admin memasukkan data Pelatihan (Judul, Tempat, Waktu, Instruktur, Nomor Sertifikat) dan data SK (No Surat, Tgl Surat).

2. **Generate QR Code:** Sistem secara otomatis membuat *satu QR Code* untuk pelatihan tersebut (URL: `https://domainanda.com/validasi/[qr_code_hash]`).

3. **Input Participants:** Admin memasukkan daftar peserta (bisa upload Excel/CSV).

4. **Download PDF:** Admin mengunduh file `.zip` berisi:
   * File PDF Sertifikat untuk *semua* peserta (menggunakan Nomor Sertifikat dan QR Code yang sama).
   * File PDF SK Direksi beserta lampiran daftar pesertanya.

### 5.2. Alur Validasi QR Code (Publik)

1. Seseorang memindai QR Code di sertifikat mana pun dari batch tersebut.

2. Browser terbuka dan mengarah ke URL unik pelatihan (cth: `domainanda.com/validasi/batch123xyz`).

3. Halaman web menampilkan:

   * Status: **"Sertifikat & SK Valid"**

   * Dokumen Digital Surat Keterangan / SK Direksi yang memuat detail pelatihan.

   * Tabel Lampiran Daftar Peserta (menampilkan seluruh nama peserta yang sah untuk membuktikan bahwa nama di sertifikat fisik ada di dalam daftar resmi).

## 6. Rekomendasi Teknologi (Tech Stack)

Sesuai dengan permintaan, pengembangan akan menggunakan **Antigravity** dengan ekosistem Python:

* **Backend:** Python (menggunakan *environment* atau *framework* yang terintegrasi dengan Antigravity/Web framework Python seperti FastAPI, Flask, atau Django jika Antigravity merujuk pada standar Python *web development*).
* **Database:** SQLite (untuk skala ringan) atau PostgreSQL.
* **PDF Generator:** `ReportLab` atau `WeasyPrint` (sangat direkomendasikan di Python untuk men-generate PDF berbasis HTML/CSS).
* **QR Code Generator:** `qrcode` library di Python (`pip install qrcode[pil]`) untuk men-generate gambar QR Code yang disisipkan ke dalam PDF.