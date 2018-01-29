from connector_client.connector import client
from connector_client.modules import device_pool
from monitor import monitor
from observer import observer
from executer import executer

if __name__ == "__main__":
    connector_client = client.Client(device_manager=device_pool.DevicePool) 
    
    monitor_openhab = monitor.Monitor()
    monitor_openhab.start()

    observer_openhab = observer.Observer() 
    observer_openhab.start()

    executer_openhab = executer.Executer()
    executer_openhab.start()