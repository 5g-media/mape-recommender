import time
import logging.config
from influxdb import InfluxDBClient
import schedule
from influxdbapi.openstack_queries import OpenStackQueries
from redminelib import Redmine
from nbiapi.identity import bearer_token
from nbiapi.vim_account import VimAccount
from nbiapi.vnfd import Vnfd
from utils import add_recommendation, email_notification
from settings import LOGGING, SCHEDULER_MINUTES, INFLUX_DATABASES, REDMINE, POLICIES, \
    OSM_ADMIN_CREDENTIALS, OSM_COMPONENTS

logging.config.dictConfig(LOGGING)
logger = logging.getLogger("worker")


def main():
    # Get the auth token in OSM
    osm_token = bearer_token(OSM_ADMIN_CREDENTIALS['username'], OSM_ADMIN_CREDENTIALS['password'])
    # Discover the openstack VIMs
    vim_acc = VimAccount(token=osm_token)
    vims_req = vim_acc.get_list()
    vims = vims_req.json()

    vdus_consumption = get_resources_consumption(vims)
    recommend_flavor(osm_token, vdus_consumption)


def get_resources_consumption(vim_accounts):
    """ Retrieve the resources consumption of VDUs hosted in registered NFVIs from the InfluxDB API

    Args:
        vim_accounts (list): the registered VIM account in the local OSM

    Returns:
        list: the resources consumption as a list of VDUs

    Response example:
        [
            {
                "mean_memory_util": 3.4,
                "vnfd_uuid":"23f76771-3a39-42ae-a09c-2f79f459a90a",
                "vim_uuid": "23f76771-3a39-42ae-a09c-2f79f459a9as",
                "vdu_uuid": "99f76771-3a39-42ae-a09c-2f79f459a910",
                "vim_type": "openstack",
                "vim_name": "Openstack_ENG",
                "mean_disk_util": 7.8,
                "mean_cpu_util": 35.6
            }
        ]
    """
    vdus = []

    # Init the influxDB client
    client = InfluxDBClient(
        host=INFLUX_DATABASES['default']['HOST'], port=INFLUX_DATABASES['default']['PORT'],
        username=INFLUX_DATABASES['default']['USERNAME'],
        password=INFLUX_DATABASES['default']['PASSWORD'],
        database=INFLUX_DATABASES['default']['NAME'])

    # Discover the VDUs per VIM
    for vim_account in vim_accounts:
        vim_name = vim_account['name']
        vim_type = vim_account['vim_type']
        openstack = OpenStackQueries(client, vim_name, int(SCHEDULER_MINUTES))
        openstack_vdus = openstack.get_vdu_list()

        # Fetch the resources consumption per VDU
        for vdu in openstack_vdus:
            instance = {'vim_type': vim_type, 'vim_name': vim_name, 'vdu_uuid': vdu}
            instance['vnfd_uuid'] = openstack.get_vnfd_uuid(vdu)
            instance['mean_cpu_util'] = openstack.mean_cpu_util(vdu)
            instance['mean_memory_util'] = openstack.mean_memory_util(vdu)
            instance['mean_disk_util'] = openstack.mean_disk_usage(vdu)
            # mean_disk_allocation = openstack.mean_disk_allocation(vdu)
            # instance['mean_disk_util'] = openstack.mean_disk_util(mean_disk_usage,
            #                                                       mean_disk_allocation)
            vdus.append(instance)

    logger.info('get_resources_consumption(): {}'.format(vdus))
    return vdus


