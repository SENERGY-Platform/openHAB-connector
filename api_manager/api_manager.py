import requests 
import configparser
import os
dir = os.path.dirname(__file__)
filename = os.path.join(dir, '../config.ini')
config = configparser.ConfigParser()
config.read(filename)
print(config.sections())


class APIManager():
    def __init__(self, ip, port, base_path=""):
        self.ip = ip 
        self.port = port 
        self.base_path = base_path
    
    def get(self, path, headers=None):
        response = requests.get("http://{ip}:{port}{base_path}{path}".format(ip=self.ip, port=self.port,base_path=self.base_path,path=path), headers=headers)
        return response.json()

    def post(self, path, payload, headers=None):
        url = "http://{ip}:{port}{base_path}{path}".format(ip=self.ip, port=self.port,base_path=self.base_path,path=path)
        response = requests.post(url,data=payload, headers=headers)
        return response

class OpenhabAPIManager(APIManager):
    def __init__(self):
        super().__init__(config["OPENHAB"]["host"], config["OPENHAB"]["port"])

    def get_thing_type(self,type_id):
        return self.get("/rest/thing-types/{id}".format(id=type_id))
        
    def get_things(self):
        return self.get("/rest/things")

    def get_item(self,item):
        return self.get("/rest/items/{item}".format(item=item))

    def get_thing(self, device_id):
        return self.get("/rest/things/{device_id}".format(device_id=device_id))

class PlatformAPIManager(APIManager):
    def __init__(self):
        super().__init__(config["PLATFORM"]["host"], config["PLATFORM"]["port"], config["PLATFORM"]["iot_repo_path"])
        self.keycloak_manager = KeycloakAPIManager()

    def create_type(self,payload):
        return self.post("/deviceType", payload, {"Authorization": "Bearer " + self.keycloak_manager.get_access_token()}).json()

    def get_device_type(self,id):
        return self.get("/deviceType/{id}".format(id=id), {"Authorization": "Bearer " + self.keycloak_manager.get_access_token()})
    
    def get_device_types_with_service(self, services):
        return self.post("/query/service", services, {"Authorization": "Bearer " + self.keycloak_manager.get_access_token()}).json()

class KeycloakAPIManager(APIManager):
    def __init__(self):
        super().__init__(config["KEYCLOAK"]["host"], config["KEYCLOAK"]["port"])

    def get_access_token(self):
        payload = {
            "grant_type": "password",
            "username": config["KEYCLOAK"]["username"],
            "password": config["KEYCLOAK"]["password"],
            "client_id": config["KEYCLOAK"]["client_id"],
            "client_secret": config["KEYCLOAK"]["client_secret"]
        }
        return self.post("/auth/realms/master/protocol/openid-connect/token", payload).json().get("access_token")

class DeviceAPIManager():
    def get_item(self,item):
        return requests.get("{item}".format(item=item))
