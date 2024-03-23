import ovh
import requests
import os
import logging

log_level = os.getenv('OVH_LOG_LEVEL', 'WARNING').upper()

logging.basicConfig(
	level=log_level,
	format='%(asctime)s [%(levelname)s] (%(name)s) %(message)s',
	datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)


# Główne zmienne
OVH_ENDPOINT = os.getenv('OVH_ENDPOINT',"ovh-eu")
OVH_APPLICATION_KEY=os.getenv('OVH_APPLICATION_KEY',"OVH_APPLICATION_KEY")
OVH_APPLICATION_SECRET=os.getenv('OVH_APPLICATION_SECRET',"OVH_APPLICATION_SECRET")
OVH_CONSUMER_KEY=os.getenv('OVH_CONSUMER_KEY',"OVH_CONSUMER_KEY")

OVH_DOMAIN_NAME = os.getenv('OVH_DOMAIN_NAME',"OVH_DOMAIN_NAME")
OVH_SUBDOMAIN = os.getenv('OVH_SUBDOMAIN',"*")


logger.info(f"Update dynamic dns hosted on OVH {OVH_ENDPOINT}, domain {OVH_SUBDOMAIN}.{OVH_DOMAIN_NAME}")


def get_client():
    return  ovh.Client(
        endpoint=OVH_ENDPOINT,     # Endpoint API for EU; 'ovh-ca' for Canada, 'ovh-us' for USA USA itd.
        application_key=OVH_APPLICATION_KEY,    # Podmień na swoją Application Key
        application_secret=OVH_APPLICATION_SECRET, # Podmień na swój Application Secret
        consumer_key=OVH_CONSUMER_KEY,       # Podmień na swój Consumer Key
    )

# create default client
OVH_CLIENT = get_client()


def get_records(domain_name, client=OVH_CLIENT):
    return client.get(f'/domain/zone/{domain_name}/record')

def get_record(domain_name, record_id,client=OVH_CLIENT):
    return client.get(f'/domain/zone/{domain_name}/record/{record_id}')

def refresh_domain(domain_name,client=OVH_CLIENT):
    return client.post(f'/domain/zone/{domain_name}/refresh')

def update_record(domain_name,record_id,new_target,client=OVH_CLIENT):
    return client.put(f'/domain/zone/{domain_name}/record/{record_id}',target=new_target)

def get_public_ip():
    response = requests.get('https://api.ipify.org')
    if response.status_code == 200:
        return response.text
    else:
        raise Exception("I could get an external IP.")


def update_external_addres():
    try:
        logger.debug(f'OVH Getting client APPLICATION_KEY={OVH_APPLICATION_KEY}')
        logger.debug(f'OVH Getting client APPLICATION_SECRET={OVH_APPLICATION_SECRET}')
        logger.debug(f'OVH Getting client CONSUMER KEY={OVH_CONSUMER_KEY}')
        logger.debug(f'OVH Getting client OVH_ENDPOINT={OVH_ENDPOINT}')
        logger.debug(f'OVH Getting client OVH_DOMAIN_NAME={OVH_DOMAIN_NAME}')
        logger.debug(f'OVH Getting client OVH_SUBDOMAIN={OVH_SUBDOMAIN}')
        new_ip = get_public_ip()
        logger.debug(f'Public IP = {new_ip}')
        logger.debug(f'OVH Getting client CLIENT={OVH_CLIENT}')
        records = get_records(domain_name=OVH_DOMAIN_NAME,client=OVH_CLIENT)
        logger.debug(f'OVH Getting client records={records}')
        for record_id in records:
            record = get_record(domain_name=OVH_DOMAIN_NAME,record_id=record_id)
            if record.get('subDomain','X')==OVH_SUBDOMAIN:
                current_ip = record.get('target','X')
                if current_ip!=new_ip:
                    update_record(domain_name=OVH_DOMAIN_NAME, record_id=record_id,new_target=new_ip)
                    refresh_domain(domain_name=OVH_DOMAIN_NAME)
                    logger.info(f"IP address changed, your new external IP adress: {new_ip}")
                else:
                    logger.info(f"No change, your external IP adress: {current_ip}")
    except Exception as e:
        logger.error(e)

update_external_addres()
