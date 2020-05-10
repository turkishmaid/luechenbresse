# luechenbresse

Investigatives durchforsten von Textwüsten, um nachvollziehbare und belastbare Informationen zur Medienpräsenz 
von Themen und Begriffen aus dem politischen und gesellschaftlichen Leben zu gewinnen.

## A note to international readers

This module is used to monitor _German_ media presence of various terms and topice, including political
parties. Therefore many parts of the documentation and user dialogs are in German language. In case you
are not fluent in German: never mind, you are not missing anything. That said, ...


## Hintergrund

Lügenpresse, eigentl. **Lüchenbrässe**,...
> ist ein politisches Schlagwort, das polemisch und in herabsetzender Absicht auf mediale Erzeugnisse 
> gerichtet ist [...] Seit Beginn des 21. Jahrhunderts wird der Ausdruck Lügenpresse – zumal in Deutschland – 
> vorrangig von rechtsextremen und rechtspopulistischen, völkischen oder auch fremdenfeindlichen und islamophoben Kreisen 
> verwendet, zunächst von Teilen der Hooligan-Szene, bekannter seit 2014 als Parole bei den von Dresden ausgehenden 
> Pegida-Demonstrationen sowie bei Demonstrationen der AfD. Hier ist sie mit Gewaltdrohungen und Gewalt gegen Journalisten 
> eng verbunden. – [Wikipedia](https://de.wikipedia.org/wiki/Lügenpresse)

Das Modul soll (im Ziel) dafür verwendet werdem, die Medienpräsenz verschiedener Begriffe und Themen,
darunter auch und vor allem Personen des politischen und gesellschaftlichen Lebens und politische Parteien, 
im Zeitverlauf zu verfolgen.

Konkreter Anlass zur Entwicklung war die in den sog. "sozialen" Medien oft aufgestellte Behauptung, 
die rechtsgerichtete und in Teilen rechtsextremistische AfD würde von der sog. "Systempresse" und 
vornehmlich von den öffentloich rechtlichen Medien in Deutschland nur unterrepräsentiert abgebildet,
während Die Grünen "hochgeschrieben" würden.
Es zeigt sich aber rasch, dass auch durch einfache Textanalyse bereits sehr spannende Ergebnisse zu
Medienpräsenz aller möglichen Themen und auch zur Arbeit von Journalismus insgesamt gewonnen werden kann.

Auch wenn bereits der Name dieses Moduls –angelehnt an die sächsische Intonation des gerne gebrauchten Schmähwortes für seriös 
recherchierenden Journalismus– den absolut gerechtfertigten Anschein erweckt, dass die Autor:inn:en derartige 
Schmähbegriffe –und diejenigen, die sie verwenden– zutiefst verachten, versuchen die vorliegenden Algorithmen ihr Bestes, 
um unvoreingenommene Analysen als Grundlage für unangreifbare politische Argumentationen zu liefern.  Dass dies mitunter auch 
für den von den Autor:inn:en ausdrücklich geschätzten und bewunderten seriös recherchierenden Journalismus 
nicht gut ausgeht, liegt in der Natur der Sache, und darf als konstruktive Kritik und Ansporn zur Verbesserung 
verstanden werden.

## Funktionen

### Implementiert

- Monitoring und Download der folgenden RSS-Feeds
  - ZDF heute
  - ARD tagesschau
- Download der in den Feeds referenzierten Artikel als HTML Quelltext
- Halbautomatische Installation der benötigten Datenbanken

### Geplant

- Download historischer Textwüsten (wo vorhanden)
  - ARD tagesschau
- Extraktion des im HTML text verborgenen Informationsinhaltes
- Worthäufigkeits-Analyse pro Medium und Woche
- Begleitende Lieferung von Jupyter Notebooks zur einfachen Erstellung eigener Auswertungen
- freie Inhalte aus weiteren Medien
  - Spiegel
  - Zeit
  - rechte Meinungsblogger
- verbesserte Erkennung von Schlagwörtern (berücksichtigung alternativer Schreibweisen)
- Ermittlung von Stimmungkontext (zustimmende vs. kritische Erwähnungen)

## Installation

**Verwende dieses Modul noch nicht!**

Wir sind gerade dabei, die Paketierung und die Installation zu testen. Wenn du es doch so cool findest, dass du keine
Minute mit Warten verschwenden möchtest, klone das GitHub-Repository und verwende `./reinstall` im Wurzelverzeichnis,
um eine lokale Entwicklerinstallation zu erhalten. Eine funktionsfähige Python-Installation ab Release 3.7 wird 
vorausgesetzt. 

## Verwendung

```sh
# once
pip install luechenbresse
luechenbresse --init

# best planed as cron job to run at least every 3 hrs 
luechenbresse --get_all 
```

Die verwendeten `SQLite` Datenbanken weden in `~/.luechenbresse` angelegt. Wenn du damit nichts anfangen kannst,
ist dieses Modul (noch) nichts für dich.

Schönen Tag noch!