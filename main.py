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