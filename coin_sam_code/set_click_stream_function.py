import json
import boto3
import os

firehose_client = boto3.client('firehose', region_name=os.environ['AWS_REGION'])
DELIVERY_STREAM_NAME = os.environ['FIREHOSE_STREAM_NAME']

def set_click_stream_handler(event, context):
    try:
        body = json.loads(event['body'])

        # Firehose에 레코드 전송
        response = firehose_client.put_record(
            DeliveryStreamName=DELIVERY_STREAM_NAME,
            Record={
                'Data': json.dumps(body) + "\n"  # Firehose는 \n으로 레코드 구분하는 것이 일반적
            }
        )
        print(f"Data sent to Firehose, Response: {response}")

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Data sent to Firehose Successfully'})
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    
'''
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
'''