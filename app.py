import os
import json
import pytesseract
import yake
import re
import cv2
import numpy as np
from flask import Flask, render_template, request, send_from_directory, redirect
from PIL import Image, ImageEnhance, ImageFilter
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
CACHE_FILE = 'cache.json'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

kw_model = yake.KeywordExtractor(lan="en", n=1, top=5)
def clean_text(text):
    return re.sub(r'\s{2,}', ' ', re.sub(r'[^\x00-\x7F]+', '', text)).strip()
def extract_text(image_path):
    try:
        image = cv2.imread(image_path)
        image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
        raw_text = pytesseract.image_to_string(thresh, config='--psm 6')
        return clean_text(raw_text)
    except Exception as e:
        return f"Error reading image: {e}"


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(data):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    query = request.args.get('search', '').lower()
    tag_filter = request.args.get('tag', '').lower()

    cache = load_cache()
    screenshots = []

    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            if filename in cache:
                entry = cache[filename]
            else:
                path = os.path.join(UPLOAD_FOLDER, filename)
                text = extract_text(path)
                keywords = kw_model.extract_keywords(text)
                tags = [kw[0] for kw in keywords]
                timestamp = os.path.getmtime(path)
                date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
                entry = {"text": text, "tags": tags, "date": date}
                cache[filename] = entry

            if (
                query in entry["text"].lower()
                or tag_filter in [t.lower() for t in entry["tags"]]
                or (query == '' and tag_filter == '')
            ):
                screenshots.append({
                    "filename": filename,
                    "text": entry["text"],
                    "date": entry["date"],
                    "tags": entry["tags"]
                })

    save_cache(cache)
    screenshots.sort(key=lambda x: x['date'], reverse=True)
    return render_template('index.html', screenshots=screenshots, search=query)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'screenshot' not in request.files:
        return redirect('/')
    file = request.files['screenshot']
    if file.filename == '':
        return redirect('/')
    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        cache = load_cache()
        if filename in cache:
            del cache[filename]
            save_cache(cache)

        return redirect('/')

@app.route('/clear-cache')
def clear_cache():
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
    return redirect('/')

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
