import threading
import time
from connector_client.connector import device, client
import json
from connector_client.modules import device_pool
from api_manager import api_manager
import datetime
from connector_client.modules.logger import root_logger
logger = root_logger.getChild(__name__)

class Observer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.openhab_api_manager = api_manager.OpenhabAPIManager()
    
    def run(self):
        while True:
            time.sleep(30)
            logger.info("get values from devices and push to platform")
            connected_devices = device_pool.DevicePool.devices()
            for device in connected_devices:
                device_json = self.openhab_api_manager.get_thing(device)

                channels = device_json.get("channels")
                for channel in channels:
                    items = channel.get("linkedItems")
                    if len(items) != 0:
                        service_response = self.openhab_api_manager.getItemState(items[0])
                        try:
                            service_response = float(service_response)
                        except ValueError as e:
                            pass

                        # TODO convert to string / float
                        payload = {
                            "value": service_response,
                            "time": datetime.datetime.now().isoformat()
                        }
                        # channel type uid == service id
                        logger.info("try to publish data from service: " + channel.get("channelTypeUID"))
                        client.Client.event(device, channel.get("channelTypeUID"), json.dumps(payload))
                        logger.info("published data: " + json.dumps(payload))