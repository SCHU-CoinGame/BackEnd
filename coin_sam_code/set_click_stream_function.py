import json
import boto3
import os

kinesis_client =  boto3.client('kinesis', region_name = os.environ['AWS_REGION'])

KINESIS_STREAM_NAME = os.environ['KINESIS_STREAM_NAME']

def set_click_stream_handler(event, context):
    try:
        body = json.loads(event['body'])

        response = kinesis_client.put_record(
            StreamName = KINESIS_STREAM_NAME,
            Data = json.dumps(body),
            PartitionKey="single-shard"
        )
        print(f"Data send to Kinesis, Response: {response}")

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Data sent Successfully'})
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }