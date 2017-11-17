import requests 
import time 
import threading

hab_ip = "127.0.0.1"
hab_port = 8080

class Monitor(threading.Thread):
    def __init__(self):
        super().__init__()
        self._known_devices = dict()

    def run(self):
        while True:
            time.sleep(30)
            unknown_devices = self.get_items()
            if unknown_devices:
                self._evaluate(unknown_devices)

    def _diff(self, known, unknown):
        known_set = set(known)
        unknown_set = set(unknown)
        missing = known_set - unknown_set
        new = unknown_set - known_set
        return missing, new


    def _evaluate(self, unknown_devices):
        missing_devices, new_devices = self._diff(self._known_devices, unknown_devices)
        if missing_devices:
            for missing_device_id in missing_devices:
                del __class__.deconz_map[missing_device_id]
                Client.remove(missing_device_id)
        if new_devices:
            for new_device_id in new_devices:
                name = unknown_devices[new_device_id].get('name')
                __class__.deconz_map[new_device_id] = unknown_devices[new_device_id].get('LIGHT_KEY')
                Client.add(device)

    def get_items(self):
        return requests.get("http://{ip}:{port}/rest/things".format(ip=hab_ip, port=hab_port))

if __name__ == "__main__":
    connector_client = Client(device_manager=DevicePool)    
    items = get_items()
    print(items.json())