import threading
import requests 
import time 
import json 
from urllib import parse
from connector import device as device_file
from modules import singleton
from modules import device_pool
from connector import client
from api_manager import api_manager
import configparser
import os 
import logging
from modules.logger import connector_client_log_handler

logger = logging.getLogger("openhab_logger")
logger.setLevel(logging.DEBUG) 
logger.addHandler(connector_client_log_handler)


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
        logger.info("start monitoring openhab")
        while True:
            logger.info("restart monitoring")
            unknown_devices = None
            try:
                unknown_devices = self.openhab_api_manager.get_things()
            except Exception as e:
                logger.info(e)
            if unknown_devices:
                self._evaluate(unknown_devices)
            time.sleep(int(config["CONNECTOR"]["openhab_monitor_interval"]))
        
    def _evaluate(self, unknown_devices):   
        missing_devices, new_devices = self._diff(device_pool.DevicePool.devices(), unknown_devices)
        if missing_devices:
            logger.info(str(len(new_devices)) + " devices were deleted on OpenHAB")
            for device in missing_devices:
                client.Client.delete(device)
        if new_devices: 
            logger.info("Found " + str(len(new_devices)) + " new devices on OpenHAB")
            for device in new_devices:
                try:
                    self.add_device(device)
                except Exception as e:
                    logger.info(e)

    def _diff(self, known, unknown):
        known_set = set(known.keys())
        unknown_ids = list(map(lambda device: device.get("UID"), unknown))
        unknown_set = set(unknown_ids)
        missing = known_set - unknown_set
        new = unknown_set - known_set
        new = list(filter(lambda device: device.get("UID") in new, unknown))
        return missing, new

    def add_device(self,device):
        """
        Add a new device, regardless of its connection status
        """
        # TODO set status to connected/disconnected on device creation Yann?

        status = device.get("statusInfo")
        if status:
            if status.get("status") == "ONLINE":
                logger.info("try to add new device")
                device_type_json_formatted = self.get_device_type_json(device)
                found_on_platform, device_type_patform_id = self.get_platform_id(device_type_json_formatted)

                logger.info("device type " + json.loads(device_type_json_formatted).get("name") + " found on platform? " + str(found_on_platform))

                # if platform id exists then the device type was created already
                if not found_on_platform:
                    device_type_patform_id = self.create_type_on_platform(device_type_json_formatted)
                    logger.info("generated device type: " + str(device_type_patform_id))
                else:
                    logger.info("found device type: " + str(device_type_patform_id))

                if device_type_patform_id:
                    formatted_device = self.format(device, device_type_patform_id)
                    client.Client.add(formatted_device)
                    logger.info("added new device")

    def format(self,device,device_type_id_on_platform):
        device_name = device.get("label")
        device_id = device.get("UID")
        return device_file.Device(device_id, device_type_id_on_platform, device_name)
    
    def get_device_type_json(self, device):
        logger.info("generate device type in platform json format")
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


        for channel in device.get("channels"):
            # Get platform data type with the device instance channel
            # not possible to get data type from device type channel
            # distinguish between sensors and actuators, because they need different data types
            # if item is read only -> thing is sensor
            # also only add a channel as service type if it has a linked item which can be accessed to get data 
            linked_items = channel.get("linkedItems")
            if linked_items:
                item = self.openhab_api_manager.get_item(linked_items[0])
                thing_is_sensor = False
                if item:
                    state_desc = item.get("stateDescription") 
                    if state_desc:
                        thing_is_sensor = state_desc.get("readOnly")
                
                # only if a matching data type was found the platform on , create the device type
                data_type = self.get_platform_data_type(channel.get("itemType"), thing_is_sensor)
                if data_type:
                    service = {  
                            "protocol":{  
                                "id": config["PLATFORM"]["protocol_id"]
                            },
                            "device_class": {
                                "id": config["PLATFORM"]["device_class_id"]
                            },
                            "vendor": {
                                "id": config["PLATFORM"]["vendor_id"]
                            },
                            "name": channel.get("label", "no label"),
                            "description":  channel.get("description", "no description"),
                            "service_type":"http://www.sepl.wifa.uni-leipzig.de/ontlogies/device-repo#Sensor",
                            "url": channel.get("channelTypeUID", "no uri") 
                        }
                    
                    parameter = {  
                                "type": {  
                                    "id": data_type
                                },
                                "msg_segment":{  
                                    "id":"iot#88cd5b0e-a451-4070-a20d-464ee23742dd"
                                },
                                "name":"ValueType",
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
                    if thing_is_sensor: 
                        service["output"] = [parameter]
                    else:
                        service["input"] = [parameter]
                    device_type["services"].append(service)

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
            logger.info(same_device_types)
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
        device_types_with_same_name = self.platform_api_manager.get_device_types_with_name(device_type_json_formatted)
        logger.info(device_types_with_same_name)
        # 1. Check if device type has service, e.g Netatmo API has no services, as it is only the API but registered as device
        # 2. Check if there are device types with same name, if no, then create new device type, if yes, compare services
        # 3. Compare services
        if len(services) == 0:
            return (True, found_device_type_id)
        elif not device_types_with_same_name["Exists"]:
            return (False, None)
        else:
            found_device_type_id = self.get_types_with_service([], services, 0)

        if found_device_type_id:
            # check if keys from my generated device type have the same value as the one from the platform
            # todo
            found_device_type_object = self.platform_api_manager.get_device_type(parse.quote_plus(found_device_type_id))
            # last check for general proerperties of device type like name
            check_properties = ["name", "description"]
            for check in check_properties:
                if found_device_type_object.get(check) != device_type.get(check):
                    return (False, found_device_type_id)

            return (True, found_device_type_id)
        else:
            return (False, found_device_type_id)

    def get_platform_data_type(self, item_type, thing_is_sensor):
        """
        Map the item types from openhab with platform data types.
        """

        if thing_is_sensor:
            # Use data type that adds a timestamp {"value": value, "time": time}
            type_map = {
                "Number": config["PLATFORM"]["number_time_data_type"],
                "Location": config["PLATFORM"]["string_time_data_type"],
                "Switch": config["PLATFORM"]["string_time_data_type"],
                "String": config["PLATFORM"]["string_time_data_type"]
            }
        else:
            # Thing is an actuator -> use data type that matches the OpenHAB data type e.g plain string or number
            type_map = {
                "Number": config["PLATFORM"]["number_data_type"],
                "Location": config["PLATFORM"]["string_data_type"],
                "Switch": config["PLATFORM"]["string_data_type"],
                "String": config["PLATFORM"]["string_data_type"]
            }

        return type_map.get(item_type)

    def create_type_on_platform(self,device_type_json_formatted):
        logger.info("try to create new device type")
        response = self.platform_api_manager.create_type(device_type_json_formatted)
        logger.info(response)
        device_type_id_on_platform = response.get("id")
        return device_type_id_on_platform 

  