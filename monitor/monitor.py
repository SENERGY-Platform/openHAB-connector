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

# todo: Yann connector client post device type support 

class Monitor(threading.Thread):
    def __init__(self, ip, port, iot_repo):
        super().__init__()
        self.openhab_ip = ip 
        self.openhab_port = port 
        self.iot_repository = iot_repo
        self.api_manager = api_manager.APIManager(self.openhab_ip, self.openhab_port)

    def run(self):
        while True:
            time.sleep(10)
            unknown_devices = self.api_manager.get_things()
            if unknown_devices:
                self._evaluate(unknown_devices)

    def _diff(self, known, unknown):
        known_set = set(known.keys())
        unknown_ids = list(map(lambda device: device.get("UID"), unknown))
        unknown_set = set(unknown_ids)
        missing = known_set - unknown_set
        new = unknown_set - known_set
        new = list(filter(lambda device: device.get("UID") in new, unknown))
        return missing, new

    def format(self,device,device_type_id_on_platform):
        device_name = device.get("label")
        device_id = device.get("UID")
        return device_file.Device(device_id, device_type_id_on_platform, device_name)

    def _evaluate(self, unknown_devices):        
        missing_devices, new_devices = self._diff(device_pool.DevicePool.devices(), unknown_devices)
        if missing_devices:
            for device in missing_devices:
                client.Client.delete(device)
        
        if new_devices:
            for device in new_devices:
                self.add_device(device)
    
    def get_device_type_json(self, device):
        device_type_informations = self.api_manager.get_thing_type(device.get("thingTypeUID"))
        
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
            data_types[channel.get("channelTypeUID")] = {
                "data_type": self.get_platform_data_type(channel.get("itemType"))
            }

        services = []
        for channel in device_type_informations.get("channels"):
            services.append({
                "name": channel.get("label", "no label"),
                "desc": channel.get("description", "no description"),
                "uri": channel.get("typeUID", "no uri")            
            })

        for service in services:        
            # only if a data type was found, create the device type
            data_type_id_platform = data_types.get(service.get("uri")).get("data_type")
            if data_type_id_platform:
                device_type["services"].append(  
                    {  
                        "protocol":{  
                            "id":"iot#d6a462c5-d4e0-4396-b3f3-28cd37b647a8"
                        },
                        "config_parameter":[  

                        ],
                        "input":[  

                        ],
                        "output":[  
                            {  
                            "type": {  
                                "id": data_type_id_platform
                            },
                            "msg_segment":{  
                                "id":"iot#88cd5b0e-a451-4070-a20d-464ee23742dd"
                            },
                            "name":"Value Type",
                            "format":"http://www.sepl.wifa.uni-leipzig.de/ontlogies/device-repo#json",
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
                        "name": service.get("name"),
                        "description": service.get("desc"),
                        "service_type":"http://www.sepl.wifa.uni-leipzig.de/ontlogies/device-repo#Sensor",
                        "url": service.get("uri")
                    }
                )

        return json.dumps(device_type)


    def add_device(self,device):
        device_type_json_formatted = self.get_device_type_json(device)
        found_on_platform, device_type_patform_id = self.get_platform_id(device_type_json_formatted)
        print(found_on_platform)
        print(device_type_patform_id)
        # if platform id exists then the device type was created already 
        if not found_on_platform:
            self.create_type_on_platform(device_type_json_formatted)

        if device_type_patform_id:
            formatted_device = self.format(device, device_type_patform_id)
            client.Client.add(formatted_device)

    def get_types_with_service(self, device_types, services, index):
        # Query all device types that have this one service
        url = self.iot_repository + "/query/service"
        response = requests.post(url, data=json.dumps(services[index])).json()
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
            url = self.iot_repository + "/deviceType/" + parse.quote_plus(found_device_type_id)
            found_device_type_object = requests.get(url).json()
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
            "Number": "iot#ae51bb9c-af3a-495a-aebf-c46469045e05",
            "Location" : "iot#659baf31-64ec-44e9-85fc-2c154ba04976",
            "Switch": "iot#659baf31-64ec-44e9-85fc-2c154ba04976",
            "String": "iot#659baf31-64ec-44e9-85fc-2c154ba04976"

        }

        return type_map.get(item_type)

    def create_type_on_platform(self,device_type_json_formatted):
        response = requests.post(self.iot_repository + "/deviceType",data=device_type_json_formatted)
        device_type_id_on_platform = response.json().get("id")
        return device_type_id_on_platform 

  