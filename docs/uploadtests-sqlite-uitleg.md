# Uitleg: uploadtests met SQLite

De integratietests voor het uploaden van personen, cases en samples draaien nu op twee soorten opslag: DICT en SQLite. SQLite controleert meer regels van de database. Daardoor kunnen de tests fouten in verwijzingen en andere databasebeperkingen eerder vinden.

Deze wijziging gaat over de tests en hun testgegevens. De werking van de productiecode en de HTTP-endpoints is niet aangepast.

## Waarom was dit nodig?

De meeste uploadtests gebruikten DICT: opslag in Python-geheugen. DICT is handig voor snelle tests, maar controleert geen databasebeperkingen zoals:

- **Foreign keys:** een verwijzing moet naar een bestaande rij wijzen. Een persoon kan bijvoorbeeld verwijzen naar een concept dat in de database moet bestaan.
- **Unieke waarden:** bepaalde waarden mogen niet dubbel voorkomen.
- **Verplichte kolommen:** sommige kolommen mogen niet leeg zijn.

In productie gebruikt de applicatie SQL Server. Die database controleert deze regels wel. Daardoor kon een test op DICT slagen, terwijl dezelfde gegevens in productie werden afgewezen.

SQLite controleert een groot deel van deze regels ook. De applicatie schakelt de controle van foreign keys in voor elke SQLite-verbinding. De tests geven daarom meer vertrouwen dat de opgeslagen gegevens aan de databasebeperkingen voldoen. SQLite is wel een andere database dan SQL Server en vangt niet elk SQL Server-probleem af.

## Hoe draaien de tests nu?

De actieve uploadtests gebruiken nu combinaties uit `_PARAMS`. Elke combinatie beschrijft welke opslag wordt gebruikt en of de test via een HTTP-endpoint gaat. Dit volgt het bestaande patroon met `BuildDbParams`.

| Tests | DICT | SQLite |
| --- | --- | --- |
| OMOPDB: personen en itemfouten | Via HTTP | Rechtstreeks via de applicatie |
| OMOPDB: nieuwe objecten overslaan | Rechtstreeks via de applicatie | Rechtstreeks via de applicatie |
| CASEDB: itemfouten en verwijderen van inhoud | Rechtstreeks via de applicatie | Rechtstreeks via de applicatie |
| SEQDB: sample-upload | Rechtstreeks via de applicatie | Rechtstreeks via de applicatie |

Bij een rechtstreekse test wordt het uploadcommando aan de applicatie gegeven, zonder HTTP-verzoek. De upload en de opslag worden nog steeds uitgevoerd. De HTTP-laag zelf wordt dan niet getest.

De combinaties hebben leesbare namen, zoals `with_endpoints__DICT_EMPTY` en `skip_endpoints__SA_SQLITE_EMPTY`. Deze namen verschijnen bij de testresultaten. Zo is direct te zien welke uitvoering is geslaagd of mislukt.

Elke combinatie krijgt ook een eigen naam voor de applicatieconfiguratie. De testclient wordt op basis van die naam bewaard en hergebruikt. Verschillende namen voorkomen dat een test per ongeluk de client of database van een andere combinatie gebruikt. De `env`-fixture is per testbestand en combinatie beschikbaar: tests binnen die combinatie delen de ingerichte omgeving.

### HTTP-tests

De SQLite-uitvoeringen gebruiken geen HTTP-endpoint. De bestaande SQLite-opzet werkt niet goed met de threads die de HTTP-testclient gebruikt. Dit is niet opgelost in deze wijziging.

De OMOPDB-tests die specifiek een HTTP-antwoord controleren, worden alleen voor de SQLite-combinatie overgeslagen. Op DICT blijven ze draaien. Het gaat onder meer om de controle op een ongeldige aanvraag en om de inhoud van een fout in het HTTP-antwoord. De andere OMOPDB-uploadtests draaien ook op SQLite.

## OMOPDB: bestaande concepten in plaats van losse ID's

Voorheen gebruikten de person-uploadtests concept-ID's zonder de bijbehorende concepten aan te maken. DICT accepteerde die verwijzingen. SQLite wees ze af wanneer een foreign key werd gecontroleerd.

De gedeelde fixture in [conftest.py](../test/omopdb/integration/person_upload/conftest.py) maakt nu deze gegevens aan:

1. Een domein, een vocabulaire en een conceptklasse.
2. Eén concept dat naar die drie records verwijst.
3. Een uitgever van identificaties voor tests met identifiers.

Het domein, het vocabulaire en de conceptklasse verwijzen zelf naar het concept dat daarna wordt aangemaakt. De fixture gebruikt hetzelfde concept voor de conceptvelden van personen en specimens. Het doel is hier geldige testgegevens te maken, niet verschillende medische concepten na te bootsen.

