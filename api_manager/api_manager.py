"""
   Copyright 2018 SEPL Team

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import requests, configparser, os
from logger.logger import root_logger

dir = os.path.dirname(__file__)
filename = os.path.join(dir, '../config.ini')
config = configparser.ConfigParser()
config.read(filename)

logger = root_logger.getChild('api_manager')

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
        logger.debug("get thing type from OpenHAB")
        return self.get("/rest/thing-types/{id}".format(id=type_id)).json()
        
    def get_things(self):
        logger.debug("get things from OpenHAB")
        return self.get("/rest/things").json()

    def get_item(self,item):
        logger.debug("get item from OpenHAB")
        return self.get("/rest/items/{item}".format(item=item)).json()

    def getItemState(self,item):
        logger.debug("get item state from OpenHAB")
        return self.get("/rest/items/{item}/state".format(item=item)).text

    def get_thing(self, device_id):
        logger.debug("get thing from OpenHAB")
        return self.get("/rest/things/{device_id}".format(device_id=device_id)).json()

class PlatformAPIManager(APIManager):
    def __init__(self):
        super().__init__(config["PLATFORM"]["host"], config["PLATFORM"]["port"], config["PLATFORM"]["iot_repo_path"], config["PLATFORM"]["scheme"])
        self.keycloak_manager = KeycloakAPIManager()

    def create_type(self,payload):
        logger.debug("create device type on platform")
        return self.post("/deviceType", payload, {"Authorization": "Bearer " + self.keycloak_manager.get_access_token()}).json()

    def get_device_type(self,id):
        logger.debug("get device type on platform")
        return self.get("/deviceType/{id}".format(id=id), {"Authorization": "Bearer " + self.keycloak_manager.get_access_token()}).json()
    
    def get_device_types_with_name(self, payload):
        logger.debug("get device types with match on name")
        return self.post("/query/deviceType", payload, {"Authorization": "Bearer " + self.keycloak_manager.get_access_token()}).json()

    def get_device_types_with_service(self, services):
        logger.debug("get device types with match to provided services")
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
