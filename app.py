from flask import Flask, render_template, request, send_file, current_app
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import img2pdf
import pdfplumber
import os
import zipfile
import pymupdf as fitz  # PyMuPDF
import uuid
import pandas as pd
import tabula
from pdf2docx import Converter
from pdf2image import convert_from_path
from pptx import Presentation
from pptx.util import Inches
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image, ImageOps
from werkzeug.utils import secure_filename


# ===================== APP SETUP =====================
def create_app():
    app = Flask(__name__)

    app.config.from_mapping(
        UPLOAD_FOLDER=os.path.join(app.root_path, 'uploads'),
        OUTPUT_FOLDER=os.path.join(app.root_path, 'outputs')
    )

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

    # ===================== HELPER FUNCTION =====================
    def save_uploaded_file(file, file_type='pdf'):
        if not file or file.filename == '':
            return None, None

        filename = secure_filename(file.filename)

        allowed = {
            'pdf': ('.pdf',),
            'image': ('.jpg', '.jpeg', '.png')
        }

        if file_type in allowed:
            if not filename.lower().endswith(allowed[file_type]):
                return None, None

        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filename, filepath
    
        # ===================== PDF CONVERTER HELPERS =====================
    def convert_pdf_to_word(pdf_path):
        output_filename = f"converted_{uuid.uuid4().hex}.docx"
        output_path = os.path.join(current_app.config['OUTPUT_FOLDER'], output_filename)

        cv = Converter(pdf_path)
        cv.convert(output_path, start=0, end=None)
        cv.close()

        return output_filename, output_path


    def convert_pdf_to_excel(pdf_path):
        output_filename = f"converted_{uuid.uuid4().hex}.xlsx"
        output_path = os.path.join(current_app.config['OUTPUT_FOLDER'], output_filename)

        try:
            tables = tabula.read_pdf(
                pdf_path,
                pages='all',
                multiple_tables=True,
                pandas_options={'header': None},
                lattice=True  # helps detect tables better
            )
        except Exception as e:
            raise Exception(f"Tabula failed: {str(e)}")

        if not tables or len(tables) == 0:
            raise Exception("No tables found in this PDF. Try another file with proper tables.")

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for i, table in enumerate(tables):
                table.to_excel(writer, sheet_name=f"Table_{i+1}", index=False)

        return output_filename, output_path


    def convert_pdf_to_ppt(pdf_path):
        output_filename = f"converted_{uuid.uuid4().hex}.pptx"
        output_path = os.path.join(current_app.config['OUTPUT_FOLDER'], output_filename)

        image_folder = os.path.join(current_app.config['OUTPUT_FOLDER'], f"ppt_pages_{uuid.uuid4().hex}")
        os.makedirs(image_folder, exist_ok=True)

        # IMPORTANT: Change this if your Poppler path is different
        poppler_path = r"C:\poppler-25.12.0\Library\bin"

        pages = convert_from_path(pdf_path, dpi=200, poppler_path=poppler_path)

        prs = Presentation()

        for i, page in enumerate(pages):
            img_path = os.path.join(image_folder, f'page_{i+1}.png')
            page.save(img_path, "PNG")

            slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank slide
            slide_width = prs.slide_width
            slide_height = prs.slide_height

            slide.shapes.add_picture(img_path, 0, 0, width=slide_width, height=slide_height)

        prs.save(output_path)

        return output_filename, output_path

    # ===================== HOME =====================
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
                filename, filepath = save_uploaded_file(file, 'pdf')
                if filename:
                    merger.append(filepath)

            output_path = os.path.join(current_app.config['OUTPUT_FOLDER'], 'merged.pdf')
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

            filename, filepath = save_uploaded_file(file, 'pdf')
            if not filename:
                return "<h2>No file uploaded or invalid PDF.</h2>"

            reader = PdfReader(filepath)

            if page_number < 1 or page_number > len(reader.pages):
                return f"<h2>Invalid page number. This PDF has only {len(reader.pages)} pages.</h2>"

            writer = PdfWriter()
            writer.add_page(reader.pages[page_number - 1])

            output_path = os.path.join(current_app.config['OUTPUT_FOLDER'], 'split_page.pdf')
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

            filename, filepath = save_uploaded_file(file, 'pdf')
            if not filename:
                return "<h2>No file uploaded or invalid PDF.</h2>"

            reader = PdfReader(filepath)
            writer = PdfWriter()

            for page in reader.pages:
                page.rotate_clockwise(angle)
                writer.add_page(page)

            output_path = os.path.join(current_app.config['OUTPUT_FOLDER'], 'rotated.pdf')
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

            filename, filepath = save_uploaded_file(file, 'pdf')
            if not filename:
                return "<h2>No file uploaded or invalid PDF.</h2>"

            reader = PdfReader(filepath)
            writer = PdfWriter()

            try:
                pages = [int(p.strip()) - 1 for p in pages_to_keep.split(',')]
            except ValueError:
                return "<h2>Invalid input. Please enter pages like: 1,3,5</h2>"

            for p in pages:
                if 0 <= p < len(reader.pages):
                    writer.add_page(reader.pages[p])

            output_path = os.path.join(current_app.config['OUTPUT_FOLDER'], 'organized.pdf')
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            return send_file(output_path, as_attachment=True)

        return render_template('organize.html')
    
    # ===================== COMPRESS IMAGE =====================
    @app.route('/compress_image', methods=['GET', 'POST'])
    def compress_image_tool():
        if request.method == 'POST':
            file = request.files.get('image')

            if not file:
                return "<h3>No image uploaded</h3>"

            # Save input file
            filename = secure_filename(file.filename)
            input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)

            # Output path
            output_path = os.path.join(current_app.config['OUTPUT_FOLDER'], 'compressed_image.jpg')

            # Get form values
            mode = request.form.get('mode')
            target_size = request.form.get('target_size')

            # Open image
            img = Image.open(input_path)

            # Convert to RGB (important for JPG)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # 🎯 Compression logic

            # If user gives target size
            if target_size:
                target_size = int(target_size) * 1024  # KB → bytes
                quality = 90

                while quality > 10:
                    img.save(output_path, "JPEG", quality=quality, optimize=True)
                    if os.path.getsize(output_path) <= target_size:
                        break
                    quality -= 5

            else:
                # Mode-based compression
                if mode == "maximum":
                    quality = 30
                elif mode == "medium":
                    quality = 60
                else:  # minimum
                    quality = 85

                img.save(output_path, "JPEG", quality=quality, optimize=True)

            return send_file(output_path, as_attachment=True)

        return render_template('compress_image.html')

    # ===================== JPG TO PDF =====================
    @app.route('/jpg_to_pdf', methods=['GET', 'POST'])
    def jpg_to_pdf():
        if request.method == 'POST':
            files = request.files.getlist('images')
            cleaned_image_paths = []

            for index, file in enumerate(files):
                filename, filepath = save_uploaded_file(file, 'image')
                if not filename:
                    continue

                try:
                    img = Image.open(filepath)
                    img = ImageOps.exif_transpose(img)

                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")

                    cleaned_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"cleaned_{index}.jpg")
                    img.save(cleaned_path, "JPEG")
                    cleaned_image_paths.append(cleaned_path)

                except Exception as e:
                    return f"<h2>Error processing image {filename}: {str(e)}</h2>"

            if not cleaned_image_paths:
                return "<h2>No valid image files uploaded.</h2>"

            output_path = os.path.join(current_app.config['OUTPUT_FOLDER'], 'images_to_pdf.pdf')

            try:
                with open(output_path, "wb") as f:
                    f.write(img2pdf.convert(cleaned_image_paths))
            except Exception as e:
                return f"<h2>Error converting images to PDF: {str(e)}</h2>"

            return send_file(output_path, as_attachment=True)

        return render_template('jpg_to_pdf.html')

    # ===================== PDF TO JPG (NO POPPLER) =====================
    @app.route('/pdf_to_jpg', methods=['GET', 'POST'])
    def pdf_to_jpg():
        if request.method == 'POST':
            file = request.files['pdf']
            filename, filepath = save_uploaded_file(file, 'pdf')
            if not filename:
                return "<h2>No file uploaded or invalid PDF.</h2>"

            try:
                doc = fitz.open(filepath)
                zip_path = os.path.join(current_app.config['OUTPUT_FOLDER'], 'pdf_images.zip')

                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for i, page in enumerate(doc):
                        pix = page.get_pixmap()
                        img_path = os.path.join(current_app.config['OUTPUT_FOLDER'], f'page_{i+1}.jpg')
                        pix.save(img_path)
                        zipf.write(img_path, os.path.basename(img_path))

                doc.close()
                return send_file(zip_path, as_attachment=True)

            except Exception as e:
                return f"<h2>Error converting PDF to JPG: {str(e)}</h2>"

        return render_template('pdf_to_jpg.html')

    # ===================== PDF TO TEXT =====================
    @app.route('/pdf_to_text', methods=['GET', 'POST'])
    def pdf_to_text():
        if request.method == 'POST':
            file = request.files['pdf']
            filename, filepath = save_uploaded_file(file, 'pdf')
            if not filename:
                return "<h2>No file uploaded or invalid PDF.</h2>"

            text_output = ""

            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_output += text + "\n\n"

            output_path = os.path.join(current_app.config['OUTPUT_FOLDER'], 'extracted_text.txt')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text_output)

            return send_file(output_path, as_attachment=True)

        return render_template('pdf_to_text.html')

    # ===================== HTML TO PDF =====================
    @app.route('/html-to-pdf', methods=['GET', 'POST'])
    def html_to_pdf():
        if request.method == 'POST':
            html_content = request.form['html_content']

            output_path = os.path.join(current_app.config['OUTPUT_FOLDER'], 'html_to_pdf.pdf')

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
                c.drawString(40, y, line[:100])
                y -= 15

            c.save()

            return send_file(output_path, as_attachment=True)

        return render_template('html_to_pdf.html')
    
        # ===================== PDF CONVERTER =====================
    @app.route('/pdf_converter', methods=['GET', 'POST'])
    def pdf_converter():
        if request.method == 'POST':
            file = request.files.get('file')
            convert_to = request.form.get('convert_to')

            filename, filepath = save_uploaded_file(file, 'pdf')
            if not filename:
                return "<h2>No file uploaded or invalid PDF.</h2>"

            if not convert_to:
                return "<h2>Please select a conversion format.</h2>"

            try:
                if convert_to == 'word':
                    output_filename, output_path = convert_pdf_to_word(filepath)

                elif convert_to == 'excel':
                    output_filename, output_path = convert_pdf_to_excel(filepath)

                elif convert_to == 'ppt':
                    output_filename, output_path = convert_pdf_to_ppt(filepath)

                else:
                    return "<h2>Invalid conversion format selected.</h2>"

                return send_file(output_path, as_attachment=True)

            except Exception as e:
                return f"<h2>Conversion failed: {str(e)}</h2>"

        return render_template('pdf_converter.html')
    
    # ===================== DOWNLOAD =====================
    @app.route('/download/<filename>')
    def download_file(filename):
        file_path = os.path.join(current_app.config['OUTPUT_FOLDER'], filename)
        return send_file(file_path, as_attachment=True)

    # ===================== COMPRESS PDF =====================
    @app.route('/compress', methods=['GET', 'POST'])
    def compress_pdf():
        if request.method == 'POST':
            file = request.files['pdf']

            filename, filepath = save_uploaded_file(file, 'pdf')
            if not filename:
                return "<h2>No file uploaded or invalid PDF.</h2>"

            output_path = os.path.join(current_app.config['OUTPUT_FOLDER'], 'compressed.pdf')

            # Original size
            original_size = os.path.getsize(filepath)

            # Compress using PyMuPDF
            doc = fitz.open(filepath)
            doc.save(output_path, garbage=4, deflate=True)
            doc.close()

            # Compressed size
            compressed_size = os.path.getsize(output_path)

            # Reduction calculations
            reduced_bytes = original_size - compressed_size
            reduction_percent = (reduced_bytes / original_size) * 100 if original_size > 0 else 0

            return render_template(
                'compress_result.html',
                original_size=round(original_size / 1024, 2),
                compressed_size=round(compressed_size / 1024, 2),
                reduced_size=round(reduced_bytes / 1024, 2),
                reduction_percent=round(reduction_percent, 2),
                download_file='compressed.pdf'
          )

        return render_template('compress.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)