import boto3
from botocore.exceptions import NoCredentialsError
import os

# Set your details
BUCKET_NAME = 'swiftscan-bucket'
FILE_PATH = 'output/screenshot.png'  # Change this if your image name or path is different
S3_FILE_NAME = 'screenshots/screenshot.png'

# Initialize S3
s3 = boto3.client('s3')

def upload_file():
    try:
        s3.upload_file(FILE_PATH, BUCKET_NAME, S3_FILE_NAME)
        print(f"Uploaded '{FILE_PATH}' to S3 bucket as '{S3_FILE_NAME}'")
    except FileNotFoundError:
        print("File not found!")
    except NoCredentialsError:
        print("AWS credentials not available!")

if __name__ == "__main__":
    upload_file()
