import logging.config
from notifier import Email
from settings import LOGGING, EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, \
    EMAIL_NOTIFICATION_ENABLED, EMAIL_PORT

logging.config.dictConfig(LOGGING)
logger = logging.getLogger("worker")


def add_recommendation(redmine, project, subject, description, category_id=2):
    """ Publish a recommendation as an issue in the SVP Redmine

    Args:
        redmine (object): The Redmine object
        project (object): The project object (in Redmine)
        subject (str): The title of the recommendation
        description (str): The description of the recommendation
        category_id (int): The identifier of the category of this type of issues
    """
    try:
        redmine.issue.create(project_id=project.identifier, subject=subject,
                             description=description, category_id=category_id)
    except Exception as ex:
        logger.exception(ex)


def get_redmine_issues_categories():
    return {'openstack': 2, 'kubernetes': 3, 'opennebula': 4}


def email_notification(receiver, content):
    """ Notify the vendor

    Args:
        receiver (str): The receiver email
        content (dict): The email body as a dict
    """
    if not EMAIL_NOTIFICATION_ENABLED:
        return

    try:
        email = Email(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_HOST, EMAIL_PORT)
        receivers = list()
        receivers.append(receiver)
        email.send_email(receivers, content)
    except Exception as ex:
        logger.exception(ex)
