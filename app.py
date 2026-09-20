import os
import uuid
import qrcode
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file, abort
from models import db, Pelatihan, Peserta
from pdf_generator import generate_sertifikat_pdf, generate_sk_direksi_pdf

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cert.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Ensure folders exist
os.makedirs('static/qr_codes', exist_ok=True)
os.makedirs('static/templates', exist_ok=True)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    pelatihans = Pelatihan.query.order_by(Pelatihan.tanggal_mulai.desc()).all()
    return render_template('index.html', pelatihans=pelatihans)

@app.route('/pelatihan/tambah', methods=['GET', 'POST'])
def tambah_pelatihan():
    if request.method == 'POST':
        judul = request.form.get('judul_pelatihan')
        tempat = request.form.get('tempat')
        tanggal_mulai = datetime.strptime(request.form.get('tanggal_mulai'), '%Y-%m-%d').date()
        tanggal_selesai = datetime.strptime(request.form.get('tanggal_selesai'), '%Y-%m-%d').date()
        nama_instruktur = request.form.get('nama_instruktur')
        no_sertifikat = request.form.get('no_sertifikat')
        no_sk = request.form.get('no_sk')
        tanggal_sk = datetime.strptime(request.form.get('tanggal_sk'), '%Y-%m-%d').date()
        silabus = request.form.get('silabus')
        
        # Generate hash for verification
        qr_hash = str(uuid.uuid4().hex)
        
        # Generate QR Code image
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        verification_url = url_for('validasi_sertifikat', qr_code_hash=qr_hash, _external=True)
        qr.add_data(verification_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        qr_filename = f"qr_{qr_hash}.png"
        qr_filepath = os.path.join('static', 'qr_codes', qr_filename)
        img.save(qr_filepath)
        
        pelatihan = Pelatihan(
            judul_pelatihan=judul,
            tempat=tempat,
            tanggal_mulai=tanggal_mulai,
            tanggal_selesai=tanggal_selesai,
            nama_instruktur=nama_instruktur,
            no_sertifikat=no_sertifikat,
            no_sk=no_sk,
            tanggal_sk=tanggal_sk,
            silabus=silabus,
            qr_code_hash=qr_hash,
            qr_code_path=qr_filepath
        )
        db.session.add(pelatihan)
        db.session.commit()
        return redirect(url_for('index'))
        
    return render_template('form_pelatihan.html')

@app.route('/pelatihan/<int:pelatihan_id>/edit', methods=['GET', 'POST'])
def edit_pelatihan(pelatihan_id):
    pelatihan = Pelatihan.query.get_or_404(pelatihan_id)
    if request.method == 'POST':
        pelatihan.judul_pelatihan = request.form.get('judul_pelatihan')
        pelatihan.tempat = request.form.get('tempat')
        pelatihan.tanggal_mulai = datetime.strptime(request.form.get('tanggal_mulai'), '%Y-%m-%d').date()
        pelatihan.tanggal_selesai = datetime.strptime(request.form.get('tanggal_selesai'), '%Y-%m-%d').date()
        pelatihan.nama_instruktur = request.form.get('nama_instruktur')
        pelatihan.no_sertifikat = request.form.get('no_sertifikat')
        pelatihan.no_sk = request.form.get('no_sk')
        pelatihan.tanggal_sk = datetime.strptime(request.form.get('tanggal_sk'), '%Y-%m-%d').date()
        pelatihan.silabus = request.form.get('silabus')
        
        db.session.commit()
        return redirect(url_for('index'))
        
    return render_template('form_pelatihan.html', pelatihan=pelatihan)

@app.route('/pelatihan/<int:pelatihan_id>/peserta', methods=['GET', 'POST'])
def peserta(pelatihan_id):
    pelatihan = Pelatihan.query.get_or_404(pelatihan_id)
    if request.method == 'POST':
        nama = request.form.get('nama_peserta')
        perusahaan = request.form.get('perusahaan')
        keterangan = request.form.get('keterangan')
        
        peserta = Peserta(pelatihan_id=pelatihan.id, nama_peserta=nama, perusahaan=perusahaan, keterangan=keterangan)
        db.session.add(peserta)
        db.session.commit()
        return redirect(url_for('peserta', pelatihan_id=pelatihan.id))
        
    peserta_list = Peserta.query.filter_by(pelatihan_id=pelatihan.id).all()
    return render_template('peserta.html', pelatihan=pelatihan, peserta_list=peserta_list)

@app.route('/peserta/<int:peserta_id>/edit', methods=['GET', 'POST'])
def edit_peserta(peserta_id):
    peserta = Peserta.query.get_or_404(peserta_id)
    if request.method == 'POST':
        peserta.nama_peserta = request.form.get('nama_peserta')
        peserta.perusahaan = request.form.get('perusahaan')
        peserta.keterangan = request.form.get('keterangan')
        
        db.session.commit()
        return redirect(url_for('peserta', pelatihan_id=peserta.pelatihan_id))
        
    return render_template('edit_peserta.html', peserta=peserta)

@app.route('/pelatihan/<int:pelatihan_id>/cetak_sertifikat')
def cetak_sertifikat(pelatihan_id):
    pelatihan = Pelatihan.query.get_or_404(pelatihan_id)
    # Check if a template file exists
    template_path = 'static/templates/sertifikat_template.jpg'
    if not os.path.exists(template_path):
        template_path = None # Will draw without background template if not found
    
    pdf_buffer = generate_sertifikat_pdf(pelatihan, template_path)
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"Sertifikat_{pelatihan.judul_pelatihan.replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )

@app.route('/peserta/<int:peserta_id>/cetak_sertifikat')
def cetak_sertifikat_peserta(peserta_id):
    peserta = Peserta.query.get_or_404(peserta_id)
    pelatihan = Pelatihan.query.get(peserta.pelatihan_id)
    template_path = 'static/templates/sertifikat_template.jpg'
    if not os.path.exists(template_path):
        template_path = None
    
    pdf_buffer = generate_sertifikat_pdf(pelatihan, template_path, peserta_id=peserta.id)
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"Sertifikat_{peserta.nama_peserta.replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )

@app.route('/pelatihan/<int:pelatihan_id>/cetak_sk')
def cetak_sk(pelatihan_id):
    pelatihan = Pelatihan.query.get_or_404(pelatihan_id)
    template_path = 'static/templates/kop-surat-fjm.jpg'
    if not os.path.exists(template_path):
        template_path = None
        
    pdf_buffer = generate_sk_direksi_pdf(pelatihan, template_path)
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"SK_{pelatihan.judul_pelatihan.replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )

@app.route('/validasi/<qr_code_hash>')
def validasi_sertifikat(qr_code_hash):
    pelatihan = Pelatihan.query.filter_by(qr_code_hash=qr_code_hash).first()
    if not pelatihan:
        abort(404, description="Sertifikat tidak ditemukan atau tidak valid.")
    return render_template('validasi.html', pelatihan=pelatihan)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
