import os
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

def generate_sertifikat_pdf(pelatihan, template_path=None, peserta_id=None):
    """
    Generate PDF Sertifikat for all participants or a specific one, with syllabus page.
    """
    buffer = BytesIO()
    # Certificate is usually landscape
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    if peserta_id:
        peserta_list = [p for p in pelatihan.peserta if p.id == peserta_id]
    else:
        peserta_list = pelatihan.peserta
        
    if not peserta_list:
        c.setFont("Helvetica", 16)
        c.drawString(100, height / 2.0, "Belum ada peserta untuk dicetak.")
        c.showPage()
        
    for peserta in peserta_list:
        # 1. Draw Template (if provided)
        if template_path and os.path.exists(template_path):
            try:
                # Fill the page with the template
                c.drawImage(template_path, 0, 0, width=width, height=height)
            except Exception as e:
                print(f"Error loading template: {e}")
        
        # 2. Draw Text (Adjust coordinates based on actual template)
        # Center the name
        name_font, name_size = "Helvetica-Bold", 28
        c.setFont(name_font, name_size)
        name_y = height / 2.0 + 80
        c.drawCentredString(width / 2.0, name_y, peserta.nama_peserta)
        
        # Draw underline for name
        name_width = c.stringWidth(peserta.nama_peserta, name_font, name_size)
        c.line(width / 2.0 - name_width / 2.0, name_y - 4, width / 2.0 + name_width / 2.0, name_y - 4)
        
        # Date Logic
        d_mulai = pelatihan.tanggal_mulai
        d_selesai = pelatihan.tanggal_selesai
        months_id = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        m_mulai = months_id[d_mulai.month]
        m_selesai = months_id[d_selesai.month]
        
        if d_mulai.year == d_selesai.year and d_mulai.month == d_selesai.month:
            if d_mulai.day == d_selesai.day:
                tgl_str = f"{d_mulai.day:02d} {m_mulai} {d_mulai.year}"
            else:
                tgl_str = f"{d_mulai.day:02d} - {d_selesai.day:02d} {m_mulai} {d_mulai.year}"
        elif d_mulai.year == d_selesai.year:
            tgl_str = f"{d_mulai.day:02d} {m_mulai} - {d_selesai.day:02d} {m_selesai} {d_mulai.year}"
        else:
            tgl_str = f"{d_mulai.day:02d} {m_mulai} {d_mulai.year} - {d_selesai.day:02d} {m_selesai} {d_selesai.year}"
            
        try:
            # Mencoba memuat Garamond dari sistem (Windows)
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.pdfbase import pdfmetrics
            pdfmetrics.registerFont(TTFont('Garamond', 'GARA.TTF'))
            pdfmetrics.registerFont(TTFont('Garamond-Italic', 'GARAI.TTF'))
            font_inst = 'Garamond'
            font_inst_it = 'Garamond-Italic'
        except:
            # Fallback ke Times-Roman jika Garamond tidak ditemukan
            font_inst = 'Times-Roman'
            font_inst_it = 'Times-Italic'

        judul_font, judul_size = "Helvetica-Bold", 24
        c.setFont(judul_font, judul_size)
        judul_y = height / 2.0 + 0
        c.drawCentredString(width / 2.0, judul_y, pelatihan.judul_pelatihan)
        
        # Draw underline for judul
        judul_width = c.stringWidth(pelatihan.judul_pelatihan, judul_font, judul_size)
        c.line(width / 2.0 - judul_width / 2.0, judul_y - 4, width / 2.0 + judul_width / 2.0, judul_y - 4)
        
        # Tambahan tulisan "Training"
        c.setFont(font_inst, 14)
        c.drawCentredString(width / 2.0, judul_y - 20, "training")
        
        tempat_font, tempat_size = "Helvetica", 16
        c.setFont(tempat_font, tempat_size)
        tempat_y = height / 2.0 - 90
        c.drawCentredString(width / 2.0, tempat_y, pelatihan.tempat)
        
        # Draw underline for tempat
        tempat_width = c.stringWidth(pelatihan.tempat, tempat_font, tempat_size)
        c.line(width / 2.0 - tempat_width / 2.0, tempat_y - 4, width / 2.0 + tempat_width / 2.0, tempat_y - 4)
        
        c.drawCentredString(width / 2.0, height / 2.0 - 110, tgl_str)

        # Instruktur (Kiri)
        c.setFont(font_inst, 12)
        inst_y = height / 2.0 - 200
        inst_x = width / 2.0 - 150
        c.drawCentredString(inst_x, inst_y, pelatihan.nama_instruktur)
        
        # Draw underline for instruktur
        inst_width = c.stringWidth(pelatihan.nama_instruktur, font_inst, 12)
        c.line(inst_x - inst_width / 2.0, inst_y - 2, inst_x + inst_width / 2.0, inst_y - 2)
        
        c.setFont(font_inst_it, 12)
        c.drawCentredString(width / 2.0 - 150, height / 2.0 - 215, "Instructor")
        
        c.setFont("Helvetica-Oblique", 11)
        c.drawCentredString(width / 2.0, height / 2.0 - 240, f"No. {pelatihan.no_sertifikat}")
        
        # 3. Draw QR Code
        qr_path = pelatihan.qr_code_path
        if qr_path and os.path.exists(qr_path):
            try:
                # Draw QR at bottom center
                c.drawImage(qr_path, (width - (1.2*inch)) / 2.0, 70, width=1.2*inch, height=1.2*inch)
            except Exception as e:
                print(f"Error loading QR: {e}")
        
        # Add page for next participant
        c.showPage()
        
        # 4. Add Syllabus Page (Halaman 2)
        logo_path = 'static/templates/logo-fjm.jpg'
        if os.path.exists(logo_path):
            c.drawImage(logo_path, width - 150, height - 100, width=100, height=100, preserveAspectRatio=True, mask='auto')
            
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, height - 100, pelatihan.judul_pelatihan)
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, height - 130, "TRAINING OUTLINE:")
        # Underline
        c.line(100, height - 132, 250, height - 132)
        
        c.setFont("Helvetica", 12)
        y_pos = height - 160
        if pelatihan.silabus:
            for line in pelatihan.silabus.split('\n'):
                line = line.strip()
                if line:
                    c.drawString(100, y_pos, line)
                    y_pos -= 20
        else:
            c.drawString(100, y_pos, "(Tidak ada silabus yang diisi)")
            
        c.showPage() # End of syllabus page
        
    c.save()
    buffer.seek(0)
    return buffer

