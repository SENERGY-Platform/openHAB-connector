import threading
import time
from connector_client.connector import device, client
import json
from connector_client.modules import device_pool
import requests
from api_manager import api_manager
import datetime

class Observer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.openhab_api_manager = api_manager.OpenhabAPIManager()
    
    def run(self):
        while True:
            time.sleep(30)
            connected_devices = device_pool.DevicePool.devices()
            for device in connected_devices:
                device_json = self.openhab_api_manager.get_thing(device)

                channels = device_json.get("channels")
                for channel in channels:
                    items = channel.get("linkedItems")
                    if len(items) != 0:
                        service_response = self.openhab_api_manager.get("/" + items[0])
                        service_response_value = service_response.get("state")
                        payload = {
                            "value": service_response_value,
                            "time": datetime.datetime.now().isoformat()
                        }
                        # channel type uid == service id
                        client.Client.event(device, channel.get("channelTypeUID"), json.dumps(payload))
                    
         