De gegevens die een test nodig heeft, staan samen in `RefData`, in [ref_data.py](../test/omopdb/integration/person_upload/ref_data.py). De gewone person-uploadtests, de tests voor fouten per persoon en de tests voor overgeslagen nieuwe objecten gebruiken dezelfde fixture. De specimen-ID's en de bijbehorende numerieke concept-ID's zijn op elkaar afgestemd.

De tests voor `on_new=SKIP` draaiden eerder al op SQLite. Ze draaien nu ook op DICT. Ze blijven controleren dat een overgeslagen nieuwe persoon of een nieuw specimen, en de bijbehorende identifiers, niet worden opgeslagen.

## CASEDB: uploaden met een ingebouwde SEQDB

De actieve CASEDB-tests voor fouten per case en voor het verwijderen van case-inhoud draaien nu op beide soorten opslag. De inhoudstest controleert nog steeds dat een waarde die op `None` wordt gezet, echt uit de opgeslagen case verdwijnt.

CASEDB gebruikt in deze tests ook een ingebouwde SEQDB-applicatie. Bij het maken van een lokale client kan de configuratie van die ingebouwde applicatie worden aangepast. Daarom zet de fixture voor elke combinatie de juiste SEQDB-configuratie terug voordat zij de client maakt. Zo krijgt DICT de DICT-configuratie en SQLite de SQLite-configuratie.

Een proef met de actieve CASEDB-uploadtests is op SQLite geslaagd. Een oudere testklasse voor case-upload was al overgeslagen omdat zij is vervangen door unit-tests; die klasse blijft overgeslagen. Ook is een verouderde opmerking in de CASEDB-databasebouwtest aangepast: de code bevat daar namelijk al een SQLite-combinatie.

## SEQDB: zelf referentiegegevens maken

De sample-uploadtests gebruikten eerder de DICT-demodatabase. Ze haalden daar een bestaande sample op om de ID van een datacollectie te vinden. Ook zochten ze bestaande protocollen in de demogegevens. Een lege SQLite-database heeft die gegevens niet.

De nieuwe helper in [ref_data.py](../test/seqdb/integration/upload_samples/ref_data.py) maakt daarom zelf aan:

- een datacollectie;
- een assemblyprotocol voor geldige samples;
- een sequencingprotocol voor de test met een verkeerd protocoltype.

De helper geeft de ID's terug in `SeqUploadRefData`. De [fixture](../test/seqdb/integration/upload_samples/conftest.py) maakt deze gegevens per testomgeving. De helper kan ook worden gebruikt bij toekomstig werk aan sample-upload via HTTP.

De tests beginnen nu op beide opslagsystemen met een lege database. Ze controleren nog steeds wat er gebeurt als één sample een verkeerd protocoltype, een onbekende protocol-ID of een onbekende protocolcode heeft. Bij `fail_batch_on_item_error=False` moeten de geldige samples worden opgeslagen en de ongeldige sample niet. Bij `True` wordt de batch gestopt en wordt geen van die samples opgeslagen.

## Wat blijft buiten bereik?

- SQLite controleert alleen foreign keys die in de gebruikte SQLite-database aanwezig zijn. Diensten gebruiken aparte databasebestanden. Een verwijzing naar een andere dienst wordt daardoor niet altijd met een foreign key gecontroleerd.
- SQL Server-specifieke problemen, zoals de limiet van 2100 parameters, worden hiermee niet getest.
- De bestaande tests voor niet-wijzigbare velden gebruiken mocks: nagebootste onderdelen in plaats van een echte database. Die tests zijn daarom niet simpelweg op SQLite gezet.
- De HTTP-endpoints zijn niet aangepast om met SQLite te werken.

## Uitgevoerde controles

Met Python 3.14 zijn de drie betrokken uploadmappen samen uitgevoerd: **50 tests geslaagd en 4 overgeslagen**. Twee skips zijn HTTP-specifieke OMOPDB-tests bij SQLite; de andere twee horen bij de al overgeslagen oude CASEDB-testklasse.

Ook de CI-achtige testset is uitgevoerd:

```bash
python run.py test_all --include_e2e=False
```

Het resultaat was **6.203 geslaagd en 284 overgeslagen**. De gerichte controles met Black en isort zijn ook geslaagd.

Voor een indicatie van de extra testtijd is dezelfde volledige testset één keer op een schone uitgangssituatie uitgevoerd. De pytest-uitvoering duurde daar 101,61 seconden en met de wijzigingen 92,61 seconden. Deze enkele metingen laten geen meetbare toename zien, maar zijn te gevoelig voor normale verschillen tussen runs om een nauwkeurige CI-tijdwinst of -toename te bepalen.
