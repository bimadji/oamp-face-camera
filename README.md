## Instalasi Program

### 1. Persiapan Environment

Buat dan aktifkan virtual environment (opsional tapi direkomendasikan):

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Unix/Linux/MacOS
python -m venv venv
source venv/bin/activate
```

### 2. Instal Dependensi

```bash
pip install -r requirements.txt
```

### 3. Konfigurasi

1. Salin file `.env.example` ke `.env`:
   ```bash
   copy .env.example .env
   ```
2. Edit file `.env` dan sesuaikan dengan konfigurasi database Anda.

### 4. Unduh File Berukuran Besar (Opsional)

Jika menggunakan Git LFS untuk file-file berukuran besar, jalankan perintah berikut:

```bash
git lfs install
git lfs pull
```

### 5. Setup Library Intel MKL (Windows)

Untuk pengguna Windows dengan processor Intel:
1. Salin file `DLL/svml_dispmd.dll` ke folder `C:\Windows\System32\`

## Menjalankan Aplikasi

```bash
python main.py
```
