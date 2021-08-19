from requests.auth import HTTPBasicAuth
from typing import Dict, Tuple
import json
import os
import pathlib
import requests
import tempfile
import time

if os.environ.get('LOCAL_DEVELOPMENT', None) == '1':
    import localstack_client.session as boto3
else:
    import boto3  # type: ignore


def _aws_credentials():
    if os.environ.get('AWS_ACCESS_KEY', None) is None:
        raise RuntimeError('Missing aws access key')
    if os.environ.get('AWS_SECRET_KEY', None) is None:
        raise RuntimeError('Missing aws secret key')

    return {
        'aws_access_key_id': os.environ['AWS_ACCESS_KEY'],
        'aws_secret_access_key': os.environ['AWS_SECRET_KEY'],
        'region_name': 'eu-central-1'
    }


def _get_client(service: str):
    if os.environ.get('LOCAL_DEVELOPMENT', None) == '1':
        session = boto3.Session(localstack_host='localhost',
                                **_aws_credentials())
    else:
        session = boto3.Session(**_aws_credentials())
    client = session.client(service)
    return client


def _receive_messages(queue_url: str,
                      max_num_messages: int,
                      wait_time_seconds: int = 0) -> Dict:
    client = _get_client('sqs')
    response = client.receive_message(QueueUrl=queue_url,
                                      AttributeNames=['SentTimestamp'],
                                      MaxNumberOfMessages=max_num_messages,
                                      MessageAttributeNames=['All'],
                                      WaitTimeSeconds=wait_time_seconds)
    return response


def _get_s3_content(bucket: str, key: str) -> str:
    client = _get_client('s3')
    with tempfile.NamedTemporaryFile() as f:
        client.download_file(bucket, key, f.name)
        content = pathlib.Path(f.name).read_text()
    return content


def _delete_message(queue_url: str, receipt_handle: str) -> None:
    client = _get_client('sqs')
    client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)


def _es_credentials() -> Tuple[str, str]:
    es_user = os.environ.get('ES_USER', None)
    es_password = os.environ.get('ES_PASSWORD', None)
    if es_user is None or es_password is None:
        raise RuntimeError('Missing ES credentials')
    return (es_user, es_password)


def _init_elastic_search_index(index: str, mapping: Dict) -> None:
    es_url = os.environ.get('ES_URL', None)
    url = f'{es_url}/{index}'
    response = requests.get(url, auth=HTTPBasicAuth(*_es_credentials()))
    if response.status_code == 200:
        # index already exists
        return

    response = requests.put(url,
                            auth=HTTPBasicAuth(*_es_credentials()),
                            data=json.dumps(mapping),
                            headers={'content-type': 'application/json'})

    if response.status_code != 200:
        raise RuntimeError(f'Failed to create index for {index}')


def _init_elastic_search() -> None:
    mapping = {
        'settings': {
            'number_of_shards': 1
        },
        'mappings': {
            'properties': {
                'content': {
                    'type': 'text'
                },
            }
        }
    }
    _init_elastic_search_index(index='random', mapping=mapping)


def process_messages():
    queue_url = os.environ.get('SQS_QUEUE')
    message_data = _receive_messages(queue_url, max_num_messages=10)
    messages = message_data.get('Messages', [])
    for message in messages:
        print('Processing message')
        msg_body = json.loads(message['Body'])
        s3_info = msg_body['Records'][0]['s3']
        bucket_name = s3_info['bucket']['name']
        key = s3_info['object']['key']
        content = _get_s3_content(bucket_name, key)

        url = f'{os.environ.get("ES_URL")}/random/_doc/'
        _ = requests.post(url,
                          data=json.dumps({'content': content}),
                          auth=HTTPBasicAuth(*_es_credentials()),
                          headers={'content-type': 'application/json'})

        _delete_message(queue_url, message['ReceiptHandle'])


if __name__ == '__main__':
    _init_elastic_search()
    while True:
        process_messages()
        time.sleep(1)
