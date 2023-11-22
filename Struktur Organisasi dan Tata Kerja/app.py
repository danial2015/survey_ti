from flask import Flask, render_template, send_file
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SelectField, RadioField
import matplotlib.pyplot as plt
from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///survey.db'  # Database SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional, but recommended

db = SQLAlchemy(app)

# Model untuk menyimpan data survey
class SurveyResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    nim_nip = db.Column(db.String(20))
    status = db.Column(db.String(20))
    struktur_organisasi = db.Column(db.String(20))
    pengembangan_kompetensi = db.Column(db.String(20))
    layanan_akademik_non_akademik = db.Column(db.String(20))
    kesesuaian_regulasi = db.Column(db.String(20))

# Definisikan kelas formulir
class SurveyForm(FlaskForm):
    nama = StringField('Nama')
    nim_nip = StringField('NIM/NIP')
    status = SelectField('Status', choices=[('Tendik', 'Tendik'), ('Mahasiswa', 'Mahasiswa')])
    struktur_organisasi = RadioField('Struktur Organisasi dan Tatakerja PNL yang Jelas', choices=[('Tidak Memuaskan', 'Tidak Memuaskan'), ('Kurang Memuaskan', 'Kurang Memuaskan'), ('Cukup Memuaskan', 'Cukup Memuaskan'), ('Memuaskan', 'Memuaskan')])
    pengembangan_kompetensi = RadioField('Pengembangan Kompetensi, Tugas Pokok, dan Sarana Prasarana Pembelajaran', choices=[('Tidak Memuaskan', 'Tidak Memuaskan'), ('Kurang Memuaskan', 'Kurang Memuaskan'), ('Cukup Memuaskan', 'Cukup Memuaskan'), ('Memuaskan', 'Memuaskan')])
    layanan_akademik_non_akademik = RadioField('Layanan Akademik dan Non Akademik', choices=[('Tidak Memuaskan', 'Tidak Memuaskan'), ('Kurang Memuaskan', 'Kurang Memuaskan'), ('Cukup Memuaskan', 'Cukup Memuaskan'), ('Memuaskan', 'Memuaskan')])
    kesesuaian_regulasi = RadioField('Kesesuaian Regulasi dengan Implementasi di PNL', choices=[('Tidak Memuaskan', 'Tidak Memuaskan'), ('Kurang Memuaskan', 'Kurang Memuaskan'), ('Cukup Memuaskan', 'Cukup Memuaskan'), ('Memuaskan', 'Memuaskan')])

# Route untuk menampilkan formulir
@app.route('/', methods=['GET', 'POST'])
def index():
    form = SurveyForm()
    if form.validate_on_submit():
        # Simpan data survey ke dalam database
        response = SurveyResponse(
            nama=form.nama.data,
            nim_nip=form.nim_nip.data,
            status=form.status.data,
            struktur_organisasi=form.struktur_organisasi.data,
            pengembangan_kompetensi=form.pengembangan_kompetensi.data,
            layanan_akademik_non_akademik=form.layanan_akademik_non_akademik.data,
            kesesuaian_regulasi=form.kesesuaian_regulasi.data
        )
        db.session.add(response)
        db.session.commit()

        return "Terima kasih telah mengisi survey!"
    return render_template('survey.html', form=form)

# Route untuk menampilkan hasil tanggapan
@app.route('/hasil_tanggapan')
def hasil_tanggapan():
    # Ambil semua data survey dari database
    responses = SurveyResponse.query.all()
    return render_template('hasil_tanggapan.html', responses=responses)

# Route untuk membuat chart dan menyimpannya ke dalam file
@app.route('/chart', endpoint='create_chart')
def create_chart():
    # Ambil data untuk chart dari database
    questions = ['struktur_organisasi', 'pengembangan_kompetensi', 'layanan_akademik_non_akademik', 'kesesuaian_regulasi']
    choices = ['Tidak Memuaskan', 'Kurang Memuaskan', 'Cukup Memuaskan', 'Memuaskan']

    data = {
        question: [SurveyResponse.query.filter(getattr(SurveyResponse, question) == choice).count() for choice in choices]
        for question in questions
    }

    # Buat chart batang
    fig, axes = plt.subplots(nrows=len(questions), ncols=1, figsize=(8, 12))

    for i, (question, values) in enumerate(data.items()):
        ax = axes[i]
        width = 0.2
        x = range(len(choices))
        ax.bar(x, values, width, label=question)
        ax.set_title(f'Hasil Tanggapan: {question}')
        ax.set_xlabel('Tanggapan')
        ax.set_ylabel('Jumlah Tanggapan')
        ax.set_xticks([val + width / 2 for val in x])
        ax.set_xticklabels(choices)
        ax.legend()

    plt.tight_layout()

    # Simpan chart ke dalam BytesIO
    img_io = BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    plt.close()

    # Kirim file chart sebagai respons
    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='chart.png')

if __name__ == '__main__':
    # Buat tabel dalam database jika belum ada
    with app.app_context():
        db.create_all()
    app.run(debug=True)
