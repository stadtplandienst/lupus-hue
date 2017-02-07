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

### Begrifflichkeiten

Räume werden in der Notation des Phlips Hue API als "Groups" (Gruppen) bezeichnet. 

### HTTP-Request

Der lupus-hue Webservice wird über einen HTTP Get-Request aufgerufen:

http://<ip_des_raspi>:8000/<kommando>?<param1>=<value1>_<param2>=<value2>

Im Folgenden werden die verschiedenen Kommandos erklärt:

### on: Lichter oder Räume ein und Ausschalten

on?g=<group>|l=<light>}[_t=timer][_d=deferred][_h=hue][_s=sat][_b=brightness]
switch group|light on an set hue/sat, optionally set timer or defer

on?{g=group|l=light}[_t=timer][_d=deferred][_c=colortemp][_b=brightness]
            #
            #       switch on group|light on an set color temperature, optionally set timer or defer
            #
            #   on?g=group[_t=timer][_d=deferred_x=lux_level][_n=scene]
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
