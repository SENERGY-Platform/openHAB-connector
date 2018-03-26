import threading
import requests 
import time 
import json 
from urllib import parse
from connector_client.connector import device as device_file
from connector_client.modules import singleton
from connector_client.modules import device_pool
from connector_client.connector import client
from api_manager import api_manager
import configparser
import os 

dir = os.path.dirname(__file__)
filename = os.path.join(dir, '../config.ini')
config = configparser.ConfigParser()
config.read(filename)

# todo: Yann connector client post device type support 

class Monitor(threading.Thread):
    def __init__(self):
        super().__init__()
        self.openhab_api_manager = api_manager.OpenhabAPIManager()
        self.platform_api_manager = api_manager.PlatformAPIManager()

    def run(self):
        while True:
            try:
                time.sleep(int(config["CONNECTOR"]["openhab_monitor_interval"]))
                unknown_devices = self.openhab_api_manager.get_things()
                if unknown_devices:
                    self._evaluate(unknown_devices)
            except Exception as e:
                print(e)

    def _evaluate(self, unknown_devices):   
        missing_devices, new_devices = self._diff(device_pool.DevicePool.devices(), unknown_devices)
        if missing_devices:
            for device in missing_devices:
                client.Client.delete(device)
        if new_devices: 
            for device in new_devices:
                self.add_device(device)

    def _diff(self, known, unknown):
        known_set = set(known.keys())
        unknown_ids = list(map(lambda device: device.get("UID"), unknown))
        unknown_set = set(unknown_ids)
        missing = known_set - unknown_set
        new = unknown_set - known_set
        new = list(filter(lambda device: device.get("UID") in new, unknown))
        return missing, new

    def add_device(self,device):
        print("add_device()")
        device_type_json_formatted = self.get_device_type_json(device)
        found_on_platform, device_type_patform_id = self.get_platform_id(device_type_json_formatted)
        print("device type found on platform? " + str(found_on_platform))

        # if platform id exists then the device type was created already 
        if not found_on_platform:
            print("create new device type")
            self.create_type_on_platform(device_type_json_formatted)

        # device type id exists and device is online
        status = device.get("statusInfo")
        if status:
            device_is_connected = status.get("status")
            if device_type_patform_id and device_is_connected == "ONLINE":
                print("device type ID: " + str(device_type_patform_id))
                print("add new device")
                formatted_device = self.format(device, device_type_patform_id)
                client.Client.add(formatted_device)

    def format(self,device,device_type_id_on_platform):
        device_name = device.get("label")
        device_id = device.get("UID")
        return device_file.Device(device_id, device_type_id_on_platform, device_name)
    
    def get_device_type_json(self, device):
        device_type_informations = self.openhab_api_manager.get_thing_type(device.get("thingTypeUID"))
        
        # Object structure for IoT Repository
        device_type = {  
            "device_class":{  
                "id":"iot#74806075-4c2a-47a3-9694-685de26add3d",
            },
            "vendor":{  
                "id":"iot#a9157959-8967-4d0e-8bfd-af079d821a3d",
            },
            "name": device_type_informations.get("label", ""),
            "description": device_type_informations.get("description", ""),
            "services": [],
            "config_parameter":[  

            ]
        }

        data_types = {}
        for channel in device.get("channels"):
            # Get platform data type with the device instance channel
            # not possible to get data type from device type channel
            data_types[channel.get("channelTypeUID")] = {
                "data_type": self.get_platform_data_type(channel.get("itemType"))
            }

        services = []
        for channel in device_type_informations.get("channels"):
            service = {
                "name": channel.get("label", "no label"),
                "desc": channel.get("description", "no description"),
                "uri": channel.get("typeUID", "no uri")          
            }

            data_type = data_types.get(service.get("uri"))
            if data_type:
                service["data_type_id_platform"] = data_type.get("data_type")

            services.append(service)

        for service in services:        
            # only if a matching data type was found the platform on , create the device type
            if service.get("data_type_id_platform"):
                device_type["services"].append(  
                    {  
                        "protocol":{  
                            "id":"iot#d6a462c5-d4e0-4396-b3f3-28cd37b647a8"
                        },
                        "config_parameter":[  

                        ],
                        "input":[  
                         {  
                            "type": {  
                                "id": service.get("data_type_id_platform")
                            },
                            "msg_segment":{  
                                "id":"iot#88cd5b0e-a451-4070-a20d-464ee23742dd"
                            },
                            "name":"ValueType",
                            "format":"http://www.sepl.wifa.uni-leipzig.de/ontlogies/device-repo#PlainText",
                            "additional_formatinfo":[  
                                {  
                                    "field":{  
                                        "id":"iot#7d4df496-0df0-4323-ba6b-0a0eaf90840d"
                                    },
                                    "format_flag":None
                                }
                            ]
                            }
                        ],
                        "output":[  
                        ],
                        "name": service.get("name"),
                        "description": service.get("desc"),
                        "service_type":"http://www.sepl.wifa.uni-leipzig.de/ontlogies/device-repo#Sensor",
                        "url": service.get("uri")
                    }
                )

        return json.dumps(device_type)

    def get_types_with_service(self, device_types, services, index):
        # Query all device types that have this one service
        response = self.platform_api_manager.get_device_types_with_service(json.dumps(services[index]))
        if response:
            same_device_types = []
            if index == 0:
                same_device_types = response
            else:
                same_device_types = list(set(device_types) & set(response))

            length_same_device_types = len(same_device_types) 
            if length_same_device_types == 0:
                # Nothing found
                return False
            elif length_same_device_types == 1:
                # Only one result, no futher checks needed
                return same_device_types[0]
            else:
                # More than one device type found -> more service checks
                found_device_type = self.get_types_with_service(same_device_types, services, index + 1)
                return found_device_type
        else:
            return False

    def get_platform_id(self, device_type_json_formatted):
        """
        SPARQL query where the whole device type json structure is used to search a device type, is to slow.
        So I have to query all device types that have one service and iterate through all services until only one device type matches all.
        """

        device_type = json.loads(device_type_json_formatted)
        services = device_type.get("services", [])
        found_device_type_id = False
        if len(services) == 0:
            # Case: Device type with no service like Netatmo API -> is not important -> should not be on the platform
            return (True, found_device_type_id)
        else: 
            found_device_type_id = self.get_types_with_service([], services, 0)
            
        if found_device_type_id:
            # check if keys from my generated device type have the same value as the one from the platform 
            #todo
            found_device_type_object = self.platform_api_manager.get_device_type(parse.quote_plus(found_device_type_id))
            # last check for general proerperties of device type like name 
            check_properties = ["name", "description"]
            for check in check_properties:
                if found_device_type_object.get(check) != device_type.get(check):
                    return (False, found_device_type_id)
            
            return (True, found_device_type_id)
        else:
            return (False,found_device_type_id)

    def get_platform_data_type(self, item_type):
        """
        Map the item types from openhab with platform data types.
        """

        type_map = {
            "Number": config["PLATFORM"]["number_data_type"],
            "Location": config["PLATFORM"]["string_data_type"],
            "Switch": config["PLATFORM"]["string_data_type"],
            "String": config["PLATFORM"]["string_data_type"]
        }

        return type_map.get(item_type)

    def create_type_on_platform(self,device_type_json_formatted):
        response = self.platform_api_manager.create_type(device_type_json_formatted)
        print(response)
        device_type_id_on_platform = response.get("id")
        return device_type_id_on_platform 

  