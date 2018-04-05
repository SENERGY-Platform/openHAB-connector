import requests 
import configparser
import os
dir = os.path.dirname(__file__)
filename = os.path.join(dir, '../config.ini')
config = configparser.ConfigParser()
config.read(filename)
from connector_client.modules.logger import root_logger
logger = root_logger.getChild(__name__)

class APIManager():
    def __init__(self, ip, port, base_path="", scheme="http"):
        self.ip = ip 
        self.port = port 
        self.base_path = base_path
        self.scheme = scheme 
    
    def get(self, path, headers=None):
        response = requests.get("{scheme}://{ip}:{port}{base_path}{path}".format(scheme=self.scheme,ip=self.ip, port=self.port,base_path=self.base_path,path=path), headers=headers)
        return response

    def post(self, path, payload, headers=None):
        url = "{scheme}://{ip}:{port}{base_path}{path}".format(scheme=self.scheme,ip=self.ip, port=self.port,base_path=self.base_path,path=path)
        response = requests.post(url,data=payload, headers=headers)
        return response

class OpenhabAPIManager(APIManager):
    def __init__(self):
        super().__init__(config["OPENHAB"]["host"], config["OPENHAB"]["port"])

    def get_thing_type(self,type_id):
        logger.info("get thing type from OpenHAB")
        return self.get("/rest/thing-types/{id}".format(id=type_id)).json()
        
    def get_things(self):
        logger.info("get things from OpenHAB")
        return self.get("/rest/things").json()

    def get_item(self,item):
        logger.info("get item from OpenHAB")
        return self.get("/rest/items/{item}".format(item=item)).json()

    def getItemState(self,item):
        logger.info("get item state from OpenHAB")
        return self.get("/rest/items/{item}/state".format(item=item)).text

    def get_thing(self, device_id):
        logger.info("get thing from OpenHAB")
        return self.get("/rest/things/{device_id}".format(device_id=device_id)).json()

class PlatformAPIManager(APIManager):
    def __init__(self):
        super().__init__(config["PLATFORM"]["host"], config["PLATFORM"]["port"], config["PLATFORM"]["iot_repo_path"], config["PLATFORM"]["scheme"])
        self.keycloak_manager = KeycloakAPIManager()

    def create_type(self,payload):
        logger.info("create device type on platform")
        return self.post("/deviceType", payload, {"Authorization": "Bearer " + self.keycloak_manager.get_access_token()}).json()

    def get_device_type(self,id):
        logger.info("get device type on platform")
        return self.get("/deviceType/{id}".format(id=id), {"Authorization": "Bearer " + self.keycloak_manager.get_access_token()}).json()
    
    def get_device_types_with_service(self, services):
        logger.info("get device types with match to provided services")
        return self.post("/query/service", services, {"Authorization": "Bearer " + self.keycloak_manager.get_access_token()}).json()

class KeycloakAPIManager(APIManager):
    def __init__(self):
        super().__init__(config["KEYCLOAK"]["host"], config["KEYCLOAK"]["port"], "", config["KEYCLOAK"]["scheme"])

    def get_access_token(self):
        payload = {
            "grant_type": "password",
            "username": config["KEYCLOAK"]["username"],
            "password": config["KEYCLOAK"]["password"],
            "client_id": config["KEYCLOAK"]["client_id"]
        }
        response = self.post("/auth/realms/master/protocol/openid-connect/token", payload).json()
        return response.get("access_token")

class DeviceAPIManager():
    def get_item(self,item):
        return requests.get("{item}".format(item=item))
