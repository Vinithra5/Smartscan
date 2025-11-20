#Smartscan
SmartScan is a simple web tool that turns screenshots into searchable text. It uses Tesseract OCR to extract text from images and YAKE to automatically generate keyword tags, making it easy to organize and find information quickly.

Features

Upload images or screenshots

Extract text using OCR

Auto-generate smart keyword tags

Clean, lightweight Flask UI

Run Locally
git clone https://github.com/Vinithra5/Smartscan.git
cd Smartscan

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
python app.py


Open in browser:

http://127.0.0.1:5000
