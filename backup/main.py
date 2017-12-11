import requests 
import time 
import threading
from connector_client.connector import client
from connector_client.connector import device as device_file
from connector_client.modules import device_pool
from connector_client.modules import singleton
import json 
from urllib import parse
import sqlite3


# todo: Yann connector client post device type support 

iot_repo = "http://fgseitsrancher.wifa.intern.uni-leipzig.de:8000/iot-device-repo/deviceType"
hab_ip = "openhabianpi"
hab_port = 8080

class DB(singleton.SimpleSingleton):
    """
    Database class, for SQL execution on a SQLite file.
    Containts device type mapping between already created platform types and openhab device types
    """
    _db_path = 'device_types.sqlite'

    def __init__(self):
        self._executeQuery("""CREATE TABLE IF NOT EXISTS types(
              openhab_device_type_id VARCHAR(100) PRIMARY KEY,
              platform_device_type_id VARCHAR(100)
          )""")

    def add_types(self, platform_id, openhab_id):
        
        query = """
        IF EXISTS ( SELECT 1 FROM types WHERE openhab_device_type_id = '{openhab_id}' )
        BEGIN
        UPDATE types 
        SET (
            platform_device_type_id = '{platform_id}'
            openhab_device_type_id = '{openhab_id}'
        )
        WHERE openhab_device_type_id = '{openhab_id}'
        END
        """.format(platform_id=platform_id,openhab_id=openhab_id)
        self._executeQuery(query)

    def get_platform_id(self, openhab_id):
        query = """
            SELECT platform_device_type_id FROM types
            WHERE openhab_device_type_id = '{openhab_id}'
        """.format(openhab_id=openhab_id)
        response = self._executeQuery(query)
        # todo ??
        print(response)
        if len(response) == 0:
            return None
        return response[0][0]

    def get_types(self):
        query = """
            SELECT * FROM types
        """
        response = self._executeQuery(query)
        return response
        
    @staticmethod
    def _executeQuery(query):
        db_conn = sqlite3.connect(__class__._db_path)
        cursor = db_conn.cursor()
        cursor.execute(query)
        if any(statement in query for statement in ('CREATE', 'INSERT', 'DELETE', 'UPDATE')):
            db_conn.commit()
            result = True
        else:
            result = cursor.fetchall()
        db_conn.close()
        return result
        

