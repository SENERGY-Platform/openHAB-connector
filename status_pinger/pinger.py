# /things mit ids aus device ppool status checken 
from api_manager import api_manager
import threading
from connector_client.modules import device_pool
import time 
from connector_client.connector import client

class Pinger(threading.Thread):
    def __init__(self):
        super().__init__()
        self.openhab_api_manager = api_manager.OpenhabAPIManager()
        self.platform_api_manager = api_manager.PlatformAPIManager()

    def run(self):
        while True:
            time.sleep(10)
            current_connected_devices = device_pool.DevicePool.devices().keys()
            if len(current_connected_devices) is not 0:
                for device_id in current_connected_devices:
                    self.ping(device_id)

    def ping(self, device_id):
        response = self.openhab_api_manager.get_thing(device_id)
        status = response.get("statusInfo")
        if status:
            if status.get("status") == "OFFLINE":
                client.Client.disconnect(device_id)
            elif status == "ONLINE":
                device = device_pool.DevicePool.get(device_id)
                client.Client.add(device)

