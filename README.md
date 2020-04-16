# MAPE recommender component

This component is part of the 5G-MEDIA MAPE service. Take a look in the [mape](https://github.com/5g-media/mape) repository.

## Introduction
The `mape-recommender` component:
 - analyzes the resource consumption per VDU in a OSM instance based on the historical data and recommend updates in existing flavors (scale up or scale out),
 - analyzes the failed scaled out operation of a VNF and recommends (if needed) updates in the VNFd scaling policy/maximum allowed VNF instances

In both cases, the SDK developer/owner of the VNF can be informed directly (via email) or through the Issue tracking tool (part of SVP).

This component must be deployed in any NFVI that any OSM instance is running.

## Requirements
- Python 3.5+ 
  + a set of python packages are used (see `requirements.txt`).
- The OSM NBI APIs must be accessible from the component.
- The intra-OSM Kafka broker must be accessible from the component
- The InfluxDB must be accessible from the component.
- The Redmine must be accessible from the component.
- The Graylog must be accessible from the component.

## Configuration
Check the `settings.py` file:
- *DEBUG*: 1 for debug mode. Otherwise, 0.
- *KAFKA_SERVER*: The host and port of the 5G-MEDIA kafka.
- *KAFKA_CLIENT_ID*: The id of this kafka client.
- *OSM_IP*: The IPv4 of the OSM instance.
- *OSM_ADMIN_CREDENTIALS*: The admin credentials of the OSM instance.
- *OSM_COMPONENTS*: The URL of each OSM component
- *OSM_KAFKA_SERVER*: The host and port of the OSM kafka.
- *OSM_KAFKA_NS_TOPIC*: The name of the OSM kafka topic in which the NS events are arrived.
- *VDNS_IP*: The IPv4 in the MGMT network of the vDNS.
- *INFLUX_DATABASES*: The InfluxDB settings.
- *GRAYLOG_HOST*: The host/IPv4 of the Graylog server.
- *GRAYLOG_PORT*: The port of the Graylog server.
- ...


## Installation/Deployment

To build the docker image, copy the bash script included in the `bash_scripts/` folder in the parent folder of the project and then, run:
```bash
   chmod +x build_docker_image.sh
   ./build_docker_image.sh
```

The deployment can be done  using either the docker engine by passing the proper env variables or docker-compose in the [MAPE](https://github.com/5g-media/mape) repository.

`TODO`: describe the deployemnt using docker engine


## Usage

Access the docker container:
```bash
$ sudo docker exec -it  mape-resource-recommendation bash
```

Two services are running in this docker container under the supervisor:
- flavor_recommender
- osm_kafka_subscriber

Start the services through the supervisor:
```bash
$ service supervisor start && supervisorctl start {service_name}
```

Stop the execution service through the supervisor:
```bash
$ supervisorctl stop {service_name}
```

Stop the supervisor service:
```bash
$ service supervisor stop 
```

You are able to check the status of the services using your browser from the supervisor UI.
Type the URL: `http://{mape_ipv4}:{container_port}`

## Screenshots

![VDU flavor recommendation](/screenshots/flavor_recommendations.JPG)

![Scaling policy recommendation](/screenshots/scaling_recommendation.JPG)


## Authors
- Singular Logic <pathanasoulis@ep.singularlogic.eu>


## Contributors
 - Contact with Authors

 
## Acknowledgements
This project has received funding from the European Union’s Horizon 2020 research and innovation 
programme under grant agreement *No 761699*. The dissemination of results herein reflects only 
the author’s view and the European Commission is not responsible for any use that may be made 
of the information it contains.


## License
[Apache 2.0](LICENSE.md)


