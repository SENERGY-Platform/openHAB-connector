import requests 

hab_ip = "openhabianpi"
hab_port = 8080
platform_ip = "fgseitsrancher.wifa.intern.uni-leipzig.de"
platform_port = 8000
iot_repo_path = "/iot-device-repo"


class APIManager():
    def __init__(self, ip, port, base_path=""):
        self.ip = ip 
        self.port = port 
        self.base_path = base_path
    
    def get(self, path):
        response = requests.get("http://{ip}:{port}{base_path}{path}".format(ip=self.ip, port=self.port,base_path=self.base_path,path=path))
        return response.json()

    def post(self,path,payload):
        url = "http://{ip}:{port}{base_path}{path}".format(ip=self.ip, port=self.port,base_path=self.base_path,path=path)
        response = requests.post(url,data=payload)
        return response.json()

class OpenhabAPIManager(APIManager):
    def __init__(self):
        super().__init__(hab_ip, hab_port)

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
        super().__init__(platform_ip, platform_port, iot_repo_path)

    def create_type(self,payload):
        return self.post("/deviceType",payload)

    def get_device_type(self,id):
        return self.get("/deviceType/{id}".format(id=id))

    def get_device_types_with_service(self, services):
        return self.post("/query/service", services)

class DeviceAPIManager():
    def get_item(self,item):
        return requests.get("{item}".format(item=item))
