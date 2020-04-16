#!/bin/bash

sed -i "s/ENV_DEBUG/$DEBUG/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_GRAYLOG_HOST/$GRAYLOG_HOST/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_GRAYLOG_PORT/$GRAYLOG_PORT/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_GRAYLOG_LOGGING/$GRAYLOG_LOGGING/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_SCHEDULER_MINUTES/$SCHEDULER_MINUTES/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_REDMINE_BASE_URL/$REDMINE_BASE_URL/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_REDMINE_USER/$REDMINE_USER/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_REDMINE_PASSWORD/$REDMINE_PASSWORD/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_INFLUXDB_DB_NAME/$INFLUXDB_DB_NAME/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_INFLUXDB_USER/$INFLUXDB_USER/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_INFLUXDB_PWD/$INFLUXDB_PWD/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_INFLUXDB_IP/$INFLUXDB_IP/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_INFLUXDB_PORT/$INFLUXDB_PORT/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_OSM_IP/$OSM_IP/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_OSM_USER/$OSM_USER/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_OSM_PWD/$OSM_PWD/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_OSM_KAFKA_PORT/$OSM_KAFKA_PORT/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_POLICY_VM_CPU_UPPER_THRESHOLD/$POLICY_VM_CPU_UPPER_THRESHOLD/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_POLICY_VM_CPU_LOWER_THRESHOLD/$POLICY_VM_CPU_LOWER_THRESHOLD/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_POLICY_VM_MEMORY_UPPER_THRESHOLD/$POLICY_VM_MEMORY_UPPER_THRESHOLD/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_POLICY_VM_MEMORY_LOWER_THRESHOLD/$POLICY_VM_MEMORY_LOWER_THRESHOLD/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_POLICY_VM_DISK_UPPER_THRESHOLD/$POLICY_VM_DISK_UPPER_THRESHOLD/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_POLICY_VM_DISK_LOWER_THRESHOLD/$POLICY_VM_DISK_LOWER_THRESHOLD/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_POLICY_CONTAINER_MEMORY_UPPER_THRESHOLD/$POLICY_CONTAINER_MEMORY_UPPER_THRESHOLD/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_POLICY_CONTAINER_MEMORY_LOWER_THRESHOLD/$POLICY_CONTAINER_MEMORY_LOWER_THRESHOLD/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_EMAIL_NOTIFICATION_ENABLED/$EMAIL_NOTIFICATION_ENABLED/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_NOTIFICATION_EMAIL_HOST/$NOTIFICATION_EMAIL_HOST/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_NOTIFICATION_EMAIL_HOST_USER/$NOTIFICATION_EMAIL_HOST_USER/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_NOTIFICATION_EMAIL_HOST_PASSWORD/$NOTIFICATION_EMAIL_HOST_PASSWORD/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_NOTIFICATION_EMAIL_PORT/$NOTIFICATION_EMAIL_PORT/g" /etc/supervisor/supervisord.conf

# Restart services
service supervisor start && service supervisor status

# Makes services start on system start
update-rc.d supervisor defaults

echo "Initialization completed."
tail -f /dev/null  # Necessary in order for the container to not stop
