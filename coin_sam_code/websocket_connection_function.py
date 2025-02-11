import boto3
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('websocket_connections')

def websocket_connection_handler(event, context):
    connection_id = event['requestContext']['connectionId']
    table.put_item(Item={'connectionId': connection_id})
    return {'statusCode': 200}
