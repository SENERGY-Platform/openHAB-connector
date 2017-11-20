import requests 
import time 
import threading
from connector_client.connector import client
from connector_client.connector import device as device_file
from connector_client.modules import device_pool



# get data from openhab items -> channel id = rest api je funtkion => service url auf platform 

hab_ip = "smartpi"
hab_port = 8080

class Monitor(threading.Thread):
    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip 
        self.port = port 

    def run(self):
        while True:
            time.sleep(10)
            unknown_devices = self.get_items()
            if unknown_devices:
                self._evaluate(unknown_devices)

    def _diff(self, known, unknown):
        known_set = set(known.keys())
        unknown_ids = list(map(lambda device: device.get("UID"), unknown))
        unknown_set = set(unknown_ids)
        missing = known_set - unknown_set
        new = unknown_set - known_set
        new = list(filter(lambda device: device.get("UID") in new, unknown))
        print(new)
        return missing, new

    def format(self,device):
        return device_file.Device(device.get("UID"), "iot#1a6572ed-f572-44df-be22-4ea844d6381b", device.get("label"))

    def _evaluate(self, unknown_devices):        
        missing_devices, new_devices = self._diff(device_pool.DevicePool.devices(), unknown_devices)
        if missing_devices:
            for device in missing_devices:
                client.Client.delete(device)
        
        if new_devices:
            for device in new_devices:
                formatted_device = self.format(device)
                client.Client.add(formatted_device)
        
    def get_items(self):
        response = requests.get("http://{ip}:{port}/rest/things".format(ip=self.ip, port=self.port))
        return response.json()

if __name__ == "__main__":
    connector_client = client.Client(device_manager=device_pool.DevicePool) 
    monitor = Monitor(hab_ip, hab_port)
    monitor.start()