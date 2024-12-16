import json
import os
import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO
import pandas as pd
from datetime import datetime
import base64

s3_client = boto3.client('s3')

RAW_DATA_BUCKET = os.environ['RAW_DATA_BUCKET']
RAW_DATA_PREFIX = os.environ['RAW_DATA_PREFIX', "ClickStream/raw-data/"]

def KDS_Firehose_S3_Parquet_handler(event, context):
    records = event['records']
    output = []

    for record in records:
        try:
            payload = json.loads(json.loads(record['data']).decode('utf-8'))
            table = conver_to_parquet([payload])

            s3_key = create_s3_key(context.aws_request_id)
            full_s3_path = f"{RAW_DATA_PREFIX}{s3_key}"

            buffer = BytesIO()
            pq.write_table(table, buffer)
            buffer.seek(0)

            s3_client.upload_fileobj(buffer, RAW_DATA_BUCKET, full_s3_path)

            output_record = {
                'recordId': record['recordId'],
                'result': 'Ok',
                'data': base64.b64encode(record['data']).decode('utf-8')
            }
            output.append(output_record)
        except Exception as e:
            print(f"Error processing record: {str(e)}")
            output_record = {
                'recordId': record['recordId'],
                'result': 'ProcessingFailed',
                'data': record['data']
            }
            output.append(output_record)
    return {'records': output}

def conver_to_parquet(records):
    df = pd.DataFrame(records)
    table = pa.Table.from_pandas(df)
    return table

def create_s3_key(request_id):
    now = datetime.now()
    year, month, day = now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")
    s3_key = f"year={year}/month={month}/day={day}/part-{request_id}.parquet"
    return s3_key