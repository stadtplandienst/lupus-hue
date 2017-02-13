# lupus-hue

## Steuere Philips Hue Lichter über die LUPUS XT2+ Alarmanlage

Die LUPUS XT2+ Alarmanlage bietet eine Reihe von Home Automation Regeln, um verschiedene Aspekte eines intelligenten Heims
zu steuern. Unter anderem ist es möglich Lichter oder andere Verbraucher über die Unterputzrelais oder die Funksteckdosen 
zu schalten. Das ist eine schöne Möglichkeit für die Simulation einer Anwesenheit durch Lichter wenn die Anlage scharf
gestellt wird. 

Wer jedoch bereits intelligente LED-Lichter von Philips im Einsatz hat oder mit den von LUPUS gebotenen Möglichkeiten der
Lichtsteuerung nicht weiterkommt, für den bietet sich mit diesem Projekt die Möglichkeit, Hue- und kompatible Lampen 
von der LUPUS XT-Anlage aus zu steuern.

Dieses Projekt bietet eine generische Web-Schnittstelle, die auch ohne eine LUPUS-Anlage sinnvoll genutzt werden kann. Die meisten
Features sind aber bei dem Versuch, intelligente Lichter aus der Home Automation der LUPUS XT2 zu steuern, entstanden und damit
vermutlich auch für andere LUPUS-Nutzer von Nutzen.

## Voraussetzungen

Folgendes Equipment wird vorausgesetzt:

+ LUPUS XT2+ (getestet mit FW 0.0.2.17)
+ Rapsberry Pi 3 (mit aktuellem Rasbian basierend auf Jessie)
+ Philips Hue Bridge (getestet mit Bridge v2, sollte aber auch mit v1 laufen)
+ Philips Hue oder kompatible Leuchtmittel (z.B. auch Osram Lightify oder innr)

Optional:

+ LUPUS Lichtsensor (für lichtabhängige Steuerung)
+ LUPUS Bewegungsmelder (für bewegungsabhängige Steuerung)
+ OSRAM Lightify Plug (günstige Funksteckdose)
+ Andere Sensoren wie sie in den Home Automation Regeln genutzt werden 

## Features und Anwendungsfälle

lupus-hue hat folgende Features:

+ Räume (Groups) oder Lichter ein- und ausschalten
+ Setzen von Helligkeit, Farben oder Lichttemperatur für Räume (Groups) oder einzelne Lichter
+ Erstellen und Aufrufen von Szenen (verschiedene Einstellungen für die Lichter eines Raums)
+ Setzen von Timern für das Ein- und Ausschalten (entspricht der "Einschalten für"-Aktion von LUPUS allerdings zusätzlich mit einem "Ausschalten für")
+ Loops für Effekte (z.B. für die Signalisierung eines Zustands oder bei Alarm)

Typische Anwendungsfälle im Zusammenspiel mit der LUPUS-Anlage sind:

+ Lichter bei Dämmerung einschalten wenn Anlage scharf
+ Lichter abends automatisch ausschalten oder Nachtlichtmodus aktivieren
+ Verschiedene Lichtemperaturen für verschiedene Tageszeiten setzen
+ Lichter ausschalten, wenn es außen hell genug ist (immer oder nur in einem bestimmten Zustand der Anlage)
+ Lichter für eine definierte Zeit einschalten bei Bewegung (gemeldet über einen LUPUS Bewegungsmelder)
+ Lichter einschalten oder blinken lassen, wenn Alarm ausgelöst wird
+ Scharfschaltungszustand der Anlage bei Betreten des Hauses über Farbe eines Lichtes signalisieren 

## Installation und Setup

### 1. Räume und Lichter mit Philips Hue App konfigurieren

Ich habe dieses Programm ausschließlich mit der Standard Hue App von Philips getestet. Grundsätzlich müsste lupus-hue aber
auch mit Apps von Drittanbietern zusammenarbeiten.