def recommend_flavor(osm_token, consumption_records):
    """ Recommend an adjustment in the flavor of a VDU, part of a running VNF

    Analyze the resource consumption of each VDU and make a recommendation wrt the VDUs' flavor.
    This recommendation will describe a `scale up` or `scale down` operation.

    Input example:
        [
            {
                "mean_memory_util": 3.4,
                "vnfd_uuid":"23f76771-3a39-42ae-a09c-2f79f459a90a",
                "vim_uuid": "23f76771-3a39-42ae-a09c-2f79f459a9as",
                "vdu_uuid": "99f76771-3a39-42ae-a09c-2f79f459a910",
                "vim_type": "openstack",
                "vim_name": "Openstack_ENG",
                "mean_disk_util": 7.8,
                "mean_cpu_util": 35.6
            }
        ]

    Args:
        consumption_records (list): The mean resource consumption for a set of VDUs

    """
    redmine = Redmine(REDMINE['BASE_URL'], username=REDMINE['USER'], password=REDMINE['PASSWORD'])
    project = redmine.project.get(REDMINE['PROJECT_NAME'])

    for record in consumption_records:
        logger.warning(record)
        proposed_flavor_changes = analyze_consumption(record)
        info, flavor = get_vdu_info(osm_token, record['vnfd_uuid'], record['vdu_uuid'])
        action, new_flavor_details = compare_flavor(flavor, proposed_flavor_changes)

        if action:
            try:
                subject = 'Support new flavor for the VDU with name {}'.format(info['vdu_name'])

                if record['mean_disk_util'] and flavor['disk']:
                    record['mean_disk_util'] = (record['mean_disk_util']) * 100 / (
                            flavor['disk'] * pow(10, 9))
                    if record['mean_disk_util'] > 100:
                        record['mean_disk_util'] = 100

                description = """
                After the resources consumption analysis based on the  historical data for the VDU with
                name {} that is part of the VNF descriptor with identifier {} and ref {}, the 
                generation and usage of a new VDU flavor is recommended.
                
                Mean CPU utilization: {}/100\nMean RAM utilization: {}/100\nMean disk utilization: {}/100\nTime window: Last {} minutes\n\n
                VNFd ref: {}\nVNFd identifier: {}\nVNFd vendor: {}\nVNFd version: {}\nVDU name: {}\nVIM name: {}\nVIM type: {}\nOSM instance: {}\n\n
                The current VDU flavor has the following characteristics:\n- vCPU: {}\n- MEMORY: {} MB\n- DISK: {} GB
                
                It is recommended the generation of the following flavor:\n{}    
                
                """.format(info['vdu_name'], info['vnfd_name'], record['vnfd_uuid'],
                           round(record['mean_cpu_util'], 2) if record['mean_cpu_util'] else '-',
                           round(record['mean_memory_util'], 2) if record[
                               'mean_memory_util'] else '-',
                           round(record['mean_disk_util'], 2) if record['mean_disk_util'] else '-',
                           SCHEDULER_MINUTES, record['vnfd_uuid'], info['vnfd_name'],
                           info['vendor'], info['version'], info['vdu_name'], record['vim_name'],
                           record['vim_type'], OSM_COMPONENTS['UI'], flavor['cpu'],
                           flavor['memory'] * 1024.0, flavor['disk'], new_flavor_details)

                # fixme: currently, the name of the project is static. We could use the VNFd vendor
                #  to group the recommendations per Vendor.
                add_recommendation(redmine, project, subject, description, category_id=2)

                # Notification through email
                content = {'title': subject, 'description': description}
                email_notification('test@localhost.eu', content)
            except Exception as ex:
                logger.exception(ex)