class Monitor(threading.Thread):
    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip 
        self.port = port 
        self.db = DB()

    def run(self):
        while True:
            time.sleep(10)
            unknown_devices = self.get_things()
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

    def format(self,device):
        device_name = device.get("label")
        device_id = device.get("UID")
        device_type = self.db.get_platform_id(device.get("thingTypeUID"))
        return device_file.Device(device_id, device_type, device_name)

    def _evaluate(self, unknown_devices):        
        missing_devices, new_devices = self._diff(device_pool.DevicePool.devices(), unknown_devices)
        if missing_devices:
            for device in missing_devices:
                client.Client.delete(device)
        
        if new_devices:
            for device in new_devices:
                self.add_device(device)
    
    def add_device(self,device):
        device_type_id = device.get("thingTypeUID")
        if not self.type_exists_on_platform(device_type_id):
            device_type_id_on_platform = self.create_type_on_platform(device)
            print(device_type_id_on_platform)
            self.db.add_types(device_type_id_on_platform,device_type_id)

        formatted_device = self.format(device)
        print("-------------------")
        print(formatted_device)
        client.Client.add(formatted_device)

    def type_exists_on_platform(self,device_type_id):
        """
        Get the platform id mapped to the openhab device type id.
        If it is not mapped, then it was never created.
        If it was mapped, then it was created at some time. 
        Then check if i is still exists on platform side by GET Request to platform
        """
        device_platform_id = self.db.get_platform_id(device_type_id)
        print(device_platform_id)
        if device_platform_id:
            url = parse.urljoin(iot_repo + "/", parse.quote_plus(device_platform_id))
            print(url)
            response = requests.get(url)
            print(response)
            ## if not exsit json() not working todo
            return len(response.json().get("device_class")) != 0 
        else:
            return False

    def get_platform_data_type(self, item_type):
        """
        Map the item types from openhab with platform data types.
        """
        type_map = {
            "Number": {  
                    "id":"iot#5b297825-f88e-46c5-a525-794e9a3b8a1e",
                    "name":"OpenHAB-number",
                    "description":"Decimal number like 1",
                    "base_type":"http://www.w3.org/2001/XMLSchema#integer",
                    "fields":None,
                    "literal":""
            }
        }

        return type_map.get(item_type)

    def create_type_on_platform(self,device):
        device_type_informations = self.get_thing_type(device.get("thingTypeUID"))

        # Object structure for IoT Repository
        device_type = {  
            "device_class":{  
                "id":"iot#74806075-4c2a-47a3-9694-685de26add3d",
                "name":"sensorBinary"
            },
            "vendor":{  
                "id":"iot#a9157959-8967-4d0e-8bfd-af079d821a3d",
                "name":"libelium"
            },
            "name": device_type_informations.get("label", ""),
            "description": device_type_informations.get("description", ""),
            "services": [],
            "config_parameter":[  

            ]
        }

        channels_1 = {}
        for channel in device.get("channels"):
            service = {
                "data_type": self.get_platform_data_type(channel.get("itemType"))
            }
            channels_1[channel.get("id")] = service 

        services = {}
        for channel in device_type_informations.get("channels"):
            service = {
                "name": channel.get("label", "no label"),
                "desc": channel.get("description", "no description"),
                "uri": channel.get("typeUID", "no uri")
            }
            services[channel.get("id")] = service

        for service in services:
            device_type["services"].append(  
                {  
                    "protocol":{  
                        "id":"iot#d6a462c5-d4e0-4396-b3f3-28cd37b647a8",
                        "protocol_handler_url":"connector",
                        "name":"standard-connector",
                        "description":"Generic protocol for transporting data and metadata.",
                        "msg_structure":[  
                        {  
                            "id":"iot#37ff5298-a7dd-4744-9080-7cfdbda5dc72",
                            "name":"metadata",
                            "constraints":None
                        },
                        {  
                            "id":"iot#88cd5b0e-a451-4070-a20d-464ee23742dd",
                            "name":"data",
                            "constraints":None
                        }
                        ]
                    },
                    "config_parameter":[  

                    ],
                    "input":[  

                    ],
                    "output":[  
                        {  
                        "type": {  
                            "id":"iot#ae51bb9c-af3a-495a-aebf-c46469045e05",
                            "name":"openhab-number",
                            "description":"Decimal number like 1",
                            "base_type":"http://www.w3.org/2001/XMLSchema#decimal",
                            "fields":None,
                            "literal":""
                        },
                        "msg_segment":{  
                            "id":"iot#88cd5b0e-a451-4070-a20d-464ee23742dd",
                            "name":"data",
                            "constraints": None
                        },
                        "name":"data type",
                        "format":"http://www.sepl.wifa.uni-leipzig.de/ontlogies/device-repo#json",
                        "additional_formatinfo":[  
                            {  
                                "field":{  
                                    "id":"iot#7d4df496-0df0-4323-ba6b-0a0eaf90840d",
                                    "name":"color",
                                    "type":{  
                                    "id":"iot#c8c36810-c8e0-403e-b00f-187414a84ccd",
                                    "name":"text",
                                    "description":"text",
                                    "base_type":"http://www.w3.org/2001/XMLSchema#string",
                                    "fields":None,
                                    "literal":None
                                    }
                                },
                                "format_flag":None
                            }
                        ]
                        }
                    ],
                    "name": services[service].get("name"),
                    "description": services[service].get("desc"),
                    "service_type":"http://www.sepl.wifa.uni-leipzig.de/ontlogies/device-repo#Sensor",
                    "url": services[service].get("uri")
                }
            )
        print(json.dumps(device_type))
        response = requests.post(iot_repo,data=json.dumps(device_type))
        device_type_id_on_platform = response.json().get("id")
        return device_type_id_on_platform 

    def get_item(self,item):
        response = requests.get("{item}".format(item=item))
        return response.json()

    def get_thing_type(self,type_id):
        response = requests.get("http://{ip}:{port}/rest/thing-types/{id}".format(ip=self.ip, port=self.port,id=type_id))
        print("THING TYPES:")
        return response.json()
        
    def get_things(self):
        response = requests.get("http://{ip}:{port}/rest/things".format(ip=self.ip, port=self.port))
        print("THINGS:")
        return response.json()

if __name__ == "__main__":
    connector_client = client.Client(device_manager=device_pool.DevicePool) 
    monitor = Monitor(hab_ip, hab_port)
    monitor.start()

    # unit test
    # 1. add types dann abfragen checken
    # 2. types nicht vorhanden dann abfragen checken 
    #db = DB()
    #db.add_types("a", "b")
    #print(db.get_types())
    #print(db.get_platform_id("b"))