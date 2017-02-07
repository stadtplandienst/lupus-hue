# lupus-hue

## Steuere Philips Hue Lichter über die LUPUS XT+ Alarmanlage !!

Die LUPUS XT2+ Alarmanlage bietet u.a. auch eine Reihe von Home Automation Regeln, um verschiedene Aspekte eines intelligenten Heims
zu steuern. Unter anderem ist es möglich Lichter oder andere Verbraucher über die Unterputzrelais oder die Funksteckdosen zu schalten.

Das ist eine tolle Funktion für die Simulation einer Anwesenheit wenn die Anlage scharf gestellt wird. Bei einer großen Anzahl von
Lichtern geht das aber schnell ins Geld und hat auch eine Reihe von Einschränkungen:

- Lichter können nur ein- und ausgeschaltet werden (keine Farben, Lichttemperatur, Szenen, Übergänge etc.)
- Das Dimmen mit dem LUPUS Unterputzrelais mit Dimmerfunktion funktioniert zumindest bei mir nicht zufriedenstellend
- Die gegenwärtigen Home Automation Regeln bei LUPUS sind sehr eingeschränkt, insbesondere wenn man Regeln erstellen will, die den
  Lichtsensor abfragen oder den Sonnenstand berücksichtigen

Aus diesem Grund habe ich ein Projekt entwickelt, mit dem eine LUPUS XT2+ mit Hilfe der "Action URL"-Regel Philips Hue (oder kompatible) 
Lichter steuern kann.

## Voraussetzungen

Folgendes Equipment wird vorausgesetzt:
+ LUPUS XT2+
+ Rapsberry Pi 3 (mit Rasbian basierend auf Jessie)
+ Philips Hue Bridge (nur getestet mit v2)
+ Philips Hue oder kompatible Leuchtmittel (z.B. auch Osram Lightify oder innr)

Optional:
+ LUPUS Lichtsensor (für lichtabhängige Steuerung)
+ LUPUS Bewegungsmelder (für bewegungsabhängige Steuerung)
+ OSRAM Lightify Plug (günstige Funksteckdose)
+ Andere Sensoren wie sie in den Home Automation Regeln genutzt werden 

## Features & Anwendungsfälle

lupus-hue hat folgende Features:
+ Räume (Groups) oder Lichter ein- und ausschalten
+ Setzen von Helligkeit, Farben oder Lichttemperatur für Räume (Groups) oder einzelne Lichter
+ Aufrufen von Szenen (verschiedene Einstellungen für die Lichter eines Raums)
+ Setzen von Timern für das Ein- und Ausschalten (entspricht der "Einschalten für" von LUPUS aber auch mit "Ausschalten für")
+ Loops für Effekte (z.B. für die Signalisierung eines Zustands)
+ Ausführen von Kommandos abhängig vom Lux-Wert des Lichtsensors
+ Zeitverzögertes Ausführen von Kommandos bis ein Lux-Wert erreicht ist

Typische Anwendungsfälle:
+ Lichter bei Dämmerung einschalten wenn Anlage scharf
+ Lichter abends automatisch ausschalten oder Nachtlichtmodus aktivieren (Dimmung)
+ Verschiedene Lichtemperaturen für verschiedene Tageszeiten setzen
+ Lichter ausschalten, wenn es außen hell genuug ist (immer oder nur in einem bestimmten Zustand der Anlage)
+ Lichter für eine definierte Zeit einschalten bei Bewegung (gemeldet über einen LUPUS Bewegungsmelder)
+ Lichter einschalten oder blinken lassen, wenn Alarm ausgelöst wird
+ Scharfschaltungszustand der Anlage bei Betreten des Hauses über Farbe eines Lichtes signalisieren 

## Installation & Setup

### Auf dem Raspberry Pi

### Action-URL

### Initiale Home Automationen Regeln für Weitergabe der Lux-Werte aus dem Lichtsensor

Soll der Lichtsensor der LUPUS Anlage für die Steuerung des Lichtes mit genutzt werden, müssen die aktuellen Lux-Werte mit vordefinierten Home Automation Regeln zwischen der LUPUS XT2 und dem Raspberry Pi synchronisiert werden.

Dazu sollten folgende Home Automation Regeln in der XT2 angelegt werden:

+ Wenn Lux zwischen 0 und 5 -> Immer -> Action-URL "$1/lux?x=5
+ Wenn Lux zwischen 6 und 6 -> Immer -> Action-URL "$1/lux?x=6
+ Wenn Lux zwischen 7 und 7 -> Immer -> Action-URL "$1/lux?x=7
+ Wenn Lux zwischen 8 und 8 -> Immer -> Action-URL "$1/lux?x=8
+ Wenn Lux zwischen 9 und 16 -> Immer -> Action-URL "$1/lux?x=9

In meinen Tests haben sich die Lux-Level von 5 ... 9 als in der Praxis relevant erwiesen. Sollten doch mehr Stufen benötigt werden
müssen entsprechende Regeln ergänzt werden. Das Programm lupus-hue kann mit allen Werten zwischen 0 und 16 zurecht kommen.

