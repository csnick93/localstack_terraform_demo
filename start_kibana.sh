#!/bin/bash

docker run \
    --name kibana \
    --network=my_network \
    --ip 172.28.0.6 \
    --rm \
    -e SERVER_HOST=172.28.0.6 \
    -e ELASTICSEARCH_HOSTS=http://172.28.0.3:4571 \
    -p 5601:5601 \
    docker.elastic.co/kibana/kibana:7.7.0
