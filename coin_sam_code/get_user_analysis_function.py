import json
import boto3
import os

# S3 클라이언트 설정
s3 = boto3.client('s3')

# 환경 변수에서 S3 버킷 및 경로 설정
BUCKET_NAME = os.environ['BUCKET_NAME']
PREFIX = os.environ['PREFIX']

# 읽어올 파일 리스트
FILES = [
    'ai_recommend_1_ratio.json',
    'ai_recommend_2_ratio.json',
    'avg_balance.json',
    'coin_avg_sell_time.json',
    'coin_ratio.json',
    'leverage_ratio.json',
    'page_time_avg.json',
    'sell_time_avg.json',
    'top_10_percent_coin_ratio.json',
    'top_10_percent_avg_sell_time_by_category.json',
    'ai_recommend_1_avg_balance.json',
    'ai_recommend_2_avg_balance.json',
    'leverage_avg_balance.json'
]

def get_user_analysis_handler(event, context):
    try:
        # 결과 데이터를 저장할 딕셔너리 초기화
        result_data = {}

        # print("[INFO] 시작: 각 파일 개별 내용 확인")  # 시작 로그

        # 각 파일 읽기 및 출력
        for file_name in FILES:
            file_key = PREFIX + file_name
            response = s3.get_object(Bucket=BUCKET_NAME, Key=file_key)
            file_content = response['Body'].read().decode('utf-8').strip()  # 공백 제거

            # 개별 JSON 데이터 출력
            # print(f"[INFO] 파일명: {file_name}")
            # print(f"[INFO] 내용: {file_content}")

            # JSON 형식 검증 및 변환
            try:
                # 파일 내용이 여러 줄로 구성된 경우 배열로 감싸서 처리
                if '\n' in file_content:
                    file_content = '[' + ','.join(file_content.splitlines()) + ']'
                
                parsed_content = json.loads(file_content)  # JSON 파싱
                result_data[file_name.replace('.json', '')] = parsed_content
            except json.JSONDecodeError as e:
                print(f"[ERROR] JSON 파싱 오류 - 파일명: {file_name}, 오류: {e}")
                result_data[file_name.replace('.json', '')] = {"error": "Invalid JSON format"}

        # print("[INFO] 완료: 파일 병합 결과 출력")  # 병합 완료 로그
        # print(f"[INFO] 병합된 데이터: {json.dumps(result_data, indent=4)}")

        # HTTP 응답 반환
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(result_data)
        }

    except Exception as e:
        # 오류 발생 시 HTTP 500 응답 반환
        print(f"[ERROR] 예외 발생: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': str(e)})
        }