Es sollten alle Räume - in der Philips Hue API heißen diese Gruppen bzw. Groups - und Lichter über die App eingerichtet
werden. _Nach dem Einrichten eines neuen Raums muss lupus-hue neu gestartet werden!_

Über lupus-hue können die Farbwerte nach dem Hue/Sat-Schema und Weißtöne nach der Farbtemperatur (color temperatur)
eingestellt werden. Siehe dazu: https://www.developers.meethue.com/documentation/core-concepts

Für die Nutzung von Szenen siehe Kapitel "Szenen".

### 2. Dateien auf Raspberry Pi kopieren und Programm starten

Das Netzwerk (LAN und/oder WLAN) muss auf dem Raspberry Pi konfiguriert sein. 

Das Python-Programm lupus-hue.py und die Konfigurationsdatei lupus-hue.conf werden in ein beliebiges Verzeichnis auf dem Raspberry 
Pi kopiert. Das Programm kann nun mit dem python-Interpreter in Version 3.4 (nicht v2.x) z.B. so aufgerufen werden:

![screenshot server start](public/img/server2.png "Screenshot Server-Start")

lupus-hue sucht im lokalen Netzwerk nach der Philips Hue Bridge. Wird diese gefunden, wird die IP-Adresse der Bridge in die
Konfigurationsdatei lupus-hue.conf übernommen. Sollte die Bridge nicht automatisch gefunden werden, kann die IP-Adresse auch händisch
in der Konfigurationsdatei eingetragen werden:
```
[Hue]
bridge_ip = 192.168.0.111
```

Anschließend muss der Link-Button gedrückt werden, damit der Server gegenüber der Bridge autorisiert wird. Der User-Token wird ebenso 
in der Konfigurationsdatei gespeichert.

Das Programm lupus-hue startet einen HTTP-Server auf Port 8000. Die Portnummer kann  in der Konfigurationsdatei verändert werden:
```
[HTTP-Server]
port = 8000
```

Alle weiteren Einträge in der Konfigurationsdatei werden erst für weitergehende Funktionen benötigt und können zunächst 
ignoriert werden.

### 3. Home Automation-Regeln in der LUPUS XT2+ konfigurieren

Der lupus-hue Webservice auf dem Raspberry Pi wird über einen HTTP Get-Request aufgerufen:
```
http://pi:8000/kommando?param1=wert1_param2=wert2
```
Für "pi" ist die reale IP-Adresse des Raspberry Pi einzusetzen (also z.B. 192.168.0.111). Der Router im Heimnetz
muss so konfiguriert sein, dass dem Raspberry Pi immer dieselbe IP-Adresse zugewiesen wird. 
Bei einer Fritz!-Box und anderen Routern kann der Raspberry Pi auch über einen Namen angesprochen werden. Z.B.:
```
http://raspberrypi:8000/kommando?param1=wert1_param2=wert2
```
Nun können Aufrufe an den lupus-hue Server als "Action-URL"-Aktionen in den Home Automation-Regeln genutzt werden. Hier
ein einfaches Beispiel für das Schalten des Lichtes (mit den erweiterten Home Automation Bedingungen ab LUPUS-Firmware
0.0.2.17):

![ha regel](public/img/regel2.png "Home Automation Regel")

Wird (z.B. durch einen Bewegungsmelder) das Sensor-Event 1 ausgelöst UND ist der Lux-Wert, der vom Lichtsensor gemeldet wird, 
unter 8, dann wird im Raum "Flur" für 60 Sekunden des Licht eingeschaltet.

Wichtig ist, dass die verschiedenen Parameter jeweils mit einem Unterstrich ("_") getrennt werden!

## Das Web-API

Im Folgenden werden die verschiedenen Kommandos für den Webservice erklärt:

### Kommando "info" - Informationen zu Lichtern oder Gruppen (Räumen) ausgeben

