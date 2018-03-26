import os,sys,inspect
import_path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0],"connector-client")))
if import_path not in sys.path:
    sys.path.insert(0, import_path)

from connector import client
from connector import modules
from monitor import monitor
from observer import observer
from executer import executer
from status_pinger import pinger 


if __name__ == "__main__":
    connector_client = client.Client(device_manager=modules.DevicePool) 
    
    monitor_openhab = monitor.Monitor()
    monitor_openhab.start()

    observer_openhab = observer.Observer() 
    observer_openhab.start()

    executer_openhab = executer.Executer()
    executer_openhab.start()

    pinger_openhab = pinger.Pinger()
    pinger_openhab.start()