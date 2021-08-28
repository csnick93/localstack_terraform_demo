#!/bin/bash

docker run --rm -it \
    --network=my_network \
    --ip 172.28.0.3 \
    -p 4571:4571 \
    -p 4566:4566 \
    localstack/localstack
