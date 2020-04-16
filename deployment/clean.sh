#!/bin/bash

if sudo docker ps | grep -q 'mape-resource-recommendation'; then
    # Gracefully stop supervisor
    sudo docker exec -i mape-resource-recommendation service supervisor stop && \
    sudo docker stop mape-resource-recommendation && \
    sudo docker rm -f mape-resource-recommendation
fi
