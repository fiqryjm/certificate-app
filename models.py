from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Pelatihan(db.Model):
    __tablename__ = 'pelatihans'
    
    id = db.Column(db.Integer, primary_key=True)
    judul_pelatihan = db.Column(db.String(255), nullable=False)
    tempat = db.Column(db.String(255), nullable=False)
    tanggal_mulai = db.Column(db.Date, nullable=False)
    tanggal_selesai = db.Column(db.Date, nullable=False)
    nama_instruktur = db.Column(db.String(255), nullable=False)
    no_sertifikat = db.Column(db.String(100), nullable=False)
    no_sk = db.Column(db.String(100), nullable=False)
    tanggal_sk = db.Column(db.Date, nullable=False)
    silabus = db.Column(db.Text, nullable=True)
    qr_code_hash = db.Column(db.String(255), unique=True, nullable=False)
    qr_code_path = db.Column(db.String(255), nullable=True)
    
    # Relationship to Peserta
    peserta = db.relationship('Peserta', backref='pelatihan', lazy=True, cascade="all, delete-orphan")

class Peserta(db.Model):
    __tablename__ = 'peserta'
    
    id = db.Column(db.Integer, primary_key=True)
    pelatihan_id = db.Column(db.Integer, db.ForeignKey('pelatihans.id'), nullable=False)
    nama_peserta = db.Column(db.String(255), nullable=False)
    perusahaan = db.Column(db.String(255), nullable=True)
    keterangan = db.Column(db.String(255), nullable=True)
