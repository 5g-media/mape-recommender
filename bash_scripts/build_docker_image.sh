#!/bin/bash

# download code from repo
$ mv mape-recommender/ svp-resource-recommendations/
$ find ./svp-resource-recommendations -type d -exec sudo chmod -R 755 {} \;
$ find ./svp-resource-recommendations -type f -exec sudo chmod 664 {} \;
$ chmod a+x ./svp-resource-recommendations/deployment/run.sh ./svp-resource-recommendations/deployment/clean.sh
$ cp ./svp-resource-recommendations/deployment/Dockerfile .
# build image
$ sudo docker build --no-cache -t svp-resource-recommendations .
$ source svp-resource-recommendations/deployment/clean.sh