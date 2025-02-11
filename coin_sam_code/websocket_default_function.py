import boto3
import json
import time
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('dynamoDB_upbit_table')
connections_table = dynamodb.Table('websocket_connections')

api_gateway = boto3.client('apigatewaymanagementapi',
    endpoint_url='https://92otppblpb.execute-api.ap-northeast-2.amazonaws.com/production')

coin_codes = ['KRW-BTC', 'KRW-ETH', 'KRW-DOGE', 'KRW-BIGTIME', 'KRW-SUI',
              'KRW-UXLINK', 'KRW-SOL', 'KRW-XRP', 'KRW-SXP']

INTERVAL = 0.5  # 데이터 전송 주기 (초 단위)

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def get_latest_data():
    results = []
    for coin_code in coin_codes:
        response = table.query(
            KeyConditionExpression=Key('code').eq(coin_code),
            ScanIndexForward=False,
            Limit=1
        )
        items = response.get('Items', [])
        results.extend(items)
    return results

def broadcast_to_clients(data):
    response = connections_table.scan()
    connections = response.get('Items', [])
    for connection in connections:
        try:
            api_gateway.post_to_connection(
                ConnectionId=connection['connectionId'],
                Data=json.dumps(data, default=decimal_default)
            )
        except api_gateway.exceptions.GoneException:
            connections_table.delete_item(Key={'connectionId': connection['connectionId']})

def websocket_default_handler(event, context):
    try:
        connection_id = event['requestContext']['connectionId']
        message = json.loads(event['body'])

        if message.get('type') == 'ping':
            # Ping 처리: Pong 응답
            api_gateway.post_to_connection(
                ConnectionId=connection_id,
                Data=json.dumps({"type": "pong"})
            )
        elif message.get('action') == 'getData':
            # getData 요청 처리: 최신 데이터 전송
            latest_data = get_latest_data()
            api_gateway.post_to_connection(
                ConnectionId=connection_id,
                Data=json.dumps(latest_data, default=decimal_default)
            )
        else:
            # 알 수 없는 요청 처리
            api_gateway.post_to_connection(
                ConnectionId=connection_id,
                Data=json.dumps({"message": "Invalid action"})
            )

        return {'statusCode': 200}

    except Exception as e:
        print(f"Error: {e}")
        return {'statusCode': 500, 'body': json.dumps({'message': 'Error', 'error': str(e)})}
