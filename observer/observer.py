import threading, time, json, datetime, configparser, os, logging
from connector_client.client import Client
from connector_client.modules import device_pool
from api_manager import api_manager
from logger.logger import root_logger

logger = root_logger.getChild('observer')

dir = os.path.dirname(__file__)
filename = os.path.join(dir, '../config.ini')
config = configparser.ConfigParser()
config.read(filename)

class Observer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.openhab_api_manager = api_manager.OpenhabAPIManager()
    
    def run(self):
        logger.info("Start observing of values")
        while True:
            time.sleep(int(config["CONNECTOR"]["ping_interval"]))
            logger.debug("get values from devices and push to platform")
            connected_devices = device_pool.DevicePool.devices()
            try:
                for device in connected_devices:
                    device_json = self.openhab_api_manager.get_thing(device)

                    channels = device_json.get("channels")
                    for channel in channels:
                        items = channel.get("linkedItems")
                        if items:
                            if len(items) != 0:
                                service_response = self.openhab_api_manager.getItemState(items[0])
                                # convert depending on data type
                                if channel.get("itemType") == "Number":
                                    service_response = float(service_response)

                                payload = {
                                    "value": service_response,
                                    "time": datetime.datetime.utcnow().isoformat()
                                }
                                # channel type uid == service id
                                logger.debug("try to publish data from service: " + channel.get("channelTypeUID"))
                                logger.debug("publish data: " + json.dumps(payload))
                                response = Client.event(device, channel.get("channelTypeUID"), json.dumps(payload))
                                logger.debug(response.status)
            except Exception as e:
                logger.error(e)
