from flask import Flask, render_template, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, RadioField
import matplotlib.pyplot as plt
from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///survey.db'  # Database SQLite

db = SQLAlchemy(app)

# Model untuk menyimpan data survey
class SurveyResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    nim_nip = db.Column(db.String(20))
    status = db.Column(db.String(20))
    layanan_admin_akademik = db.Column(db.String(20))  # New field for Layanan Administrasi Akademik
    layanan_admin_kemahasiswaan = db.Column(db.String(20))  # New field for Layanan Administrasi Kemahasiswaan
    layanan_klinik = db.Column(db.String(20))  # New field for Layanan Klinik Kampus PNL

# Definisikan kelas formulir
class SurveyForm(FlaskForm):
    nama = StringField('Nama')
    nim_nip = StringField('NIM/NIP')
    status = SelectField('Status', choices=[('Tendik', 'Tendik'), ('Mahasiswa', 'Mahasiswa')])
    layanan_admin_akademik = RadioField('Layanan Administrasi Akademik', choices=[('Kurang Baik', 'Kurang Baik'), ('Cukup Baik', 'Cukup Baik'), ('Baik', 'Baik'), ('Sangat Baik', 'Sangat Baik')])
    layanan_admin_kemahasiswaan = RadioField('Layanan Administrasi Kemahasiswaan', choices=[('Kurang Baik', 'Kurang Baik'), ('Cukup Baik', 'Cukup Baik'), ('Baik', 'Baik'), ('Sangat Baik', 'Sangat Baik')])
    layanan_klinik = RadioField('Layanan Klinik Kampus PNL', choices=[('Kurang Baik', 'Kurang Baik'), ('Cukup Baik', 'Cukup Baik'), ('Baik', 'Baik'), ('Sangat Baik', 'Sangat Baik')])

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
            layanan_admin_akademik=form.layanan_admin_akademik.data,
            layanan_admin_kemahasiswaan=form.layanan_admin_kemahasiswaan.data,
            layanan_klinik=form.layanan_klinik.data
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
    questions = ['layanan_admin_akademik', 'layanan_admin_kemahasiswaan', 'layanan_klinik']
    choices = ['Kurang Baik', 'Cukup Baik', 'Baik', 'Sangat Baik']

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

    # Kirim file chart
    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='vmts_survey.png')

if __name__ == '__main__':
    # Buat tabel dalam database jika belum ada
    with app.app_context():
        db.create_all()
    app.run(debug=True)