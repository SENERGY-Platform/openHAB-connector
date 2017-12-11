Start of script:
1. alle Geräte finden 
2. Typen überprüfen ob auf Platform existent 
(vllt zur runtime speichern, nicht persistent, falls zur runtime zweites Gerät angeschlossen wird)

Runtime:
* Flow wird nur ausgeführt wenn neues Gerät gefunden wird

* nicht nur in DB checken, auch auf platform, da Typ auch wieder gelöscht werden kann
* wenn dann typ wieder angelegt wird, wird auch neu zur DB hinzugefügt, aber Openhab ID existiert schon -> Error 


Todo:
* automatisch get wenn readable wert mit client.event 

* andere daten tyoen neben number hinzufügen 

* command support 
