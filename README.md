# Requirements
Install OpenHAB
With package manager:
```shell
wget -qO - 'https://bintray.com/user/downloadSubjectPublicKey?username=openhab' | sudo apt-key add -
sudo apt-get install apt-transport-https

echo 'deb https://openhab.jfrog.io/openhab/openhab-linuxpkg unstable main' | sudo tee /etc/apt/sources.list.d/openhab2.list

sudo apt-get update

sudo apt-get install openhab2

sudo systemctl start openhab2.service
sudo systemctl status openhab2.service

sudo systemctl daemon-reload
sudo systemctl enable openhab2.service
```
[As Raspberry Pi Image](http://docs.openhab.org/installation/openhabian.html)
[With Docker:](http://docs.openhab.org/installation/docker.html):
```shell
docker pull openhab/openhab:2.2.0-snapshot-amd64-debian 

sudo useradd -r -s /sbin/nologin openhab
usermod -a -G openhab <user>
mkdir /opt/openhab
mkdir /opt/openhab/conf
mkdir /opt/openhab/userdata
mkdir /opt/openhab/addons
chown -R openhab:openhab /opt/openhab

```

Install the connector script:
You will need Python3 and pip.
```shell
python3 -m virtualenv python3 --python=python3
cd python3
source bin/activate
pip install requests
pip install websockets
git clone 
```

# Run
Run the docker container:
```shell
docker run \
        --name openhab \
        --net=host \
	--tty=true\
        -v /etc/localtime:/etc/localtime:ro \
        -v /etc/timezone:/etc/timezone:ro \
        -v /opt/openhab/conf:/openhab/conf \
        -v /opt/openhab/userdata:/openhab/userdata \
        -v /opt/openhab/addons:/openhab/addons\
        -d \
        --restart=always \
        openhab/openhab:2.2.0-snapshot-armhf-debian
```

Run the connector script:
```shell
python main.py
```

# Mapping OpenHAB to IoT Repository
* OpenHAB thing = device 
* OpenHAB item = service
** but they are linked to things
** have a unique id -> unique rest endpoint
* OpenHAB UID = device ID
* OpenHAB item link = service uri
* OpenHAB thing and item label = device and service name

# Notes
* Version 2.2.0 is needed for Netatmo and Ikea Tradfri binding 
