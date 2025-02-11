import json
import os
import boto3
from boto3.dynamodb.conditions import Attr
from decimal import Decimal

DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)

def get_user_handler(event, context):
    try:
        # affiliation 파라미터 추출
        affiliation = event.get('queryStringParameters', {}).get('affiliation') if event.get('queryStringParameters') else None
        
        # 전체 유저 조회
        if affiliation == 'all':
            print("전체 유저 데이터 조회")
            response = table.scan()
            items = response.get('Items', [])  # items 초기화 추가
        
        # 소속 리스트 조회
        elif affiliation == 'affiliation_list':
            print("소속 리스트 조회")
            response = table.scan(
                ProjectionExpression="affiliation"
            )

            affiliation_items = response.get('Items', [])  # 변수 이름 변경
            affiliations = {item['affiliation'] for item in affiliation_items}
            print(f"중복 제거 후 소속 리스트: {affiliations}")
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json; charset=UTF-8"
                },
                "body": json.dumps({
                    "message": "소속 리스트 가져옴",
                    "affiliation": list(affiliations)  # 수정
                }, ensure_ascii=False)
            }
        
        # 특정 소속별 조회
        else:
            response = table.scan(
                FilterExpression=Attr('affiliation').eq(affiliation)
            )
            items = response.get('Items', [])  # items 초기화 추가

        # 데이터 가공 및 변환
        for item in items:
            item['name'] = str(item['name'])
            item['affiliation'] = str(item['affiliation'])
            item['nickname'] = str(item['nickname'])
            item['coin_1'] = str(item['coin_1'])
            item['coin_2'] = str(item['coin_2'])
            item['coin_3'] = str(item['coin_3'])
            item['balance'] = int(item['balance'])

        # 정렬 후 반환
        sorted_items = sorted(items, key=lambda x: x['balance'], reverse=True)
        print("데이터 변환 및 정렬 완료")

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json; charset=UTF-8"
            },
            "body": json.dumps({
                "message": "유저 데이터 가져옴",
                "data": sorted_items
            }, ensure_ascii=False, cls=DecimalEncoder)
        }
    
    except Exception as e:
        print(f"에러 발생 : {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "유저 데이터 에러",
                "error": str(e)
            })
        }
