import threading
import time
from connector import device, client
import json
from modules import device_pool
from api_manager import api_manager
import datetime
from modules.logger import root_logger
logger = root_logger.getChild(__name__)
import configparser
import os
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
            logger.info("get values from devices and push to platform")
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
                                service_response = float(service_response)

                                # TODO convert to string / float
                                payload = {
                                    "value": service_response,
                                    "time": datetime.datetime.now().isoformat()
                                }
                                # channel type uid == service id
                                logger.info("try to publish data from service: " + channel.get("channelTypeUID"))
                                logger.info("publish data: " + json.dumps(payload))
                                response = client.Client.event(device, channel.get("channelTypeUID"), json.dumps(payload))
                                logger.info(response.status)
            except Exception as e:
                logger.info(e)
