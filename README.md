# Terraform + Localstack Demo

This repo is a demonstration of how to use terraform in combination with localstack to define and launch aws based pipelines locally.

## Desired Setup

* Architecture:
    * `S3 Bucket -> SQS Queue  -> ElasticSearch -> Kibana`
* Workflow
    * Write message that is dumped as text file to the s3 bucket
    * SQS queue is notified on file additions on the s3 bucket
    * File content is read in by separate worker and written to an ElasticSearch cluster
    * Kibana is used to visualize the ElasticSearch cluster's content

## Prerequesites
* Docker
* Terraform
* Python3
    * Installation of `requirements.txt`

## Steps to launch and execute the infrastructure
* Create docker network: `./create_network.sh`
    * This is required to ensure that ElasticSearch and Kibana services can communicate
* Start Localstack service: `./start_localstack.sh`
* Launch infrastructure:
    * Navigate to `infrastructure/local`
    * Setup infrastructure locally using:
        * `terraform init`
        * `terraform apply -auto-approve`
    * Wait for ElasticSearch plugins to be installed in localstack
* Source some environment variables required: `source code/.env.local`
* Launch the elasticsearch writer: `python code/elasticsearch_dumper.py`
    * There is an infinite loop of waiting for message from the sqs queue and writing it to the elasticsearch cluster
* Upload message files to the s3 bucket using: `python code/s3_uploader.py <message>`
* Check results in Kibana at `localhost:5601`
    * Index written to is `random`
