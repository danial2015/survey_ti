from flask import Flask, render_template, send_file
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
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
    bidang_kerjasama = db.Column(db.String(20))
    respon_kerjasama = db.Column(db.String(20))
    proses_pembuatan = db.Column(db.String(20))
    pendampingan_pnl = db.Column(db.String(20))
    kesesuaian_harapan = db.Column(db.String(20))
    manfaat_kerjasama = db.Column(db.String(20))
    implementasi_kerjasama = db.Column(db.String(20))
    pelaporan_kegiatan = db.Column(db.String(20))

# Definisikan kelas formulir
class SurveyForm(FlaskForm):
    nama = StringField('Nama')
    nim_nip = StringField('NIM/NIP')
    status = SelectField('Status', choices=[('Tendik', 'Tendik'), ('Mahasiswa', 'Mahasiswa')])
    bidang_kerjasama = RadioField('Dalam bidang apa mitra terlibat kerjasama dengan Politeknik Negeri Lhokseumawe', choices=[('Tidak Baik', 'Tidak Baik'), ('Cukup Baik', 'Cukup Baik'), ('Baik', 'Baik'), ('Sangat Baik', 'Sangat Baik')])
    respon_kerjasama = RadioField('Respon bidang kerjasama PNL terkait kebutuhan Mitra dengan tepat dan professional', choices=[('Tidak Baik', 'Tidak Baik'), ('Cukup Baik', 'Cukup Baik'), ('Baik', 'Baik'), ('Sangat Baik', 'Sangat Baik')])
    proses_pembuatan = RadioField('Apakah proses pembuatan MoU dan Perjanjian Kerja Sama (PKS) terlaksana sesuai harapan', choices=[('Tidak Baik', 'Tidak Baik'), ('Cukup Baik', 'Cukup Baik'), ('Baik', 'Baik'), ('Sangat Baik', 'Sangat Baik')])
    pendampingan_pnl = RadioField('PNL memberikan pendampingan terhadap kebutuhan kerja sama sesuai harapan mitra', choices=[('Tidak Baik', 'Tidak Baik'), ('Cukup Baik', 'Cukup Baik'), ('Baik', 'Baik'), ('Sangat Baik', 'Sangat Baik')])
    kesesuaian_harapan = RadioField('Apakah kerja sama yang terjalin berjalan sesuai dengan harapan mitra', choices=[('Tidak Baik', 'Tidak Baik'), ('Cukup Baik', 'Cukup Baik'), ('Baik', 'Baik'), ('Sangat Baik', 'Sangat Baik')])
    manfaat_kerjasama = RadioField('Apakah mitra mendapatkan hal yang berguna dari kerjasama', choices=[('Tidak Baik', 'Tidak Baik'), ('Cukup Baik', 'Cukup Baik'), ('Baik', 'Baik'), ('Sangat Baik', 'Sangat Baik')])
    implementasi_kerjasama = RadioField('Apakah kerjasama mitra dengan PNL telah diimplementasikan sesuai dengan yang telah disepakati bersama', choices=[('Tidak Baik', 'Tidak Baik'), ('Cukup Baik', 'Cukup Baik'), ('Baik', 'Baik'), ('Sangat Baik', 'Sangat Baik')])
    pelaporan_kegiatan = RadioField('Pelaporan akhir dari hasil kegiatan kerjasama dikomunikasikan dengan baik kepada mitra', choices=[('Tidak Baik', 'Tidak Baik'), ('Cukup Baik', 'Cukup Baik'), ('Baik', 'Baik'), ('Sangat Baik', 'Sangat Baik')])

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
            bidang_kerjasama=form.bidang_kerjasama.data,
            respon_kerjasama=form.respon_kerjasama.data,
            proses_pembuatan=form.proses_pembuatan.data,
            pendampingan_pnl=form.pendampingan_pnl.data,
            kesesuaian_harapan=form.kesesuaian_harapan.data,
            manfaat_kerjasama=form.manfaat_kerjasama.data,
            implementasi_kerjasama=form.implementasi_kerjasama.data,
            pelaporan_kegiatan=form.pelaporan_kegiatan.data
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
    questions = ['bidang_kerjasama', 'respon_kerjasama', 'proses_pembuatan', 'pendampingan_pnl', 'kesesuaian_harapan', 'manfaat_kerjasama', 'implementasi_kerjasama', 'pelaporan_kegiatan']
    choices = ['Tidak Baik', 'Cukup Baik', 'Baik', 'Sangat Baik']

    data = {
        question: [SurveyResponse.query.filter(getattr(SurveyResponse, question) == choice).count() for choice in choices]
        for question in questions
    }
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
    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='vmts_survey.png')

if __name__ == '__main__':
    # Buat tabel dalam database jika belum ada
    with app.app_context():
        db.create_all()
    app.run(debug=True)
