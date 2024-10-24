import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr
from decimal import Decimal, getcontext, Inexact, Rounded

DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)

def get_user_handler(event, context):
    try:
        print("람다 함수 시작 - get users data")

        department = event.get('queryStringParameters', {}).get('department') if event.get('queryStringParameters') else None
        
        if department == 'all':
            print("전체 유저 데이터 조회")
            response = table.scan()
        elif department == 'department_list':
            print("학과리스트 조회")
            response = table.scan(
                ProjectionExpression="department"
            )

            items = response.get('Items', [])
            departments = {item['department'] for item in items}
            print(f"중복 제거 후 학과 리스트: {departments}")
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json; charset=UTF-8"
                },
                "body": json.dumps({
                    "message": "학과 리스트 가져옴",
                    "departments": list(departments)
                }, ensure_ascii=False)
            }
        else:
            print(f"'{department}' 학과 유저 데이터 조회")
            response = table.scan(
                FilterExpression=Attr('department').eq(department)
            )

        items = response.get('Items', [])
        print("DynamoDB 에서 데이터 가져옴")

        for item in items:
            item['student_id'] = str(item['student_id'])
            item['name'] = str(item['name'])
            item['department'] = str(item['department'])
            item['nickname'] = str(item['nickname'])
            item['coin_1'] = str(item['coin_1'])
            item['coin_2'] = str(item['coin_2'])
            item['coin_3'] = str(item['coin_3'])
            item['balance'] = int(item['balance'])

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