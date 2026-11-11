# Dokumen Spesifikasi Teknis & Desain Sistem

**Nama Proyek:** Aplikasi Manajemen dan Validasi Sertifikat Pelatihan (PT Fiqry Jaya Manunggal)  
**Versi:** 1.3 (Pembaruan Modul Sertifikat Trainer/Co-Trainer/Asisten, PDF Blanko, & Auto-Migration VPS)

## 1. Pendahuluan

Aplikasi ini dirancang untuk mengotomatisasi pembuatan sertifikat pelatihan, sertifikat pengajar (Trainer, Co-Trainer, Asisten Trainer), dan Surat Keputusan (SK) Direksi. Sistem ini menyediakan fitur validasi keaslian sertifikat melalui pemindaian QR Code tunggal per pelatihan, yang akan mengarahkan pengguna ke halaman verifikasi berbasis web berisi dokumen SK Direksi, daftar peserta sah, serta tim pengajar sah.

## 2. Kebutuhan Fungsional (Functional Requirements)

Sistem mampu melakukan hal-hal berikut:

1. **Manajemen Pelatihan:** Menambah, mengubah, dan menghapus data pelatihan (Judul, Tempat, Tanggal, Nama Instruktur, Nama Co-Trainer, Nama Asisten Trainer, Nomor Sertifikat). **Satu Nomor Sertifikat berlaku untuk satu pelatihan/batch.**

2. **Manajemen SK Direksi:** Membuat nomor surat dan tanggal surat untuk setiap batch pelatihan.

3. **Manajemen Peserta:** Mengimpor atau memasukkan data peserta (Nama, Perusahaan, Keterangan) yang terikat pada satu pelatihan tertentu.

4. **Manajemen Pengajar (Trainer / Co-Trainer / Asisten):**
   * Input cepat langsung melalui formulir pelatihan (Instruktur Utama, Co-Trainer, Asisten Trainer).
   * Menu terdedikasi **Kelola Trainer** untuk menambah pengajar tambahan dan memilih peran (*Trainer*, *Co-Trainer*, atau *Asisten Trainer*).

5. **Pembuatan QR Code:** Menghasilkan **satu QR Code unik per pelatihan**. QR Code ini merujuk pada Surat Keputusan dan halaman verifikasi publik yang menaungi seluruh peserta dan pengajar batch tersebut.

6. **Pembuatan Dokumen (Generate PDF):**
   * **PDF Sertifikat Peserta:** Sertifikat kelulusan dengan desain template resmi dan lampiran silabus hierarki.
   * **PDF Blanko:** Sertifikat khusus tanpa gambar latar template dan garis bawah untuk langsung dicetak di atas kertas blanko sertifikat fisik.
   * **PDF Trainer:** Sertifikat Penghargaan khusus pengajar menggunakan template `sertifikat_trainer.jpg` dengan penataan teks yang presisi dan posisi QR code di samping tanda tangan Direktur.
   * **PDF SK Direksi:** Dokumen SK Direksi beserta lampiran daftar peserta sah.

7. **Portal Validasi (Publik):** Halaman web publik yang menampilkan SK Direksi, tabel daftar seluruh peserta sah, serta tabel daftar tim pengajar sah saat QR Code di-scan.

## 3. Arsitektur Sistem

Aplikasi ini dibangun menggunakan arsitektur berbasis Web (Client-Server):

* **Frontend (Admin Panel):** Dashboard berbasis HTML5, CSS kustom responsif, dan Jinja2 template.
* **Frontend (Halaman Validasi):** Halaman web publik yang diakses via pemindaian QR Code pada sertifikat.
* **Backend:** Flask (Python) dengan SQLAlchemy ORM dan ReportLab engine.
* **Database:** SQLite (dengan auto-migration skema otomatis pada startup).
* **Production Web Server (VPS):** Gunicorn WSGI Server + Nginx Reverse Proxy + Systemd Service daemon.

## 4. Desain Struktur Database (ERD)

