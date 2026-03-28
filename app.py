from flask import Flask, render_template, request, send_file
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image
import img2pdf
import pdfplumber
import os
import zipfile

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
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
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

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        reader = PdfReader(filepath)
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

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        reader = PdfReader(filepath)
        writer = PdfWriter()

        for page in reader.pages:
            page.rotate(angle)
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
        pages_to_keep = request.form['pages']  # Example: 1,3,5

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        reader = PdfReader(filepath)
        writer = PdfWriter()

        pages = [int(p.strip()) - 1 for p in pages_to_keep.split(',')]

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
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            image_paths.append(filepath)

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
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        images = convert_from_path(filepath)
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
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        text_output = ""

        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text_output += page.extract_text() + "\n\n"

        output_path = os.path.join(OUTPUT_FOLDER, 'extracted_text.txt')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_output)

        return send_file(output_path, as_attachment=True)

    return render_template('pdf_to_text.html')


# ===================== HTML TO PDF =====================
@app.route('/html-to-pdf', methods=['GET', 'POST'])
def html_to_pdf():
    return "<h2>Coming Soon 🚧</h2>"


# ===================== COMPRESS PDF =====================
@app.route('/compress', methods=['GET', 'POST'])
def compress_pdf():
    return "<h2>Coming Soon 🚧</h2>"


# ===================== REPAIR PDF =====================
@app.route('/repair', methods=['GET', 'POST'])
def repair_pdf():
    return "<h2>Coming Soon 🚧</h2>"


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