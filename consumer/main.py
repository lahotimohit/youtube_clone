import json
import boto3
from secret_keys import SecretKeys

secret_keys=SecretKeys()

sqs_client = boto3.client("sqs", region_name=secret_keys.REGION_NAME)
ecs_client = boto3.client("ecs", region_name=secret_keys.REGION_NAME)

def poll_sqs():
    while True:
        sqs_response = sqs_client.receive_message(QueueUrl=secret_keys.AWS_SQS_URL, MaxNumberOfMessages=1, WaitTimeSeconds=10)
        for message in sqs_response.get("Messages", []):
            message_body = json.loads(message.get("Body"))
            if (
                message_body.get("Service") and 
                message_body.get("Event") and 
                message_body.get("Event")=="s3:TestEvent"
                ):
                sqs_client.delete_message(
                    QueueUrl=secret_keys.AWS_SQS_URL,
                    ReceiptHandle=message["ReceiptHandle"])
                continue

            if "Records" in message_body:
                s3_record = message_body["Records"][0]["s3"]
                bucket_name = s3_record["bucket"]["name"]
                s3_key = s3_record["object"]["key"]
                
                #spin docker container

                response = ecs_client.run_task(
                    cluster="arn:aws:ecs:ap-south-1:158047605351:cluster/Lahoti-TranscoderCluster",
                    launchType="FARGATE",
                    taskDefinition="arn:aws:ecs:ap-south-1:158047605351:task-definition/videoTranscodingDefinition:1",
                    overrides={
                        "containerOverrides": [
                            {
                                "name": "video-transcoding",
                                "environment": [
                                    {"name": "S3_BUCKET", "value": bucket_name},
                                    {"name": "S3_KEY", "value": s3_key}
                                ]
                            }
                        ]
                    },
                    networkConfiguration={
                    'awsvpcConfiguration': {
                        'subnets': [
                            'subnet-08e4845e12656cd86',
                            'subnet-0b66af90f82adecce',
                            'subnet-04d600e8b6a51f65b'
                        ],
                        'securityGroups': [
                            'sg-08ada5f380e205fb5',
                        ],
                        'assignPublicIp': 'ENABLED'
                        }
                    },
                )
                print(response)
                sqs_client.delete_message(QueueUrl=secret_keys.AWS_SQS_URL, ReceiptHandle=message["ReceiptHandle"])

poll_sqs()