**Tabel `pelatihans`**  
*(Menyimpan data pelatihan, instruktur, co-trainer, asisten, nomor sertifikat, dan QR Code)*

| Kolom | Tipe Data | Keterangan |
| ----- | ----- | ----- |
| id | INT (PK) | ID Pelatihan |
| judul_pelatihan | VARCHAR(255) | Contoh: "Training Basic Drilling & Well Completion" |
| tempat | VARCHAR(255) | Contoh: "PHR - Rumbai Training Center" |
| tanggal_mulai | DATE | Tanggal mulai pelatihan |
| tanggal_selesai | DATE | Tanggal selesai pelatihan |
| nama_instruktur | VARCHAR(255) | Nama instruktur/trainer utama |
| nama_co_trainer | VARCHAR(255) | Nama co-trainer (opsional) |
| nama_asisten_trainer | VARCHAR(255) | Nama asisten trainer (opsional) |
| silabus | TEXT | Teks silabus dengan dukungan format bullet & numbering hierarki |
| no_sertifikat | VARCHAR(100) | Contoh: "FJM/276-BD&WC/VII/2025" |
| no_sk | VARCHAR(100) | Nomor SK Direksi |
| tanggal_sk | DATE | Tanggal penetapan SK |
| qr_code_hash | VARCHAR(255) | String unik (UUID) untuk URL validasi |
| qr_code_path | VARCHAR(255) | Path file gambar QR code |

**Tabel `trainers`**  
*(Menyimpan data pengajar tambahan atau pengajar perorangan)*

| Kolom | Tipe Data | Keterangan |
| ----- | ----- | ----- |
| id | INT (PK) | ID Pengajar |
| pelatihan_id | INT (FK) | Relasi ke tabel `pelatihans.id` |
| nama | VARCHAR(255) | Nama lengkap dan gelar pengajar |
| peran | VARCHAR(50) | Pilihan peran: "Trainer", "Co-Trainer", "Asisten Trainer" |

**Tabel `peserta`**  
*(Menyimpan data peserta per pelatihan)*

| Kolom | Tipe Data | Keterangan |
| ----- | ----- | ----- |
| id | INT (PK) | ID Peserta |
| pelatihan_id | INT (FK) | Relasi ke batch pelatihan |
| nama_peserta | VARCHAR(255) | Nama lengkap peserta |
| perusahaan | VARCHAR(255) | Asal perusahaan peserta |
| keterangan | VARCHAR(255) | Catatan opsional |

## 5. Alur Kerja Sistem (System Workflow)

### 5.1. Alur Pembuatan Sertifikat & SK (Admin)

1. **Input Pelatihan & SK:** Admin memasukkan data Pelatihan (Judul, Tempat, Waktu, Instruktur, Co-Trainer, Asisten, Nomor Sertifikat, Nomor SK).
2. **Generate QR Code:** Sistem secara otomatis membuat *satu QR Code* unik untuk pelatihan tersebut (URL: `/validasi/[qr_code_hash]`).
3. **Input Peserta:** Admin memasukkan daftar peserta di menu *Kelola Peserta*.
4. **Input Pengajar Tambahan:** (Opsional) Admin dapat mengelola pengajar tambahan melalui menu *Kelola Trainer*.
5. **Download / Cetak Dokumen:**
   * **PDF Peserta:** Sertifikat lengkap peserta (dengan silabus halaman belakang).
   * **PDF Blanko:** Cetakan teks sertifikat yang diposisikan presisi untuk kertas fisik.
   * **PDF Trainer:** Sertifikat penghargaan pengajar yang otomatis mencakup Instruktur Utama (*Sebagai Trainer*), Co-Trainer (*Sebagai Co-Trainer*), Asisten (*Sebagai Asisten Trainer*), dan pengajar tambahan lainnya.
   * **PDF SK:** Dokumen SK Direksi beserta lampiran peserta.

### 5.2. Alur Validasi QR Code (Publik)

