import requests 

class APIManager():
    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip 
        self.port = port 
    
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