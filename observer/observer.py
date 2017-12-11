import threading
import time
from connector_client.connector import device, client
import json
from connector_client.modules import device_pool
import requests

class Observer(threading.Thread):
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
    
    def run(self):
        while True:
            time.sleep(30)
            connected_devices = device_pool.DevicePool.devices()
            for device in connected_devices:
                response = requests.get("http://{ip}:{port}/rest/things/{device_id}".format(ip=self.ip, port=self.port, device_id=device))
                device_json = response.json()

                channels = device_json.get("channels")
                for channel in channels:
                    items = channel.get("linkedItems")
                    if len(items) != 0:
                        service_response = requests.get("http://{ip}:{port}/rest/items/{item}".format(ip=self.ip, port=self.port, item=items[0]))
                        service_response_value = service_response.json().get("state")
                        client.Client.event(device, channel.get("channelTypeUID"), service_response_value)
                    
         