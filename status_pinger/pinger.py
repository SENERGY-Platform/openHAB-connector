# /things mit ids aus device ppool status checken 
from api_manager import api_manager
import threading
from modules import device_pool
import time 
from connector import client
import configparser
import os 
import logging
from modules.logger import connector_client_log_handler


dir = os.path.dirname(__file__)
filename = os.path.join(dir, '../config.ini')
config = configparser.ConfigParser()
config.read(filename)

logger = logging.getLogger("openhab_logger")
logger.setLevel(logging.DEBUG) 
logger.addHandler(connector_client_log_handler)

class Pinger(threading.Thread):
    def __init__(self):
        super().__init__()
        self.openhab_api_manager = api_manager.OpenhabAPIManager()
        self.platform_api_manager = api_manager.PlatformAPIManager()

    def run(self):
        while True:
            time.sleep(int(config["CONNECTOR"]["ping_interval"]))
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

