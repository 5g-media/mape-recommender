import os

DEBUG = int(os.environ.get("DEBUG", 1))
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
GRAYLOG_LOGGING = int(os.environ.get("GRAYLOG_LOGGING", 0))

# =================================
# SCHEDULER SETTINGS
# =================================
SCHEDULER_MINUTES = os.environ.get("SCHEDULER_MINUTES", 30)  # minutes

# =================================
# REDMINE SETTINGS
# =================================
REDMINE = {
    'BASE_URL': "http://{}/".format(os.environ.get('REDMINE_BASE_URL', '192.168.1.175')),
    'USER': os.environ.get('REDMINE_USER', 'svp'),
    'PASSWORD': os.environ.get('REDMINE_PASSWORD', 'password'),
    'PROJECT_NAME': os.environ.get("REDMINE_PROJECT_NAME", 'resource-recommendations'),
    'SCALING_PROJECT_NAME': 'scaling-groups-capacity'
}

# =================================
# INFLUXDB SETTINGS
# =================================
# See InfluxDBClient class
INFLUX_DATABASES = {
    'default': {
        'ENGINE': 'influxdb',
        'NAME': os.environ.get("INFLUXDB_DB_NAME", 'monitoring'),
        'USERNAME': os.environ.get("INFLUXDB_USER", 'root'),
        'PASSWORD': os.environ.get("INFLUXDB_PWD", 'password'),
        'HOST': os.environ.get("INFLUXDB_IP", "192.168.1.175"),
        'PORT': os.environ.get("INFLUXDB_PORT", 8086)
    }
}

# =================================
# OSM SETTINGS
# =================================
OSM_IP = os.environ.get("OSM_IP", "192.168.1.175")
OSM_ADMIN_CREDENTIALS = {"username": os.environ.get("OSM_USER", "admin"),
                         "password": os.environ.get("OSM_PWD", "password")}
OSM_COMPONENTS = {"UI": 'http://{}:80'.format(OSM_IP),
                  "NBI-API": 'https://{}:9999'.format(OSM_IP),
                  "RO-API": 'http://{}:9090'.format(OSM_IP)}
OSM_KAFKA_SERVER = "{}:{}".format(OSM_IP, os.environ.get("OSM_KAFKA_PORT", "9094"))
OSM_KAFKA_NS_TOPIC = 'ns'
OSM_KAFKA_API_VERSION = (1, 1, 0)
OSM_KAFKA_CLIENT_ID = 'recommendation-service'
OSM_KAFKA_GROUP_ID = '5GMEDIA_RECOMMENDATION_CG'

# =================================
# GRAYLOG SETTINGS
# =================================
GRAYLOG_HOST = os.environ.get("GRAYLOG_HOST", '192.168.1.175')
GRAYLOG_PORT = int(os.environ.get("GRAYLOG_PORT", 12201))

# =================================
# RESOURCE POLICIES
# =================================
POLICIES = {
    'VM_CPU_UPPER_THRESHOLD': float(os.environ.get('POLICY_VM_CPU_UPPER_THRESHOLD', 60)),
    'VM_CPU_LOWER_THRESHOLD': float(os.environ.get('POLICY_VM_CPU_LOWER_THRESHOLD', 20)),
    'VM_MEMORY_UPPER_THRESHOLD': float(os.environ.get('POLICY_VM_MEMORY_UPPER_THRESHOLD', 80)),
    'VM_MEMORY_LOWER_THRESHOLD': float(os.environ.get('POLICY_VM_MEMORY_LOWER_THRESHOLD', 20)),
    'VM_DISK_UPPER_THRESHOLD': float(os.environ.get('POLICY_VM_DISK_UPPER_THRESHOLD', 80)),
    'VM_DISK_LOWER_THRESHOLD': float(os.environ.get('POLICY_VM_DISK_LOWER_THRESHOLD', 20)),
    'CONTAINER_MEMORY_UPPER_THRESHOLD': float(
        os.environ.get('POLICY_CONTAINER_MEMORY_UPPER_THRESHOLD', 80)),
    'CONTAINER_MEMORY_LOWER_THRESHOLD': float(
        os.environ.get('POLICY_CONTAINER_MEMORY_LOWER_THRESHOLD', 20))
}

# =================================
# NOTIFICATION ACCOUNT - EMAIL
# =================================
EMAIL_NOTIFICATION_ENABLED = int(os.environ.get('EMAIL_NOTIFICATION_ENABLED', 0))
EMAIL_HOST = os.environ.get('NOTIFICATION_EMAIL_HOST', 'smtp.gmail.com')
EMAIL_HOST_USER = os.environ.get('NOTIFICATION_EMAIL_HOST_USER', 'test@localhost.com')
EMAIL_HOST_PASSWORD = os.environ.get('NOTIFICATION_EMAIL_HOST_PASSWORD', 'password')
EMAIL_PORT = int(os.environ.get('NOTIFICATION_EMAIL_PORT', 587))

# ==================================
# LOGGING SETTINGS
# ==================================
# See more: https://docs.python.org/3.5/library/logging.config.html
DEFAULT_HANDLER_SETTINGS = {
    'class': 'logging.handlers.RotatingFileHandler',
    'filename': "{}/logs/worker.log".format(PROJECT_ROOT),
    'mode': 'w',
    'formatter': 'detailed',
    'level': 'DEBUG' if DEBUG else 'WARNING',
    'maxBytes': 4096 * 4096,
    'backupCount': 8,
}
if GRAYLOG_LOGGING:
    DEFAULT_HANDLER_SETTINGS = {
        'class': 'graypy.GELFUDPHandler',
        'formatter': 'detailed',
        'level': 'DEBUG' if DEBUG else 'WARNING',
        'host': GRAYLOG_HOST,
        'port': GRAYLOG_PORT
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'detailed': {
            'class': 'logging.Formatter',
            'format': "[%(asctime)s] - [%(name)s:%(lineno)s] - [%(levelname)s] %(message)s",
        },
        'simple': {
            'class': 'logging.Formatter',
            'format': '%(name)-15s %(levelname)-8s %(processName)-10s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'detailed',
        },
        'worker': DEFAULT_HANDLER_SETTINGS,
        'osm_subscriber': DEFAULT_HANDLER_SETTINGS,
        'notifier': DEFAULT_HANDLER_SETTINGS
    },
    'loggers': {
        'worker': {
            'handlers': ['worker']
        },
        'osm_subscriber': {
            'handlers': ['osm_subscriber']
        },
        'notifier': {
            'handlers': ['notifier']
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': [
            'worker',
            'osm_subscriber',
            'notifier',
            # 'console',
        ]
    }
}
