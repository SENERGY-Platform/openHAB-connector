from connector_client.connector import client
from connector_client.modules import device_pool
from monitor import monitor
from observer import observer

hab_ip = "openhabianpi"
hab_port = 8080
iot_repo = "http://fgseitsrancher.wifa.intern.uni-leipzig.de:8000/iot-device-repo"

if __name__ == "__main__":
    connector_client = client.Client(device_manager=device_pool.DevicePool) 
    
    monitor_openhab = monitor.Monitor(hab_ip, hab_port,iot_repo)
    monitor_openhab.start()

    observer_openhab = observer.Observer(hab_ip,hab_port) 
    observer_openhab.start()