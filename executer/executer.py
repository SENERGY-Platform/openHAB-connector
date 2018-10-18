"""
   Copyright 2018 InfAI (CC SES)

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

import threading, requests,logging
from connector_client.client import Client
from api_manager import api_manager
from logger.logger import root_logger

logger = root_logger.getChild('executor')

class Executer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.openhab_api_manager = api_manager.OpenhabAPIManager()

    def run(self):
        logger.info("starting executor ...")
        while True:
            message = Client.receive()
            logger.debug(message)
            response = self.get_command(message)
            Client.response(message, response, metadata=None, timeout=10, callback=None, block=True)

    def get_command(self,message):
        print("Got command from platform")
        payload = message.payload 
        thing_id = payload.get('device_url')
        channel_type_uid = payload.get('service_url')
        data = payload.get("protocol_parts")
        if data:
            data = data[0].get("value").strip()

        # GET /thing
        thing = self.openhab_api_manager.get_thing(thing_id)
        for channel in thing.get("channels"):
            # get the matching service instance of the device instance to the service type from the command 
            if channel.get("channelTypeUID") == channel_type_uid:
                # device instance has linked items (= active service instances running on this device instance)
                linked_item_id = channel.get("linkedItems")
                if linked_item_id:
                    linked_item_id = linked_item_id[0]
                    # GET /item and send command
                    item = self.openhab_api_manager.get_item(linked_item_id)
                    print("send data: " + data + "to device link: " + item.get("link"))
                    response = requests.post(item.get("link"),data=data)
                    return response.status_code
                    
        
