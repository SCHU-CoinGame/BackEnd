import json
import boto3
import os
import base64
from fastparquet import write
from datetime import datetime
from io import BytesIO
import pandas as pd


s3_client = boto3.client('s3')

RAW_DATA_BUCKET = os.environ['RAW_DATA_BUCKET']
RAW_DATA_PREFIX = os.environ.get('RAW_DATA_PREFIX', "ClickStream/unprocessed/")

def KDS_to_S3_parquet_handler(event, context):
    try:
        records = []
        for record in event['Records']:
            try:
                decoded_data = base64.b64decode(record['kinesis']['data']).decode('utf-8')
                payload = json.loads(decoded_data)
                if not isinstance(payload, dict):
                    raise ValueError("Invalid data format: Not a JSON object")
                records.append(payload)
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Skipping invalid record: {e}")

        if records:
            s3_key = create_s3_key(context.aws_request_id)
            upload_to_s3(records, s3_key)

        return {"statusCode": 200, "body": "Data processed successfully"}
    
    except Exception as e:
        print(f"Error processing Kinesis records: {str(e)}")
        return {"statusCode": 500, "body": f"Error: {str(e)}"}

def create_s3_key(request_id):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
    s3_key = f"{RAW_DATA_PREFIX}part-{request_id}-{timestamp}.parquet"
    return s3_key

def upload_to_s3(records, s3_key):
    df = pd.DataFrame(records)
    try:
        df['balance'] = pd.to_numeric(df['balance'], errors='raise').astype('float64')
        print(f"[INFO] Successfully converted 'balance' to numeric. Sample data: {df['balance'].head().tolist()}")
    except Exception as e:
        print(f"[ERROR] Failed to convert 'balance' to numeric: {e}")
        raise
    
    buffer = BytesIO()
    write(buffer, df, compression='SNAPPY')
    buffer.seek(0)
    s3_client.upload_fileobj(buffer, RAW_DATA_BUCKET, s3_key)
    print(f"Uploaded Parquet file to S3: s3://{RAW_DATA_BUCKET}/{s3_key}")