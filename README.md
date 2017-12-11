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
* OpenHAB channel = service
* OpenHAB item = konkrete REST Schnittstelle zum Channel
* OpenHAB UID = device ID
* OpenHAB item link = service uri

## Device
| OpenHAB                  | Platform        |  
| ------------------------ | --------------- | 
| Thing                    | Device          |
| Thing uid                | Device URI      |
| Thing thingTypeUID       | Device Type URI | 
| Thing label              | Device Name     | 

* Scan auf Device Ebene GET /rest/things
* wenn neues Device gefunden wird -> Prüfe, ob Device Type existiert
* da Platform die Device Type ID erstellt, kann nicht thingTypeUID direkt verwendet werden
* mappping mit bereits erstellten Device Types und openhab typen nötig -> persistent ?
* wenn nicht neuen Device Type anlegen

/rest/things
```
[  
   {  
      "statusInfo":{  
         "status":"ONLINE",
         "statusDetail":"NONE"
      },
      "editable":true,
      "label":"Outdoor",
      "bridgeUID":"netatmo:netatmoapi:df42f736",
      "configuration":{  
         "equipmentId":"02:00:00:20:9d:d0",
         "parentId":"70:ee:50:21:00:3c"
      },
      "properties":{  
         "batteryLow":"4500",
         "batteryMax":"6000",
         "batteryMin":"3600",
         "signalLevels":"90,80,70,60"
      },
      "UID":"netatmo:NAModule1:df42f736:020000209dd0",
      "thingTypeUID":"netatmo:NAModule1",
      "channels":[  
         {  
            "linkedItems":[  
               "netatmo_NAModule1_df42f736_020000209dd0_Temperature"
            ],
            "uid":"netatmo:NAModule1:df42f736:020000209dd0:Temperature",
            "id":"Temperature",
            "channelTypeUID":"netatmo:temperature",
            "itemType":"Number",
            "kind":"STATE",
            "defaultTags":[  

            ],
            "properties":{  

            },
            "configuration":{  

            }
         },
```

## Device Type
| OpenHAB                  | Platform        | 
| ------------------------ | --------------- | 
| Thing thingTypeUID       | Device Type URI | 
| Channel                  | Service         |
| Protocol                 | Standard        |
..

* Channels über GET an /thing-types/{thingTypeUID} erhalten

## Services

| OpenHAB                  | Platform           | 
| ------------------------ | -------------------|   
| Channel                  | Service            |
| Channel channelTypeUID   | Service URI        |
| Channel label            | Service Name       |
| Channel description      | Service Desc.      |
| Channel itemType         | Service Data Type  |

* als Service URI nicht Item Link nehmen, da sich die absolute URI ändern kann, z.b. Hostname vom Pi
* als Service URI nicht Channel UID nehmen, da das die ID der Service Instanz ist, für Device Type wird aber auch Service Type gebraucht

/thing-types/{thingTypeUID}:
```
{
  "channels": [
    {
      "description": "Air Quality in ppm",
      "id": "Co2",
      "label": "CO2",
      "tags": [],
      "properties": {},
      "stateDescription": {
        "pattern": "%d ppm",
        "readOnly": true,
        "options": []
      },
      "advanced": false,
      "typeUID": "netatmo:co2"
    },
```

* Items = Abstraktionsschicht über den physikalischen Things zu standardisierten Anfrage an Things
* jedes Thing bietet Channels an, welche über unique REST endpoint ansprechbar sind 
* z.b Thing Netatmo hat eine "UID", bietet Channel "Temperature" an über:
* zu dem Channel gehört das Item "netatmo_NAModule1_df42f736_020000209dd0_Temperature" über API http://openhabianpi:8080/rest/items/netatmo_NAModule1_df42f736_020000209dd0_Temperature




Item:
```
{  
   "link":"http://openhabianpi:8080/rest/items/netatmo_NAModule1_df42f736_020000209dd0_Temperature",
   "state":"26.60",
   "stateDescription":{  
      "pattern":"%.1f Â°C",
      "readOnly":true,
      "options":[  

      ]
   },
   "type":"Number",
   "name":"netatmo_NAModule1_df42f736_020000209dd0_Temperature",
   "tags":[  

   ],
   "groupNames":[  

   ]
}
```

