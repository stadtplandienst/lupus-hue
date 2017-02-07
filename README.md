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

+ _l=light    Nummer des Lichtes 
+ _g=group    Name des Raumes wie in der Hue App gesetzt oder der Name eines "Pseudo-Raums" wie unten beschrieben.
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

http://ip_des_raspi:8000/on?l=light_h=hue_s=sat][_b=bri][_t=seconds][_d=1_x=lux]

Wie oben aber für das Licht light.

http://ip_des_raspi:8000/on?{g=group|l=light}[_t=seconds][_d=1_x=lux][_h=hue][_c=coltemp][_b=brightness]
Parameter:
+ _c=coltemp  Setze die Farbtemperatur auf coltemp. Schließt sich mit hue / sat aus.
+ Andere Parameter wie oben

http://ip_des_raspi:8000/on?g=group_n=scene[_t=timer][_d=deferred_x=lux_level]
Parameter:
+ _n=scene  Aktiviere die Szene scene für.
+ Andere Parameter wie oben
            #
            #       switch group on an optionally set timer or defer
            #
            # off: switch group or light off
            #
            #   off?{g=group|l=light}[_t=timer]
            #
            #       switch group|light off and optionally set timer (to switch back on)
            #
            # info: get info on groups, lights
            #
            #   info?{g=group|l=light}
            #
            # lux: set lux level
            #
            #   lux?x=lux_level
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
