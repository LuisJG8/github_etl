import os
import boto3 
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET_NAME = "github-etl-data-bucket"

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "us-east-1")
)


region = os.getenv("AWS_REGION", "us-east-1")

s3_client.create_bucket(Bucket=S3_BUCKET_NAME)

print("READY")