# lupus-hue

## Steuere Philips Hue Lichter über die LUPUS XT2+ Alarmanlage!

Die LUPUS XT2+ Alarmanlage bietet eine Reihe von Home Automation Regeln, um verschiedene Aspekte eines intelligenten Heims
zu steuern. Unter anderem ist es möglich Lichter oder andere Verbraucher über die Unterputzrelais oder die Funksteckdosen 
zu schalten. Das ist eine schöne Möglichkeit für die Simulation einer Anwesenheit durch Lichter wenn die Anlage scharf
gestellt wird. 

Wer jedoch bereits intelligente LED-Lichter von Philips im Einsatz hat oder mit den von LUPUS gebotenen Möglichkeiten der
Lichtsteuerung nicht weiterkommt, für den bietet sich mit diesem Projekt die Möglichkeit, Hue- und kompatible Lampen 
von der LUPUS XT-Anlage aus zu steuern.

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

## Features & Anwendungsfälle

lupus-hue hat folgende Features:

+ Räume (Groups) oder Lichter ein- und ausschalten
+ Setzen von Helligkeit, Farben oder Lichttemperatur für Räume (Groups) oder einzelne Lichter
+ Erstellen und Aufrufen von Szenen (verschiedene Einstellungen für die Lichter eines Raums)
+ Setzen von Timern für das Ein- und Ausschalten (entspricht der "Einschalten für"-Aktion von LUPUS allerdings zusätzlich mit einem "Ausschalten für")
+ Loops für Effekte (z.B. für die Signalisierung eines Zustands oder bei Alarm)

Typische Anwendungsfälle:

+ Lichter bei Dämmerung einschalten wenn Anlage scharf
+ Lichter abends automatisch ausschalten oder Nachtlichtmodus aktivieren (Dimmung)
+ Verschiedene Lichtemperaturen für verschiedene Tageszeiten setzen
+ Lichter ausschalten, wenn es außen hell genuug ist (immer oder nur in einem bestimmten Zustand der Anlage)
+ Lichter für eine definierte Zeit einschalten bei Bewegung (gemeldet über einen LUPUS Bewegungsmelder)
+ Lichter einschalten oder blinken lassen, wenn Alarm ausgelöst wird
+ Scharfschaltungszustand der Anlage bei Betreten des Hauses über Farbe eines Lichtes signalisieren 

## Installation & Setup

### 1. Programm auf Raspberry Pi kopieren

Die Dateien lupus-hue.py und lupus-hue.conf müssen in ein beliebiges Verzeichnis auf dem Raspberry Pi kopiert werden.
Der Webservice, der die Lichtsteuerung übernimmt, muss mit dem python-Interpreter in Version 3.4 (nicht v2.x)
aufgerufen werden:

![screenshot server start](public/img/server2.png "Screenshot Server-Start")

Der lupus-hue Server sucht im lokalen Netzwerk nach der Philips Hue Bridge. Wird diese gefunden, wird die IP-Adresse in die
Konfigurationsdatei lupus-hue.conf übernommen. Sollte die Bridge micht automatisch gefunden werden, kann diese auch händisch
in der Konfigurationsdatei eingetragen werden. Nach dem Entdecken der Bridge muss dort der Link-Button gedrückt werden, damit
der Server gegenüber der Bridge autorisiert wird. Der User-Token wird ebenso in der Konfigurationsdatei gespeichert.

Der lupus-hue Server startet unter Port 8000. Dies kann ebenso in der Konfigurationsdatei verändert werden. Alle weiteren
Einträge lupus-hue.conf werden erst für weitergehende Funktionen benötigt und können zunächst ignoriert werden.

### 2. Action-URLs auf der LUPUS XT2+ konfigurieren

Der lupus-hue Webservice auf dem Raspberry Pi wird über einen HTTP Get-Request aufgerufen:

http://ip_des_raspi:8000/kommando?param1=wert1_param2=wert2

Für ip_des_raspi ist die reale IP-Adresse des Raspberry Pi einzusetzen (also z.B. 192.168.0.111). Der Router im Heimnetz
muss so konfiguriert sein, dass dem Raspberry Pi immer dieselbe IP-Adresse zugewiesen wird.

Bei einer Fritz!-Box und anderen Routern kann der Raspberry auch über einen Namen angesprochen werden. Z.B.:

http://pi:8000/kommando?param1=wert1_param2=wert2

Nun können Aufrufe an den lupus-hue Server als "Action-URL" Aktionen in den Home Automation-Regeln genutzt werden. Hier
ein einfaches Beispiel für das Schalten des Lichtes 

![ha regel](public/img/regel2.png "Home Automation Regel")

Wird (durch einen Bewegungsmelder) ein Sensor-Event ausgelöst UND ist der Lux-Wert, der vom Lichtsensor gemeldet wird, 
unter 8, dann wird im Raum "Flur" für 60 Sekunden des Licht eingeschaltet.

### 3. Philips Hue

Ich habe dieses Programm ausschließlich mit der Standard Hue App von Philips getestet. Grundsätzlich müsste lupus-hue aber
auch mit Apps von Dritten zusammen arbeiten.

Es sollten alle Räume - in der Philips Hue API heißen diese Gruppen bzw. Groups - und Lichter über die App eingerichtet
werden. Wenn hier von Gruppe die Rede ist, kann synonym auch Raum benutzt werden.

Über lupus-hue können die Farbwerte nach dem Hue/Sat-Schema und Weißtöne nach der Farbtemperatur (color temperatur)
eingestellt werden.

Siehe dazu: https://www.developers.meethue.com/documentation/core-concepts