Zum Start des lupus-heu Webservice wird der Lux-Wert intern auf 0 gesetzt bis zum ersten Mal eine Home Automation Regel des
Lichtsensors auslöst und damit der richtige Wert gesetzt wird. Alternativ kann über einen Browser der Lux-Wert auch zum Testen oder
initial manuell gesetzt werden (siehe weiter unten: Kommando "lux").

## Das Web-API

### Begrifflichkeiten und Konzepte

#### Gruppen bzw. Räume

#### Lichter

Räume werden in der Notation des Phlips Hue API als "Groups" (Gruppen) bezeichnet. 

#### Farbkonzept



### HTTP-Request

Der lupus-hue Webservice wird über einen HTTP Get-Request aufgerufen:

http://<ip_des_raspi>:8000/<kommando>?<param1>=<value1>_<param2>=<value2>

Im Folgenden werden die verschiedenen Kommandos erklärt:

### Kommando "info" - Informationen zu Lichtern oder Gruppen (Räumen) ausgeben

#### http://ip_des_raspi:8000/info?g=group

Gib Informationen zu Gruppe (Raum) group aus.

#### http://ip_des_raspi:8000/info?g=group

Gib Informationen zu Licht light aus. light ist die Nummer des Lichtes. Die Nummern der Lichter eines Raumes kann mit 
info?g=group ermittelt werden.

### Kommando "on" - Einschalten eines Lichtes oder einer Gruppe

#### http://ip_des_raspi:8000/on?g=group[_t=seconds][_d=1_x=lux][_b=bri]

Schalte die Gruppe (Raum) group ein und setze ggf. einen Timer bzw. verzögere die Einschaltung.

+ _t=seconds  Setze einen Timer von seconds Sekunden, nach denen das Licht / die Gruppe wieder ausgeschaltet wird.
+ _d=1_l=lux  Wenn angegeben, wird das Einschalten verzögert, bis der Lux-Level lux oder niedriger erreicht wird.
+ _b=bri      Setze die Helligkeit auf bri (0 .. 254)

Beispiel:

http://192.168.0.111:8000/on?g=Flur_b=200_t=180

Schaltet die Lichter im Raum "Flur" für 180 Sekunden ein und setzt die Helligkeit auf 200.

#### http://ip_des_raspi:8000/on?l=light[_t=seconds][_d=1_x=lux]

Wie oben aber für das Licht light.

#### http://ip_des_raspi:8000/on?g=group_h=hue_s=sat][_b=bri][_t=seconds][_d=1_x=lux]

Schalte die Gruppe (Raum) group ein und setze Farbe und Farbsättigung.

+ _h=hue      Setze den "hue" Wert des Lichts / des Raums auf hue (siehe Philips Hue API). 
+ _s=sat      Setze die Sättigung aus sat.
+ Andere Parameter wie oben

#### http://ip_des_raspi:8000/on?l=light_h=hue_s=sat][_b=bri][_t=seconds][_d=1_x=lux]

Wie oben aber für das Licht light.

#### http://ip_des_raspi:8000/on?g=group_c=coltemp[_b=brightness][_t=seconds][_d=1_x=lux]

Schalte die Lichter der Gruppe (Raums) group ein und setze die Farbtemperatur auf coltemp. Andere Parameter wir oben.

#### http://ip_des_raspi:8000/on?l_light_c=coltemp[_b=brightness][_t=seconds][_d=1_x=lux]

Schalte das Licht light ein und setze die Farbtemperatur auf coltemp. Andere Parameter wir oben.

#### http://ip_des_raspi:8000/on?g=group_n=scene[_t=timer][_d=deferred_x=lux_level]

Aktiviere die Szene scene für Gruppe (Raum) group. Andere Parameter wie oben.

### Kommando "off" - Schalte Licht oder Raum aus

#### http://ip_des_raspi:8000/off?g=group[_t=timer]

Schalte Raum (Gruppe) group aus.

+ _t=seconds  Setze einen Timer von seconds Sekunden, nach denen das Licht / die Gruppe wieder eingeschaltet(!) wird.

#### http://ip_des_raspi:8000/off?l=light[_t=timer]

Schalte Licht light aus.

### Kommando "lux" - Setze Lichtwert aus LUPUS Alarmanlage

#### http://ip_des_raspi:8000/lux?x=level

Setzte den Lux-Level gemäß dem aktuellen Stand 
            #
            #       set lux level to lux_level
            #
            # loop: call loop of scenes
            #
            #   loop?g=group_n=scene_t=timer
            #
            #       Call loop of scenes for group and scene name as defined in init_scenes() for timer seconds
            #
            # init: initialize scenes
            #

## Schreiben der LUPUS Home Automation Regeln

### Einfache Regeln

### Timer 

### Lichtabhängige Steuerung

### Szenen



## Quellen
