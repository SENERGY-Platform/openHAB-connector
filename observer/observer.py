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

import threading, time, json, datetime, configparser, os, logging
from connector_client.client import Client
from connector_client.modules import device_pool
from api_manager import api_manager
from logger.logger import root_logger

logger = root_logger.getChild('observer')

dir = os.path.dirname(__file__)
filename = os.path.join(dir, '../config.ini')
config = configparser.ConfigParser()
config.read(filename)

class Observer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.openhab_api_manager = api_manager.OpenhabAPIManager()
    
    def run(self):
        logger.info("Start observing of values")
        while True:
            time.sleep(int(config["CONNECTOR"]["ping_interval"]))
            logger.debug("get values from devices and push to platform")
            connected_devices = device_pool.DevicePool.devices()

            for device in connected_devices:
                device_json = self.openhab_api_manager.get_thing(device)

                channels = device_json.get("channels")
                for channel in channels:
                    items = channel.get("linkedItems")
                    if items:
                        if len(items) != 0:
                            try:
                                service_response = self.openhab_api_manager.getItemState(items[0])
                                # convert depending on data type
                                if channel.get("itemType") == "Number":
                                    service_response = float(service_response)
                                payload = {
                                    "value": service_response,
                                    "time": datetime.datetime.utcnow().isoformat()
                                }
                                # channel type uid == service id
                                logger.debug("try to publish data from service: " + channel.get("channelTypeUID"))
                                logger.debug("publish data: " + json.dumps(payload))
                                response = Client.event(device, channel.get("channelTypeUID"), json.dumps(payload))
                                logger.debug(response.status)
                            except Exception as ex:
                                logger.error("'{}': {}".format(items[0], ex))
