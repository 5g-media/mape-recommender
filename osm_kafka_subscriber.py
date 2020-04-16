import time
import logging.config
import yaml
from nbiapi.identity import bearer_token
from nbiapi.vim_account import VimAccount
from nbiapi.vnf import Vnf
from nbiapi.vnfd import Vnfd
from nbiapi.operation import NsLcmOperation
from kafka import KafkaConsumer
from redminelib import Redmine
from utils import add_recommendation, get_redmine_issues_categories, email_notification
from settings import OSM_ADMIN_CREDENTIALS, OSM_KAFKA_NS_TOPIC, OSM_KAFKA_SERVER, OSM_COMPONENTS, \
    OSM_KAFKA_CLIENT_ID, OSM_KAFKA_API_VERSION, OSM_KAFKA_GROUP_ID, LOGGING, REDMINE

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('osm_subscriber')


def init_consumer():
    """ Init a Kafka consumer

    See more: https://kafka-python.readthedocs.io/en/master/apidoc/KafkaConsumer.html

    Returns:
        Iterator:  A KafkaConsumer Iterator
    """
    return KafkaConsumer(bootstrap_servers=OSM_KAFKA_SERVER, client_id=OSM_KAFKA_CLIENT_ID,
                         enable_auto_commit=True, api_version=OSM_KAFKA_API_VERSION,
                         group_id=OSM_KAFKA_GROUP_ID)


def main():
    """ Detect the failed scale out operations and check it is triggered from the limitation of the
    maximum allowed VNF instances.
    """
    kafka_consumer = init_consumer()
    kafka_consumer.subscribe(pattern=OSM_KAFKA_NS_TOPIC)

    # Run any incoming message in the intra-OSM kafka bus, topic `NS`
    for message in kafka_consumer:
        action = message.key.decode('utf-8', 'ignore')
        payload = yaml.safe_load(message.value.decode('utf-8', 'ignore'))

        if action != "scaled":
            continue

        event_state = payload.get('operationState', None)
        if event_state != "FAILED":
            continue

        ns_uuid = payload.get('nsr_id', None)
        operation_uuid = payload.get('nslcmop_id', None)
        if operation_uuid is None:
            continue

        logger.info("A new event for NS_UUID `{}` in state `{}` was detected.".format(
            action, ns_uuid, event_state))

        # Detect the event: SCALE_IN, SCALE_OUT or something else
        osm_token = bearer_token(OSM_ADMIN_CREDENTIALS['username'],
                                 OSM_ADMIN_CREDENTIALS['username'])
        ns_operation = NsLcmOperation(osm_token)
        request = ns_operation.get(operation_uuid=operation_uuid)
        response = request.json()
        event = response.get('operationParams', {}).get('scaleVnfData', {}).get(
            'scaleVnfType', None)

        # Skip it if not a scale out operation
        if not event or event != "SCALE_OUT":
            continue

        # Get the VNF index that was scaled
        vnf_index = response.get('operationParams', {}).get('scaleVnfData', {}).get(
            'scaleByStepData', {}).get('member-vnf-index', 0)
        if vnf_index == 0:
            continue

        # Get the list of involved VNFs in the NS
        vnf = Vnf(osm_token)
        vnfs_request = vnf.get_list_by_ns(ns_uuid=ns_uuid)
        vnfs_list = vnfs_request.json()

        # Detect the VNFr and VNFd that probably
        scaled_vnfr = None
        for vnfr in vnfs_list:
            if int(vnfr['member-vnf-index-ref']) == int(vnf_index):
                vnf_request = vnf.get(vnf_uuid=vnfr['_id'])
                scaled_vnfr = vnf_request.json()
                break

        if scaled_vnfr is None:
            continue

        # Get the Vim details that host this NS/VNF instances
        vim_acc = VimAccount(token=osm_token)
        vim_req = vim_acc.get(scaled_vnfr['vim-account-id'])
        vim_info = vim_req.json()

        # Get VNFD info
        vnfd = Vnfd(token=osm_token)
        vnfd_req = vnfd.get(scaled_vnfr['vnfd-id'])
        vnfd_info = vnfd_req.json()

        # Compose the recommendation message
        recommend_vnfd_scaling_group(vim_info, vnfd_info, scaled_vnfr)


def recommend_vnfd_scaling_group(vim, vnfd, vnfr):
    """ Compose the recommendation content and publish it in the Redmine

    Args:
        vim (dict): The VIM details
        vnfd (dict): The VNFD details
        vnfr (dict): The VNFr details

    """
    try:
        redmine = Redmine(REDMINE['BASE_URL'], username=REDMINE['USER'],
                          password=REDMINE['PASSWORD'])
        project = redmine.project.get(REDMINE['SCALING_PROJECT_NAME'])
        categories = get_redmine_issues_categories()
        category_id = categories[vim['vim_type']] if vim[
                                                         'vim_type'] in categories.keys() else 'other'

        scaling_group_descriptors = vnfd.get('scaling-group-descriptor', [])
        if not len(scaling_group_descriptors):
            return

        # get the scaling group details
        scaling_group_descriptor = scaling_group_descriptors[0]

        subject = 'Adjust the scaling group of the VNFd {}'.format(vnfd['name'])
        description = """
            A failed SCALE OUT operation was detected related to the VNF descriptor with identifier {} 
            and ref {}. It is recommended to increase the maximum allowed number of VNF 
            instances (through scale out operation).
    
            VNFd ref: {}\nVNFd identifier: {}\nVNFd vendor: {}\nVNFd version: {}\nVNFd index: {}\nVIM name: {}\nVIM type: {}\nOSM instance: {}
            
            The current maximum allowed number of VNF instances is: {}.
                    
            It is recommended to increase the maximum allowed number of VNF instances to: {}.
    
            """.format(vnfd['name'], vnfr['vnfd-ref'], vnfr['vnfd-ref'], vnfd['name'],
                       vnfd['vendor'], vnfd['version'], vnfr['member-vnf-index-ref'], vim['name'],
                       vim['vim_type'], OSM_COMPONENTS['UI'],
                       scaling_group_descriptor['max-instance-count'],
                       scaling_group_descriptor['max-instance-count'] + 1)

        # fixme: currently, the name of the project is static. We could use the VNFd vendor
        #  to group the recommendations per Vendor.
        add_recommendation(redmine, project, subject, description, category_id=2)

        # Notification through email
        vendor_email = 'test@localhost.eu'
        content = {'title': subject, 'description': description}
        email_notification(vendor_email, content)
    except Exception as ex:
        logger.exception(ex)


if __name__ == '__main__':
    main()