def generate_sk_direksi_pdf(pelatihan, template_path=None):
    """
    Generate Surat Keputusan Direksi.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    def draw_bg():
        if template_path and os.path.exists(template_path):
            try:
                c.drawImage(template_path, 0, 0, width=width, height=height)
            except Exception as e:
                print(f"Error loading SK template: {e}")
                
    draw_bg()
    
    # Simple Header
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2.0, height - 120, "SURAT KETERANGAN")
    # underline (approximate width of text)
    c.line(width / 2.0 - 80, height - 122, width / 2.0 + 80, height - 122)
    
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2.0, height - 140, f"Nomor: {pelatihan.no_sk}")
    
    # Body Text
    y_pos = height - 190
    c.setFont("Helvetica", 12)
    c.drawString(50, y_pos, "Yang bertanda tangan di bawah ini:")
    y_pos -= 30
    c.drawString(50, y_pos, "Nama")
    c.drawString(150, y_pos, ": Ir. Dudus Ruhul Kudus")
    y_pos -= 20
    c.drawString(50, y_pos, "Jabatan")
    c.drawString(150, y_pos, ": Direktur PT Fiqry Jaya Manunggal")
    
    y_pos -= 40
    
    from reportlab.platypus import Paragraph
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_JUSTIFY
    styles = getSampleStyleSheet()
    style_justify = ParagraphStyle(name='Justify', fontName='Helvetica', fontSize=12, leading=18, alignment=TA_JUSTIFY)
    
    text1 = f"Dengan ini menerangkan bahwa nama yang tercantum dalam Lampiran-1 Surat Keterangan ini adalah benar merupakan peserta dan narasumber pada kegiatan Pelatihan <b>{pelatihan.judul_pelatihan}</b>."
    p1 = Paragraph(text1, style_justify)
    w1, h1 = p1.wrapOn(c, width - 100, height)
    y_pos -= h1
    p1.drawOn(c, 50, y_pos)
    
    y_pos -= 20
    
    # Menghitung JP (Jumlah Hari x 6)
    jumlah_hari = (pelatihan.tanggal_selesai - pelatihan.tanggal_mulai).days + 1
    jumlah_jp = jumlah_hari * 6
    
    text2 = f"Peserta yang lulus berhak mendapatkan sertifikat dengan jumlah JP ({jumlah_jp}) jam sesuai struktur program yang dipersyaratkan. Lampiran surat ini merupakan satu kesatuan yang tidak terpisahkan dari Surat Keterangan ini. Demikian Surat Keterangan ini dibuat dengan sebenarnya untuk dapat dipergunakan sebagaimana mestinya."
    p2 = Paragraph(text2, style_justify)
    w2, h2 = p2.wrapOn(c, width - 100, height)
    y_pos -= h2
    p2.drawOn(c, 50, y_pos)
    
    # Signature
    d_sk = pelatihan.tanggal_sk
    months_id = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    tgl_sk_str = f"{d_sk.day} {months_id[d_sk.month]} {d_sk.year}"
    
    y_pos -= 60
    c.drawString(width - 250, y_pos, f"Jakarta, {tgl_sk_str}")
    y_pos -= 20
    c.drawString(width - 250, y_pos, "PT Fiqry Jaya Manunggal")
    
    y_pos -= 80
    
    # Menempelkan tanda tangan
    ttd_path = 'static/templates/ttd-dudus.jpg'
    if os.path.exists(ttd_path):
        # mask='auto' biasanya membantu untuk menghilangkan background putih jika ada
        c.drawImage(ttd_path, width - 255, y_pos + 5, width=140, height=65, preserveAspectRatio=True, mask='auto')
        
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width - 250, y_pos, "Ir. Dudus Ruhul Kudus")
    # underline name
    c.line(width - 250, y_pos - 2, width - 120, y_pos - 2)
    c.setFont("Helvetica", 12)
    y_pos -= 16
    c.drawString(width - 250, y_pos, "Direktur Utama")
    
    c.showPage()
    draw_bg()
    
    # Lampiran (Page 2)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2.0, height - 150, "LAMPIRAN - 1 : Daftar Peserta")
    
    c.setFont("Helvetica", 12)
    y = height - 190
    c.drawString(50, y, "Pelatihan")
    c.drawString(150, y, f": {pelatihan.judul_pelatihan}")
    y -= 20
    c.drawString(50, y, "Trainer")
    c.drawString(150, y, f": {pelatihan.nama_instruktur}")
    y -= 20
    
    d_mulai = pelatihan.tanggal_mulai
    d_selesai = pelatihan.tanggal_selesai
    if d_mulai.year == d_selesai.year and d_mulai.month == d_selesai.month:
        if d_mulai.day == d_selesai.day:
            tgl_str = f"{d_mulai.day:02d} {months_id[d_mulai.month]} {d_mulai.year}"
        else:
            tgl_str = f"{d_mulai.day:02d} - {d_selesai.day:02d} {months_id[d_mulai.month]} {d_mulai.year}"
    elif d_mulai.year == d_selesai.year:
        tgl_str = f"{d_mulai.day:02d} {months_id[d_mulai.month]} - {d_selesai.day:02d} {months_id[d_selesai.month]} {d_mulai.year}"
    else:
        tgl_str = f"{d_mulai.day:02d} {months_id[d_mulai.month]} {d_mulai.year} - {d_selesai.day:02d} {months_id[d_selesai.month]} {d_selesai.year}"
        
    c.drawString(50, y, "Waktu")
    c.drawString(150, y, f": {tgl_str}")
    
    y -= 40
    
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors
    
    data = [["No", "Nama Peserta", "Perusahaan", "Keterangan"]]
    for i, peserta in enumerate(pelatihan.peserta, 1):
        data.append([str(i), peserta.nama_peserta, peserta.perusahaan or "", peserta.keterangan or ""])
        
    avail_w = width - 100
    col_widths = [40, 200, 150, avail_w - 390]
    
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (2,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    avail_h = y - 50
    table_to_draw = t
    
    while True:
        w, h = table_to_draw.wrapOn(c, avail_w, avail_h)
        if h <= avail_h:
            table_to_draw.drawOn(c, 50, y - h)
            break
        else:
            parts = table_to_draw.split(avail_w, avail_h)
            if not parts:
                table_to_draw.drawOn(c, 50, y - h)
                break
            part1 = parts[0]
            w1, h1 = part1.wrapOn(c, avail_w, avail_h)
            part1.drawOn(c, 50, y - h1)
            
            c.showPage()
            draw_bg()
            y = height - 100
            avail_h = y - 50
            if len(parts) > 1:
                table_to_draw = parts[1]
            else:
                break
    
    c.save()
    buffer.seek(0)
    return buffer