```
http://pi:8000/info?g=group
```
Gibt Informationen zur Gruppe (Raum) "group" aus.

```
http://pi:8000/info?l=light
```
Gibt Informationen zu Licht "light" aus. "light" ist die *Nummer* des Lichtes. Die Lichter eines Raumes können mit 
info?g=group ermittelt werden.

### Kommando "on" - Einschalten eines Lichtes oder einer Gruppe
#### Einfaches Einschalten
```
http://pi:8000/on?g=group[_b=bri][_t=seconds]
```
Schaltet die Gruppe (Raum) "group" ein und setzt ggf. einen Timer.

+ t=seconds  Setze einen Timer von "seconds" Sekunden, nach denen die Gruppe wieder ausgeschaltet wird.
+ b=bri      Setze die Helligkeit auf "bri" (0 .. 254)

Beispiele:
```
http://pi:8000/on?g=Flur_b=200_t=180
```
Schaltet die Lichter im Raum "Flur" für 180 Sekunden ein und setzt die Helligkeit auf 200 (von 254).

```
http://pi:8000/on?l=light[_b=bri][_t=seconds]
```
Wie oben aber für das Licht "light".

#### Einschalten und Setzen der Farbe
```
http://pi:8000/on?g=group_h=hue_s=sat[_b=bri][_t=seconds]
```
Schaltet die Gruppe (Raum) "group" ein und setzt Farbe und Farbsättigung.

+ h=hue      Setze den "hue"-Wert des Lichts / des Raums 
+ s=sat      Setze die Sättigung auf "sat".
+ Andere Parameter wie oben

```
http://pi:8000/on?l=light_h=hue_s=sat[_b=bri][_t=seconds]
```
Wie oben aber für das Licht "light".

Beispiel:
```
http://pi:8000/on?l=10_h=21986_s=253
```
Schaltet das Licht 10 ein und setzt einen tiefgrünen Farbton.

#### Einschalten und Setzen der Farbtemperatur
```
http://pi:8000/on?g=group_c=coltemp[_b=brightness][_t=seconds]
```
Schaltet die Lichter der Gruppe (Raums) "group" ein und setzt die Farbtemperatur auf "coltemp" (ein Wert zwischen 153 = sehr
kalt und 500 = sehr warm). Andere Parameter wir oben. 

```
http://pi:8000/on?l_light_c=coltemp[_b=brightness][_t=seconds]
```
Schaltet das Licht "light" ein und setzt die Farbtemperatur auf "coltemp". Andere Parameter wir oben.

#### Aktivieren einer Szene
```
http://pi:8000/on?g=group_n=scene[_t=seconds]
```
Aktiviert die Szene "scene" für Gruppe (Raum) "group". Andere Parameter wie oben.

Zu Szenen siehe auch unten stehendes Kapitel "Szenen".

### Kommando "off" - Ausschalten von Licht oder Raum

```
http://pi:8000/off?g=group[_t=seconds]
```
Schaltet Raum (Gruppe) "group" aus.

+ t=seconds  Setze einen Timer von "seconds" Sekunden, nach dem die Gruppe wieder eingeschaltet(!) wird.

```
http://pi:8000/off?l=light[_t=seconds]
```
Schaltet Licht "light" aus.

### Kommando "loop" - Erzeuge eine Loop

```
http://pi:8000/loop?g=group_n=scene_t=seconds
```

Mit Hilfe einer Loop können verschiedene Lichter für einen definierten Zeitraum blinken und dann in einen Endzustand
übergehen. Siehe auch das  Kapitel "Loops".

## Szenen

Anders als in der Hue App, werden Szenen bei lupus-hue nicht fest einem Raum / einer Gruppe zugeordnet. Beim Aufrufen
einer Szene muss jedoch ein Raum angegeben werden. Es werden dann nur diejenigen Lichter verändert, die sowohl in der Gruppe
als auch in der Szene aufgeführt sind. Als Gruppe kann "all" für alle Lichter verwendet werden.

