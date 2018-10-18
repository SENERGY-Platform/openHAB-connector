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

from connector_client.client import Client
from connector_client.modules.device_pool import DevicePool

from monitor import monitor
from observer import observer
from executer import executer
from status_pinger import pinger 
import logging

if __name__ == "__main__":
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    connector_client = Client(device_manager=DevicePool)
    
    monitor_openhab = monitor.Monitor()
    monitor_openhab.start()

    observer_openhab = observer.Observer() 
    observer_openhab.start()

    executer_openhab = executer.Executer()
    executer_openhab.start()

    pinger_openhab = pinger.Pinger()
    pinger_openhab.start()
