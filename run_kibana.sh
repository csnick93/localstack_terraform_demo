#!/bin/bash

docker run --name kibana --rm -p 5601:5601 -e SERVER_HOST=0.0.0.0 -e ELASTICSEARCH_HOSTS=http://host.docker.internal:4571 docker.elastic.co/kibana/kibana:7.7.0
