#!/bin/bash

docker network inspect my_network >/dev/null 2>&1 || \
      docker network create --subnet=172.28.0.0/16 my_network
