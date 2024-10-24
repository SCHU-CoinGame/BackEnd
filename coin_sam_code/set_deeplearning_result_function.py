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

def set_deeplearning_result_handler(event, context):
    try:
        print("Lambda 함수 시작 - 딥러닝 결과 저장")
        print(f"Received event: {json.dumps(event)}")

        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']

        if not isinstance(body, list):
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Request body must be a list of items."})
            }

        for item in body:
            code = item.get('code')
            percentage = Decimal(str(item.get('percentage')))
            rank = item.get('rank')
            most_volatile = item.get('most_volatile')
            least_volatile = item.get('least_volatile')
            largest_drop = item.get('largest_drop')
            largest_rise = item.get('largest_rise')
            largest_spike = item.get('largest_spike')
            fastest_growth = item.get('fastest_growth')
            fastest_decline = item.get('fastest_decline')

            response = table.put_item(
                Item={
                    'code': code,
                    'percentage': percentage,
                    'rank': rank,
                    'most_volatile': most_volatile,
                    'least_volatile': least_volatile,
                    'largest_drop': largest_drop,
                    'largest_rise': largest_rise,
                    'fastest_growth': fastest_growth,
                    'largest_spike': largest_spike,
                    'fastest_decline': fastest_decline
                }
            )
            print(f"DynamoDB에 데이터 저장 성공: {response}")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Deep learning results saved successfully"})
        }

    except Exception as e:
        print(f"에러 발생: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "An error occurred", "error": str(e)})
        }