1. Pengguna memindai QR Code di sertifikat peserta atau sertifikat pengajar.
2. Browser mengarah ke halaman verifikasi resmi PT Fiqry Jaya Manunggal.
3. Halaman web menampilkan:
   * Status keabsahan sertifikat & SK.
   * Informasi detail pelatihan (Judul, Tanggal, Tempat, No. Sertifikat).
   * Pernyataan Surat Keputusan Direksi.
   * Tabel daftar peserta sah.
   * Tabel daftar tim pengajar sah.

## 6. Rekomendasi Teknologi (Tech Stack)

* **Backend Framework:** Python 3.10+, Flask 3.0, Flask-SQLAlchemy.
* **Database:** SQLite dengan auto-migration script.
* **PDF Generator Engine:** `ReportLab` dengan canvas presisi tinggi dan auto font fallback (`Garamond` / `Times-Roman`).
* **Image Processing:** `Pillow` (PIL) & `qrcode[pil]`.
* **Production Deployment:** Gunicorn WSGI, Nginx Web Server, Systemd service daemon.

## 7. Catatan Riwayat Pengembangan & Progres (Changelog)

### Versi 1.3 (Pembaruan Terkini)
* **Modul Sertifikat Trainer / Co-Trainer / Asisten Trainer:**
  - Penambahan generator PDF [`generate_sertifikat_trainer_pdf`](file:///c:/Aplikasi/certificat-app/pdf_generator.py#L415) berbasis template penghargaan `sertifikat_trainer.jpg`.
  - Penyesuaian tata letak proporsional dan elegan: jarak nama pengajar di bawah tulisan *"Diberikan Kepada :"*, format teks *"Sebagai [Peran]"* dengan font italic, judul pelatihan, tempat, tanggal simetris di atas tanda tangan direktur, dan posisi QR code di kiri bawah.
  - Penambahan kolom `nama_co_trainer` dan `nama_asisten_trainer` pada tabel `pelatihans` dan formulir Tambah/Edit Pelatihan.
  - Pembuatan tabel database baru `trainers` serta antarmuka web [trainer.html](file:///c:/Aplikasi/certificat-app/templates/trainer.html) & [edit_trainer.html](file:///c:/Aplikasi/certificat-app/templates/edit_trainer.html).
  - Tampilan portal verifikasi publik ([validasi.html](file:///c:/Aplikasi/certificat-app/templates/validasi.html)) kini menyertakan tabel resmi Tim Pengajar Sah.
* **Pengembalian & Pemantapan Fitur PDF Blanko:**
  - Tombol `PDF Blanko` di tabel pelatihan utama dan `Cetak Blanko` di tabel peserta tetap tersedia penuh dengan offset presisi milimeter untuk kertas sertifikat fisik.
* **Auto-Migration Database SQLite:**
  - Penambahan mekanisme auto-alter skema otomatis pada startup aplikasi, memudahkan proses deployment/update di VPS tanpa perlu eksekusi SQL manual.

### Versi 1.2
* **Fitur Cetak Blanko:** Mode rendering teks tanpa background template dan garis datar untuk kebutuhan cetak ke kertas blangko bersertifikat.
* **Manajemen Penghapusan Data:** Penambahan tombol dan aksi hapus pelatihan (beserta seluruh peserta & QR-nya) dan hapus peserta satuan.

### Versi 1.1
* **Pembaruan Format Silabus Hierarki:** Dukungan perenderan otomatis untuk penomoran utama (`1.`, `2.`) dan sub-materi ber-bullet/huruf (`a.`, `b.`, `-`) dengan indentasi rapi pada halaman belakang sertifikat peserta.
* **Logika QR Code Tunggal:** Standardisasi QR Code berbasis batch pelatihan yang mengarah ke SK Direksi dan daftar peserta sah.

### Versi 1.0
* Inisialisasi sistem aplikasi sertifikat dan SK Direksi berbasis web Flask.
* CRUD Pelatihan dan Peserta.
* Integrasi awal ReportLab untuk pembuatan sertifikat dan SK digital bertanda tangan.
