import base64
import json
import boto3
import pandas as pd
from fastparquet import write
from io import BytesIO

def KDF_S3_parquet_handler(event, context):
    """ 
    Kinesis Data Firehose -> Lambda Transform 예시:
    1. base64로 인코딩된 JSON 레코드를 디코딩
    2. JSON → Pandas DataFrame
    3. Parquet (SNAPPY 압축) 변환
    4. base64로 다시 인코딩하여 Firehose로 반환

    개선사항:
    - 레코드 수 및 처리 결과(Ok / ProcessingFailed) 로그 추가
    """

    # Firehose가 전달한 레코드 목록
    records_in_batch = event.get("records", [])
    batch_size = len(records_in_batch)

    print(f"[INFO] Received {batch_size} record(s) from Firehose.")

    output = []  # 변환된 레코드들을 담을 리스트
    success_count = 0
    fail_count = 0

    for idx, record in enumerate(records_in_batch):
        # 1. base64 디코딩
        payload = base64.b64decode(record["data"]).decode("utf-8")

        try:
            # 2. JSON 파싱
            data_dict = json.loads(payload)

            # Pandas DataFrame으로 변환 (단일 레코드를 하나의 행으로 처리)
            df = pd.DataFrame([data_dict])

            # 3. Parquet 변환
            buffer = BytesIO()
            write(buffer, df, compression='SNAPPY')
            buffer.seek(0)
            parquet_data = buffer.read()

            # 4. base64 인코딩 후 Firehose에 다시 전달
            record["data"] = base64.b64encode(parquet_data).decode("utf-8")
            record["result"] = "Ok"
            success_count += 1

        except Exception as e:
            # 변환 실패 시, record["result"]를 'ProcessingFailed'로 설정
            print(f"[ERROR] Failed to process record #{idx}: {e}")
            record["result"] = "ProcessingFailed"
            fail_count += 1

        output.append(record)

    print(f"[INFO] Processing completed. Success={success_count}, Failed={fail_count}")

    # Firehose 변환 스펙에 맞춰 반환
    return {"records": output}
