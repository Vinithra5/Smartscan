from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image
import pytesseract
import boto3
import aws_config
import time
import os

folder_to_watch = r"C:\Users\sadras vinithra\OneDrive\Pictures\Screenshots 1"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"

s3 = boto3.client(
    "s3",
    aws_access_key_id=aws_config.aws_access_key,
    aws_secret_access_key=aws_config.aws_secret_key,
    region_name=aws_config.region
)

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(".png"):
            print("New screenshot:", event.src_path)
            try:
                img = Image.open(event.src_path)
                text = pytesseract.image_to_string(img)
                print("Extracted text:\n", text.strip())

                filename = os.path.basename(event.src_path)
                s3.upload_file(event.src_path, aws_config.bucket_name, f"screenshots/{filename}")
                print("Uploaded to S3:", filename)
                print("-" * 50)
            except Exception as e:
                print("Error:", e)

if __name__ == "__main__":
    if not os.path.exists(folder_to_watch):
        os.makedirs(folder_to_watch)

    observer = Observer()
    observer.schedule(MyHandler(), folder_to_watch, recursive=False)
    observer.start()
    print("Watching folder:", folder_to_watch)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
