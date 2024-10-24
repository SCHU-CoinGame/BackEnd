import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr
from decimal import Decimal, getcontext, Inexact, Rounded

DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE)

def set_user_handler(event, context):
    try:
        print("Lambda 함수 시작 - 이벤트 받음")
        print(f"Received event: {json.dumps(event)}")

        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        print(f"Parsed body: {body}")

        name = body.get('name')
        if not name:
            raise ValueError("Missing partition key 'name'")
        print(f"Extracted 'name' (Partition Key): {name}")

        balance = body.get('balance')
        if balance is None:
            raise ValueError("Missing sort key 'balance'")
        print(f"Extracted 'balance' (before conversion): {balance}")
        
        try:
            balance_decimal = Decimal(str(balance))
            print(f"Converted 'balance' to Decimal: {balance_decimal}")
        except InvalidOperation as e:
            raise ValueError(f"Invalid 'balance' value: {balance}, error: {e}")
        
        student_id = body.get('student_id')
        department = body.get('department')
        nickname = body.get('nickname')
        coin_1 = body.get('coin_1')
        coin_2 = body.get('coin_2')
        coin_3 = body.get('coin_3')

        print(f"Extracted data - student_id: {student_id}, department: {department}, nickname: {nickname}, "
              f"coin_1: {coin_1}, coin_2: {coin_2}, coin_3: {coin_3}")

        response = table.put_item(
            Item={
                'name': name, 
                'balance': balance_decimal,
                'student_id': student_id,
                'department': department,
                'nickname': nickname,
                'coin_1': coin_1,
                'coin_2': coin_2,
                'coin_3': coin_3
            }
        )
        print(f"DynamoDB에 데이터 저장 성공: {response}")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Data saved successfully"})
        }

    except ValueError as ve:
        print(f"Validation Error 발생: {ve}")
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Validation Error", "error": str(ve)})
        }

    except Exception as e:
        print(f"에러 발생: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "An error occurred", "error": str(e)})
        }