def analyze_consumption(consumption):
    """ Apply the recommendation policy by given the resources consumption per VDU

    Args:
        consumption (dict): The resource consumption (mean value) of a VDU across the time

    Returns:
        dict: the recommended adjusted on the VDU flavor
    """
    analysis = {}
    vim_type = consumption.get('vim_type', 'other')
    analysis = {'cpu': 0, 'memory': 0, 'disk': 0}

    if vim_type == 'openstack':
        if consumption['mean_cpu_util'] is not None:
            if consumption['mean_cpu_util'] > POLICIES['VM_CPU_UPPER_THRESHOLD']:
                analysis['cpu'] = 1  # vCPU
            elif consumption['mean_cpu_util'] < POLICIES['VM_CPU_LOWER_THRESHOLD']:
                analysis['cpu'] = -1  # vCPU

        if consumption['mean_memory_util'] is not None:
            if consumption['mean_memory_util'] > POLICIES['VM_MEMORY_UPPER_THRESHOLD']:
                analysis['memory'] = 1  # GB
            elif consumption['mean_memory_util'] < POLICIES['VM_MEMORY_LOWER_THRESHOLD']:
                analysis['memory'] = -1  # GB

        if consumption['mean_disk_util'] is not None:
            if consumption['mean_disk_util'] > POLICIES['VM_DISK_UPPER_THRESHOLD']:
                analysis['disk'] = 10  # GB
            elif consumption['mean_disk_util'] < POLICIES['VM_DISK_LOWER_THRESHOLD']:
                # outcome['disk'] = '-10 GB'
                pass
    elif vim_type == 'kubernetes':
        logger.warning("Vim type {} is not supported".format(vim_type))
    elif vim_type == 'opennebula':
        logger.warning("Vim type {} is not supported".format(vim_type))
    else:
        logger.warning("Vim type {} is not supported".format(vim_type))

    return analysis


def get_vdu_info(osm_token, vnfd_uuid, vdu_uuid):
    """ Retrieve the VDU details hosted in OpenStack NFVI from the local OSM

    Args:
        osm_token (str): the auth token for teh OSM NBI API
        vnfd_uuid (str): The identifier of the VNF descriptor
        vdu_uuid (str): The identifier of the VDU instance, part of the deployed VNF

    Returns:
        tuple: details for the VDU and its flavor
    """
    vnfd = Vnfd(osm_token)
    response = vnfd.get(vnfd_uuid=vnfd_uuid)
    data = response.json()
    vdus = data.get('vdu', [])

    flavor = {'memory': None, 'cpu': None, 'disk': None}
    info = {'vnfd_name': None, 'vnfd_id': None, 'vdu_name': None, 'vendor': None, 'version': None}
    if not len(vdus):
        return info, flavor

    vdu = vdus[0]
    flavor = vdu['vm-flavor']
    flavor = {'memory': int(flavor['memory-mb']) / 1024, 'cpu': int(flavor['vcpu-count']),
              'disk': int(flavor['storage-gb'])}
    info = {'vnfd_name': data['name'], 'vnfd_id': data['id'], 'vdu_name': vdu['name'],
            'vendor': data['vendor'], 'version': data.get('version', 'N/A')}

    logger.debug('get_vdu_info(): info={} | flavor={}'.format(info, flavor))
    return info, flavor


def compare_flavor(flavor, suggested_changes):
    """ Evaluate the flavor changes given the current VDU flavor.

    Args:
        flavor (dict): the auth token for teh OSM NBI API
        suggested_changes (dict): The identifier of the VNF descriptor

    Returns:
        tuple: If an action is needed and the description of the flavor.
    """
    message = ""
    action = False

    logger.debug('flavor: {}'.format(flavor))
    logger.debug('suggested_changes: {}'.format(suggested_changes))

    try:
        if suggested_changes['cpu'] is not None:
            cpu = int(flavor['cpu']) + int(suggested_changes['cpu'])
            message += "- vCPU: {}\n".format(cpu)
            if cpu > 0 and int(suggested_changes['cpu']) != 0:
                action = True

        if suggested_changes['memory'] is not None:
            memory = float(flavor['memory']) + float(suggested_changes['memory'])
            message += "- MEMORY: {} MB\n".format(memory * 1024.0)
            if memory > 0.5 and int(suggested_changes['memory']) != 0:
                action = True

        if suggested_changes['disk'] is not None:
            disk = int(flavor['disk']) + int(suggested_changes['disk'])
            message += "- DISK: {} GB\n".format(disk)
            if disk > 10 and int(suggested_changes['disk']) != 0:
                action = True

    except Exception as ex:
        logger.exception(ex)
    finally:
        logger.debug('compare_flavor(): action={} | message={}\n'.format(action, message))
        return action, message


if __name__ == '__main__':
    # Retrieve the data every X minutes
    schedule.every(int(SCHEDULER_MINUTES)).minutes.do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)
    # main()
