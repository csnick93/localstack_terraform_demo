from typing import Tuple
import click
import os
import pathlib
import tempfile
import urllib3

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


def _get_s3_client():
    if os.environ.get('LOCAL_DEVELOPMENT', None) == '1':
        session = boto3.Session(localstack_host='localhost',
                                **_aws_credentials())
    else:
        session = boto3.Session(**_aws_credentials())
    client = session.client('s3')
    return client


def _decompose_s3_uri(uri: str) -> Tuple[str, str]:
    url = urllib3.util.parse_url(uri)
    bucket = url.host
    prefix = url.path[1:]
    return bucket, prefix


def upload_file(local_uri: str, s3_uri: str) -> None:
    client = _get_s3_client()
    bucket, key = _decompose_s3_uri(s3_uri)
    client.upload_file(local_uri, bucket, key)


@click.command()
@click.argument('message', type=str)
def process_message(message: str):
    bucket_uri = os.environ.get('S3_BUCKET')
    with tempfile.NamedTemporaryFile() as f:
        p = pathlib.Path(f.name)
        p.write_text(message)
        upload_file(f.name, os.path.join(bucket_uri, p.name))


if __name__ == '__main__':
    process_message()
