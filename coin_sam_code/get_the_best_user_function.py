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

def get_the_best_user_handler(event, context):
    try:
        print("람다 함수 시작 - get the best user")

        response = table.scan()

        items = response.get('Items', [])

        if not items:
            return {
                "statusCode": 404,
                "body": json.dumps({
                    "messsage": "1등 유저 데이터를 찾을 수 없습니다."
                })
            }
        print("DynamoDB에서 데이터 가져옴")


        for item in items:
            item['name'] = str(item['name'])
            item['affiliation'] = str(item['affiliation'])
            item['nickname'] = str(item['nickname'])
            item['coin_1'] = str(item['coin_1'])
            item['coin_2'] = str(item['coin_2'])
            item['coin_3'] = str(item['coin_3'])
            item['balance'] = int(item['balance'])
        
        sorted_items = sorted(items, key=lambda x: x['balance'], reverse=True)

        top_user = sorted_items[0]

        print("1등 유저 데이터 가져옴")

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json; charset=UTF-8"
            },
            "body": json.dumps({
                "message": "1등 유저 데이터 가져옴",
                "data": top_user
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


