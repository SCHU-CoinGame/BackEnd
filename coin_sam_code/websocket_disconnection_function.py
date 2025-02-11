import boto3
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('websocket_connections')

def websocket_disconnection_handler(event, context):
    connection_id = event['requestContext']['connectionId']
    table.delete_item(Key={'connectionId': connection_id})
    return {'statusCode': 200}