In der Konfigurationsdatei (lupus-hue.conf) werden zunächst Lichtzustände konfiguriert. Dazu wird ein Abschnitt
[Lightstates] angelegt. Jedem Zustand wird eine Liste von Eigenschaften gemäß der Hue API Beschreibung zugeordnet.

Dabei können die folgenden Keys benutzt werden:
- bri: Brightness (Wert zwischen 0 = aus und 254 = hell)
- hue: Farbe (gemäß Hue Farbschema)
- sat: Sättigung (Wert zwischen 0 und 254)
- ct: Farbtemperatur (Wert zwischen 153 = kalt und 500 = warm)
- transitiontime: Wert in Zehntelsekunden für die Übergänge zwischen den Zuständen
- on: True -> ein, False -> aus

Beispiel (in lupus-hue.conf):
```
[LIGHTSTATES]
on = on:True
off = on:False
red = on:True hue:64866 sat:254 bri:254
neutral = on:True ct:220 bri:254
```
Nun können Szenen definiert werden, die auf die Lichtzustände verweisen. Dazu wird ein Abschnitt [Scenes] angelegt, der
die Szenen aufführt und jeweils Zustände mit Lichtern verbindet.

Beispiel (in lupus-hue.conf):
```
[Scenes]
scene1 = cold:3,4
scene2 = red:2,3 off:4
```

Wenn die Gruppe (Raum) "Flur" nun aus den Lichtern 2, 3 und 4 besteht, bewirkt der Aufruf:
```
http://ip:8000/on?g=Flur_n=scene2
```
dass im FLur die Lichter 2 und 3 rot und Licht 4 ausgeschaltet wird.

## Loops

Eine Loop besteht aus zwei Szenen, zwischen denen im Sekundentakt hin- und hergeschaltet wird, sowie einer Gruppe, die den
Zustand nach Beendigung der Loop beschreibt. Diese werden jeweils mit einem einheitlichen Szenennamen und einer angehängten
"1" (erster Wechselzustand), "2" (zweiter Wechselzustand) bzw. "3" (Endezustand) in der Konfigurationsdatei
angelegt.

Es sind z.B. folgende Szenen definiert:
```
[Scenes]
alarm1 = red:1,2,3,4
alarm2 = cold:1,2,3,4
alarm3 = off:1,2,3,4
```
Jetzt kann mit folgendem Kommand eine Loop z.B. als Alarmsignalisierung für 2 Minuten gestartet werden, die zwischen Rot und
kaltem Weiss wechselt und danach alle Lichter ausschaltet:
```
http://pi:8000/loop?g=all_n=alarm_t=120
```

## Raum-Listen

An jeder Stelle an der in der obigen API-Beschreibung die Nennung einer Gruppe bzw. eines Raumes mit dem Parameter g=group
möglich ist, kann auch eine benannte Liste an Räumen angegeben werden, die zuvor in der Konfigurationsdatei hinterlegt
wurden. Diese Listen dienen zur Reduktion der nötigen Home Automation Regeln in der LUPUS XT-Anlage. 

Beispiel:
```
[Groups]
WF = ('Wohnzimmer', 'Flur',)
FK = ('Flur','Keller')
SZ = ('Schlafzimmer',)
```
Mit g=WF können werden Aktionen jetzt für beide Gruppen/Räume "Wohnzimmer" und "Flur" ausgeführt. Wie mit dem Beispiel "SZ"
kann man diesen Mechanismus auch benutzen um Abkürzungen für die Namen von Gruppen/Räumen einzuführen. Wichtig ist dabei
aber das Komma nach dem Raumnamen.

## Quellen

- Philips Hue API Core Concepts: https://www.developers.meethue.com/documentation/core-concepts
- SSDP Discovery: https://gist.github.com/dankrause/6000248
