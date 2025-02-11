import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr
from decimal import Decimal, getcontext, Inexact, Rounded

DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE)

context = getcontext()
context.traps[Inexact] = False
context.traps[Rounded] = False

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError

def get_deeplearning_result_handler(event, context): 
    try:
        print("Lambda 함수 시작 - 딥러닝 결과 호출")
        print(f"Received event: {json.dumps(event)}")

        coin_codes = ['KRW-BTC', 'KRW-ETH', 'KRW-DOGE', 'KRW-BIGTIME', 'KRW-SUI', 'KRW-UXLINK', 'KRW-SOL', 'KRW-XRP', 'KRW-SXP']

        results = []

        for coin_code in coin_codes:
            response = table.query(
                KeyConditionExpression=Key('code').eq(coin_code),
                ScanIndexForward=False,
                Limit=1
            )

            items = response.get('Items', [])
            if items:
                results.append(items[0])


        if not results:
            return {
                "statusCode": 404,
                "body": json.dumps({"message": "No data found"})
            }

        return {
            "statusCode": 200,
            "body": json.dumps(results, default=decimal_default) 
        }
    except Exception as e:
        print(f"에러 발생: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "An error occurred", "error": str(e)})
        }