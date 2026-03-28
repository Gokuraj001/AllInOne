from flask import Flask, render_template, request, send_file
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from pdf2image import convert_from_path
import img2pdf
import pdfplumber
import os
import zipfile
import fitz  # PyMuPDF
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')


# ===================== MERGE PDF =====================
@app.route('/merge', methods=['GET', 'POST'])
def merge_pdf():
    if request.method == 'POST':
        files = request.files.getlist('pdfs')
        merger = PdfMerger()

        for file in files:
            if file.filename == '':
                continue
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            merger.append(filepath)

        output_path = os.path.join(OUTPUT_FOLDER, 'merged.pdf')
        merger.write(output_path)
        merger.close()

        return send_file(output_path, as_attachment=True)

    return render_template('merge.html')


# ===================== SPLIT PDF =====================
@app.route('/split', methods=['GET', 'POST'])
def split_pdf():
    if request.method == 'POST':
        file = request.files['pdf']
        page_number = int(request.form['page_number'])

        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        reader = PdfReader(filepath)

        if page_number < 1 or page_number > len(reader.pages):
            return f"<h2>Invalid page number. This PDF has only {len(reader.pages)} pages.</h2>"

        writer = PdfWriter()
        writer.add_page(reader.pages[page_number - 1])

        output_path = os.path.join(OUTPUT_FOLDER, 'split_page.pdf')
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        return send_file(output_path, as_attachment=True)

    return render_template('split.html')


# ===================== ROTATE PDF =====================
@app.route('/rotate', methods=['GET', 'POST'])
def rotate_pdf():
    if request.method == 'POST':
        file = request.files['pdf']
        angle = int(request.form['angle'])

        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        reader = PdfReader(filepath)
        writer = PdfWriter()

        for page in reader.pages:
            page.rotate_clockwise(angle)
            writer.add_page(page)

        output_path = os.path.join(OUTPUT_FOLDER, 'rotated.pdf')
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        return send_file(output_path, as_attachment=True)

    return render_template('rotate.html')


# ===================== ORGANIZE PDF =====================
@app.route('/organize', methods=['GET', 'POST'])
def organize_pdf():
    if request.method == 'POST':
        file = request.files['pdf']
        pages_to_keep = request.form['pages']

        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        reader = PdfReader(filepath)
        writer = PdfWriter()

        try:
            pages = [int(p.strip()) - 1 for p in pages_to_keep.split(',')]
        except ValueError:
            return "<h2>Invalid input. Please enter pages like: 1,3,5</h2>"

        for p in pages:
            if 0 <= p < len(reader.pages):
                writer.add_page(reader.pages[p])

        output_path = os.path.join(OUTPUT_FOLDER, 'organized.pdf')
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        return send_file(output_path, as_attachment=True)

    return render_template('organize.html')


# ===================== JPG TO PDF =====================
@app.route('/jpg-to-pdf', methods=['GET', 'POST'])
def jpg_to_pdf():
    if request.method == 'POST':
        files = request.files.getlist('images')
        image_paths = []

        for file in files:
            if file.filename == '':
                continue
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            image_paths.append(filepath)

        if not image_paths:
            return "<h2>No valid image files uploaded.</h2>"

        output_path = os.path.join(OUTPUT_FOLDER, 'images_to_pdf.pdf')

        with open(output_path, "wb") as f:
            f.write(img2pdf.convert(image_paths))

        return send_file(output_path, as_attachment=True)

    return render_template('jpg_to_pdf.html')

# ===================== PDF TO JPG =====================
@app.route('/pdf-to-jpg', methods=['GET', 'POST'])
def pdf_to_jpg():
    if request.method == 'POST':
        file = request.files['pdf']
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        try:
            images = convert_from_path(filepath)
        except Exception as e:
            return f"<h2>Error converting PDF to JPG: {str(e)}</h2>"

        zip_path = os.path.join(OUTPUT_FOLDER, 'pdf_images.zip')

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for i, image in enumerate(images):
                img_path = os.path.join(OUTPUT_FOLDER, f'page_{i+1}.jpg')
                image.save(img_path, 'JPEG')
                zipf.write(img_path, os.path.basename(img_path))

        return send_file(zip_path, as_attachment=True)

    return render_template('pdf_to_jpg.html')


# ===================== PDF TO TEXT =====================
@app.route('/pdf-to-text', methods=['GET', 'POST'])
def pdf_to_text():
    if request.method == 'POST':
        file = request.files['pdf']
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        text_output = ""

        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_output += text + "\n\n"

        output_path = os.path.join(OUTPUT_FOLDER, 'extracted_text.txt')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_output)

        return send_file(output_path, as_attachment=True)

    return render_template('pdf_to_text.html')


# ===================== HTML TO PDF =====================
@app.route('/html-to-pdf', methods=['GET', 'POST'])
def html_to_pdf():
    if request.method == 'POST':
        html_content = request.form['html_content']

        output_path = os.path.join(OUTPUT_FOLDER, 'html_to_pdf.pdf')

        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter

        y = height - 40
        lines = html_content.split('\n')

        c.setFont("Helvetica", 10)

        for line in lines:
            if y < 40:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 40
            c.drawString(40, y, line[:100])  # Avoid too-long lines
            y -= 15

        c.save()

        return send_file(output_path, as_attachment=True)

    return render_template('html_to_pdf.html')


# ===================== COMPRESS PDF =====================
@app.route('/compress', methods=['GET', 'POST'])
def compress_pdf():
    if request.method == 'POST':
        file = request.files['pdf']
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        output_path = os.path.join(OUTPUT_FOLDER, 'compressed.pdf')

        doc = fitz.open(filepath)
        doc.save(output_path, garbage=4, deflate=True)
        doc.close()

        return send_file(output_path, as_attachment=True)

    return render_template('compress.html')


# ===================== REPAIR PDF =====================
@app.route('/repair', methods=['GET', 'POST'])
def repair_pdf():
    return "<h2>Repair PDF feature coming soon 🚧</h2>"


# ===================== PDF TO WORD =====================
@app.route('/pdf-to-word')
def pdf_to_word():
    return "<h2>Coming Soon 🚧</h2>"


# ===================== WORD TO PDF =====================
@app.route('/word-to-pdf')
def word_to_pdf():
    return "<h2>Coming Soon 🚧</h2>"


if __name__ == '__main__':
    app.run(debug=True)