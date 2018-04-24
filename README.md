# Requirements
Install OpenHAB
[As Raspberry Pi Image](http://docs.openhab.org/installation/openhabian.html)

Install the connector script:
You will need Python3 and pip.
```shell
pip3 install requests
pip3 install websockets 
```

## Config files 
```
[OPENHAB]
host = openhabianpi
port = 8080

[PLATFORM]
scheme = https
host = api.sepl.infai.org
port = 8000
iot_repo_path = /iot-device-repo
number_data_type = iot#2c0f1265-8612-4c57-8bee-894acab7dad2
string_data_type = iot#ae079227-8507-4314-92b6-e1b7eba0a765

[CONNECTOR] 
ping_interval = 10
openhab_monitor_interval = 10

[KEYCLOAK]
scheme = https
host = auth.sepl.infai.org
port = 443
username = username
password = password
client_id = openhabconnector


```

# Value Type Generation
OpenHAB connector wraps the the values from openHAB in a JSON format.  
{
"value": 20.0,
"time": "2018-2-2"
}

Because it always JSON, we can generate the needed ValueTypes automatically 

# Run
Run the connector script:
```shell
cd openhabconnector
python3 main.py
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
* hauptunterschied zwischen SEPL und openhab:
* SEPL definerit Deivce Types und Service Types
* SEPL geht davon aus, dass Service URIs unabhängig von der Device Instanz sind
* z.b service location bei Typ smartphone
* jede geräte instanz verwendet location als service uri
* service uri device type = service uri device instance

* openhab definiert service uris abhängig von der device instanz
* openhab definert aber auch device unabhängige service uri
* da aber service uri bei device typ angegeben werden muss und nicht bei Device Erstellung, muss im Gateway irgendwie vom allgemeinen service uri auf die des geräts 

* services bei openhab sind auf device instanz
* zztl. kann service aktiviert oder deaktiviert sein -> im UI muss channel explizit "gelinked" werden
* in der Platform können dadurch Services vom Device Type angezeigt werden, welche nicht auf der Device Instanz ausgeführt werden können


* Openhab hat 1:n Beziehung bei Datentypen zu Service
* Service hat zwar nur ein Item Type wie "Dimmer" aber der kann verschiedene Datentypen haben, z.b 50%, "ON"
* SEPL hat 1:1 Beziehung bei Datentypen 

# Pinger 
- prüft, ob die Devices aus dem DevicePool (Memory Speicher) noch online sind
- falls disconnected, wird das device aus dem DevicePool entfertn und auf der Platfor disconnected (Client.disconnect())
- falls das Device wieder online ist, wird es wieder zur Platform hinzugefügt (Client.add()), geschieht auch, wenn das Gerät schon online ist, da im DevicePool nicht bekannt ist, ob das Device online oder offline ist 
- Ping Intervall ist konfigurierbar 

# Config

# Auto Start
/etc/rc.local

# Troubleshooting
- if you miss a service, it could be that you have to activate (=link) the channel in openhab
- some channels are not linked by default (missing dot)


# TODO
- config file für urls, value type ids 
- leerzeichen entfernen bei service name, service id ...
 


git clone --recurse-submodules

