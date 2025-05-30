#!/bin/bash

if [ $# -eq 0 ]; then
    docker-compose logs -f
else
    docker-compose logs -f $1
fi
