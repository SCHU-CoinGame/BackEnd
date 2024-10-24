import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr
from decimal import Decimal, getcontext, Inexact, Rounded

DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE)

def get_department_list_handler(event, context):
    try:
        print("람다 함수 시작 - 학과 리스트 조회")

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
    
    except Exception as e:
        print(f"에러 발생: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "학과 리스트 조회 중 에러 발생",
                "error": str(e)
            })
        }