### Referenz Device Type Request Payload
```
{  
   "device_class":{  
      "id":"iot#74806075-4c2a-47a3-9694-685de26add3d",
      "name":"sensorBinary"
   },
   "vendor":{  
      "id":"iot#a9157959-8967-4d0e-8bfd-af079d821a3d",
      "name":"libelium"
   },
   "services":[  
      {  
         "protocol":{  
            "id":"iot#d6a462c5-d4e0-4396-b3f3-28cd37b647a8",
            "protocol_handler_url":"connector",
            "name":"standard-connector",
            "description":"Generic protocol for transporting data and metadata.",
            "msg_structure":[  
               {  
                  "id":"iot#37ff5298-a7dd-4744-9080-7cfdbda5dc72",
                  "name":"metadata",
                  "constraints":null
               },
               {  
                  "id":"iot#88cd5b0e-a451-4070-a20d-464ee23742dd",
                  "name":"data",
                  "constraints":null
               }
            ]
         },
         "config_parameter":[  

         ],
         "input":[  

         ],
         "output":[  
            {  
               "type":{  
                  "id":"iot#6035e5ac-e7f1-4a3b-816c-00efbc375815",
                  "name":"LIFX-Color-Field",
                  "description":"Field: color",
                  "base_type":"http://www.sepl.wifa.uni-leipzig.de/ontlogies/device-repo#structure",
                  "fields":[  
                     {  
                        "id":"iot#7d4df496-0df0-4323-ba6b-0a0eaf90840d",
                        "type":{  
                           "fields":null,
                           "literal":""
                        }
                     }
                  ],
                  "literal":""
               },
               "msg_segment":{  
                  "id":"iot#88cd5b0e-a451-4070-a20d-464ee23742dd",
                  "name":"data",
                  "constraints":null
               },
               "name":"data type",
               "format":"http://www.sepl.wifa.uni-leipzig.de/ontlogies/device-repo#json",
               "additional_formatinfo":[  
                  {  
                     "field":{  
                        "id":"iot#7d4df496-0df0-4323-ba6b-0a0eaf90840d",
                        "name":"color",
                        "type":{  
                           "id":"iot#c8c36810-c8e0-403e-b00f-187414a84ccd",
                           "name":"text",
                           "description":"text",
                           "base_type":"http://www.w3.org/2001/XMLSchema#string",
                           "fields":null,
                           "literal":""
                        }
                     },
                     "format_flag":""
                  }
               ]
            }
         ],
         "name":"name",
         "description":"beschreibung",
         "service_type":"http://www.sepl.wifa.uni-leipzig.de/ontlogies/device-repo#Sensor",
         "url":"url"
      }
   ],
   "config_parameter":[  

   ],
   "name":"test",
   "description":"test"
}
```

## Item Types
* http://docs.openhab.org/concepts/items.html

### String Typen
* da nur Strings, reicht ein Platform Data Type

Type	Supported Values
IncreaseDecreaseType	INCREASE, DECREASE
NextPreviousType	NEXT, PREVIOUS
OnOffType	ON, OFF
OpenClosedType	OPEN, CLOSED
PlayPauseType	PLAY, PAUSE
RewindFastforwardType	REWIND, FASTFORWARD
StopMoveType	STOP, MOVE
UpDownType	UP, DOWN

### Mapping
| OpenHAB Type  | Description                                       | Values                                     | Platform Type   |
| ------------- | --------------------------------------------------| -------------------------------------------|-----------------|
| Color	        | Color information (RGB)	                    | OnOff, IncreaseDecrease, Percent, HSB      |                 |
| Contact	| Status of contacts, e.g. door/window contacts	    | OpenClose                                  | openhab-string  |
| DateTime	| Stores date and time	                            |                                            |                 |
| Dimmer	| Percentage value for dimmers	                    | OnOff, IncreaseDecrease, Percent           |                 |
| Group	        | Item to nest other items / collect them in groups |	                                         |                 |
| Image	        | Binary data of an image                           |                                            |                 |
| Location	| GPS coordinates	                            | Point                                      | openhab-location|
| Number	| Values in number format	                    | Decimal                                    | opennhab-number  |
| Player	| Allows control of players (e.g. audio players)    | PlayPause, NextPrevious, RewindFastforward |                 |
| Rollershutter	| Roller shutter Item, typically used for blinds    | UpDown, StopMove, Percent                  |                 |
| String	| Stores texts	String                              |                                            |                 |
| Switch	| Switch Item, typically used for lights (on/off)   | OnOff                                      | openhab-string  |

* eigentliche Typen sind die Values z.b. OnOff nicht Switch
* aber auf platform seite ist nur ein Data Type pro Service möglich 
* -> problem z.b. bei service mit farben -> kann OnOff, IncreaseDecrease, Percent und HSB erhalten -> aber nur einer möglich
* -> Lösung: Color Data Typ als JSON mit Properties OnOff, IncreaseDecrease,...

# Notes
* Version 2.2.0 wird benötigt ür netatmo
 