Für die Nutzung von Szenen siehe Kapitel "Szenen".

## Das Web-API

Hier wird zunächst das Web-API des lupus-hue Webservice erläutert, bevor weiter unten die praktischen Beispiele in
Verbindung mit der LUPUS Anlage erklärt werden.

Im Folgenden werden die verschiedenen Kommandos für den Webservice erklärt:

### Kommando "info" - Informationen zu Lichtern oder Gruppen (Räumen) ausgeben

#### http://pi:8000/info?g=group

Gib Informationen zur Gruppe (Raum) "group" aus.

#### http://pi:8000/info?l=light

Gib Informationen zu Licht "light" aus. light ist die *Nummer* des Lichtes. Die Lichter eines Raumes können mit 
info?g=group ermittelt werden.

### Kommando "on" - Einschalten eines Lichtes oder einer Gruppe

#### http://pi:8000/on?g=group[_t=seconds][_b=bri]

Schalte die Gruppe (Raum) group ein und setze ggf. einen Timer bzw. verzögere die Einschaltung.

+ _t=seconds  Setze einen Timer von seconds Sekunden, nach denen das Licht / die Gruppe wieder ausgeschaltet wird.
+ _b=bri      Setze die Helligkeit auf bri (0 .. 254)

Beispiele:

+ http://pi:8000/on?g=Flur_b=200_t=180

Schaltet die Lichter im Raum "Flur" für 180 Sekunden ein und setzt die Helligkeit auf 200 (von 254).

+ http://pi:8000/on?g=all

Schalte alle Lichter ein, sobald der Lux Level am Lichtsensor auf 6 gesunken ist.

#### http://pi:8000/on?l=light[_t=seconds]

Wie oben aber für das Licht light.

#### http://pi:8000/on?g=group_h=hue_s=sat[_b=bri][_t=seconds]

Schalte die Gruppe (Raum) "group" ein und setze Farbe und Farbsättigung.

+ _h=hue      Setze den "hue" Wert des Lichts / des Raums auf hue (siehe Kapitel "Farben"). 
+ _s=sat      Setze die Sättigung aus sat.
+ Andere Parameter wie oben

#### http://pi:8000/on?l=light_h=hue_s=sat[_b=bri][_t=seconds]

Wie oben aber für das Licht "light".

Beispiel:

+ http://pi:8000/on?l=10_h=21986_s=253

Schaltet das Licht 10 ein und setzt einen tiefgrünen Farbton.

#### http://pi:8000/on?g=group_c=coltemp[_b=brightness][_t=seconds]

Schalte die Lichter der Gruppe (Raums) group ein und setze die Farbtemperatur auf coltemp. Andere Parameter wir oben. 
Siehe auch Kapitel "Farben".

#### http://pi:8000/on?l_light_c=coltemp[_b=brightness][_t=seconds]

Schalte das Licht light ein und setze die Farbtemperatur auf coltemp. Andere Parameter wir oben.

#### http://pi:8000/on?g=group_n=scene[_t=seconds]

Aktiviere die Szene "scene" für Gruppe (Raum) "group". Andere Parameter wie oben.

Zu Szenen siehe auch unten stehendes Kapitel "Szenen".

### Kommando "off" - Schalte Licht oder Raum aus

#### http://pi:8000/off?g=group[_t=seconds]

Schalte Raum (Gruppe) "group" aus.

+ _t=seconds  Setze einen Timer von "seconds" Sekunden, nach dem die Gruppe wieder eingeschaltet(!) wird.

#### http://pi:8000/off?l=light[_t=seconds]

Schalte Licht "light" aus.

### Kommando "loop" - Erzeuge eine Loop

#### http://pi:8000/loop?g=group_n=scene_t=seconds

Mit Hilfe einer Loop können verschiedene Lichter für einen definierten Zeitraum blinken und dann in einen Endzustand
übergehen. 
Es werden nur die Lichter verändert, die sowohl in Gruppe group als auch in Szene scene enthalten sind. scene steht als
Platzhalter für die Szenen scene1, scene2 und scene3. Während der Loop wird zwischen den Szenen scene1 und scene2 
im Sekundentakt gewechselt (geblinkt). Nach Beendigung der Loop wird die Szene scene3 aktiviert.

Siehe auch das  Kapitel "Szenen".

## Fortgeschrittene Konzepte

### Szenen

### Loops

### Raum-Listen

An jeder Stelle an der in der obigen API-Beschreibung die Nennung eines Raumes möglich ist, der in der Hue Bridge angelegt
sein muss,
kann auch ein "Meta-Raum" angegeben werden. Das sind Listen von Räumen, die in der Konfigurationsdatei lupus-hue.conf hinterlegt werden
können.

Meta-Räume dienen der Reduktion der nötigen Home Automation Regeln in der LUPUS XT-Anlage. Beispiel:

In der Hue Bridge wurden die Räume "Wohnzimmer", "Flur" und "Kueche" angelegt. Es wird nun der Meta-Raum "Erdgeschoss" angelegt, der 
als "Wohnzimmer" + "Flur" + "Kueche" definiert wird.

Nun kann in jedem Kommando "Erdgeschoss" als Gruppe bzw. Raumname genutzt werden und damit die Steuerung aller Lichter in den
drei eigentlichen Räumen gesteuert werden. 

Der Raum "all" steht für alle Lichter, die in der Bridge angelegt sind. "all" wird auf die vordefinierte Hue Gruppe "0" abgebildet.

Die Konfiguration für Meta-Räume in der lupus-hue.conf sieht wie folgt aus:

xxx 


## Quellen
