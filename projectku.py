# Import library Flask, Pandas, dan datetime
from flask import Flask, render_template, request
import pandas as pd
from datetime import datetime

# Inisialisasi aplikasi Flask
app = Flask(__name__)


# RUTE UTAMA: Kalkulasi Engagement Rate Manual

@app.route("/", methods=["GET", "POST"])
def index():
    er = None  # Variabel untuk menyimpan hasil Engagement Rate

    if request.method == "POST":
        try:
            # Ambil nilai dari form input (diambil dari index.html)
            likes = int(request.form["likes"])
            comments = int(request.form["comments"])
            shares = int(request.form["shares"])
            followers = int(request.form["followers"])

            # Validasi agar followers tidak nol (karena akan dibagi)
            if followers == 0:
                return "Jumlah followers tidak boleh 0!"

            # Hitung engagement rate menggunakan rumus
            er = ((likes + comments + shares) / followers) * 100
            er = round(er, 2)  # dibulatkan 2 angka di belakang koma

            # Siapkan data baru yang akan dimasukkan ke CSV
            data_baru = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "followers": followers,
                "engagement_rate": er
            }

            # Nama file CSV
            nama_file = "social_media_data.csv"

            try:
                # Jika file sudah ada, baca dan tambahkan baris baru
                df = pd.read_csv(nama_file)
                df = pd.concat([df, pd.DataFrame([data_baru])], ignore_index=True)
            except FileNotFoundError:
                # Kalau file belum ada, buat baru
                df = pd.DataFrame([data_baru])

            # Simpan hasil ke file CSV
            df.to_csv(nama_file, index=False)

        except ValueError:
            # Kalau input bukan angka, munculkan pesan error
            return "Input tidak valid! Masukkan angka yang benar."

    # Kirim hasil ER (jika ada) ke halaman index.html
    return render_template("index.html", er=er)



# RUTE TAMBAHAN: Baca dan Hitung CSV dari Folder

@app.route("/read-csv")
def baca_csv():
    table = None  # Variabel untuk menyimpan HTML tabel hasil hitungan

    try:
        # Membaca file CSV bernama 'social_media_data.csv' 
        df = pd.read_csv("social_media_data.csv")

        # Mengecek apakah kolom-kolom yang dibutuhkan tersedia
        expected_cols = {'likes', 'comments', 'shares', 'followers'}
        if expected_cols.issubset(df.columns):
            # Hitung engagement rate untuk setiap baris
            df["engagement_rate"] = ((df["likes"] + df["comments"] + df["shares"]) / df["followers"]) * 100
            df["engagement_rate"] = df["engagement_rate"].round(2)  # dibulatkan 2 angka di belakang koma

            # Konversi dataframe ke tabel HTML untuk ditampilkan di upload.html
            table = df.to_html(classes="table", index=False)
        else:
            # Kalau kolom tidak lengkap, tampilkan pesan error
            return "CSV tidak lengkap. Harus ada: likes, comments, shares, followers"

    except FileNotFoundError:
        # Kalau file CSV tidak ditemukan di folder
        return "File 'social_media_data.csv' tidak ditemukan!"

    except Exception as e:
        # Penanganan error umum lainnya
        return f"Terjadi error: {str(e)}"

    # Kirim tabel ke upload.html untuk ditampilkan
    return render_template("upload.html", table=table)


if __name__ == "__main__":
    app.run(debug=True)  # Aktifkan debug untuk memudahkan pengecekan error