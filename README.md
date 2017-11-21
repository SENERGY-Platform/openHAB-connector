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
```shell
virtualenv python3.4 --python=python3.4
cd python3.4
source bin/activate
git clone 
```

# Run
Run the docker container:
```shell
docker run \
        --name openhab \
        --net=host \
        -v /etc/localtime:/etc/localtime:ro \
        -v /etc/timezone:/etc/timezone:ro \
        -v /opt/openhab/conf:/openhab/conf \
        -v /opt/openhab/userdata:/openhab/userdata \
        -v /opt/openhab/addons:/openhab/addons\
        -d \
        -e USER_ID=<uid> \
        -e GROUP_ID=<gid> \
        --restart=always \
        openhab/openhab:2.2.0-snapshot-amd64-debian
```

Run the connector script:
```shell
python main.py
```

# Mapping OpenHAB to IoT Repository
* OpenHAB UID = Device ID
* OpenHAB Label = Device name

# Notes
* Version 2.2.0 is needed for Netatmo and Ikea Tradfri binding 
