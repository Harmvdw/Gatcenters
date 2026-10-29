# Gatcenters (Fusion add-in)

Zet in het midden van elk rond gat een kort lijntje, zodat de lasersnijder het gatcentrum markeert (een stip
om later op te boren of te tappen).

## Wat het doet

- Knop **Gatcenters** in Manufacture → tab **Fabrication** (lasersnijden), en in Design → Solid → Create en
  Sheet Metal → Create.
- Selecteer een of meer **vlakke vlakken** (bijv. de bovenkant van de plaat). De dialoog laat zien hoeveel
  ronde gaten er gevonden zijn.
- **Lijnlengte**: standaard **0,03 mm**; de laatst gebruikte waarde blijft staan zolang Fusion open is.
- **Schets maken**: per vlak een schets *Gatcenters* op dat vlak, met per gat een horizontale lijn
  (x-richting van de schets) die precies op het middelpunt gecentreerd is. Alleen die lijnen, geen
  geprojecteerde randen.
- Een gat telt als de binnenlus van het vlak alleen uit cirkels/bogen met hetzelfde middelpunt bestaat.
  Sleufgaten, vierkante gaten en de buitenrand tellen niet mee.

## Installeren

1. Kopieer de map `GatCenters` naar `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\`.
2. Fusion: Utilities → Add-Ins → tab Add-Ins → **GatCenters** → Run. Vink *Run on Startup* aan.

## Voor ontwikkelaars

| Bestand | Inhoud |
|---|---|
| `GatCenters.py` | Knop, dialoog, schets maken (Fusion) |
| `gat_core.py` | Gaten herkennen in de lussen van een vlak, lijnpunten, zonder Fusion |
| `tests/test_gat_core.py` | Tests: `python tests/test_gat_core.py` |
| `tools/maak_iconen.py` | Maakt de iconen opnieuw (Pillow) |

Versie staat in `gat_core.VERSIE` en in het manifest; de test controleert dat ze gelijk zijn.

Nog niet in Fusion zelf getest. Te controleren: de tab-ID `FabricationTab` in Manufacture (ontbreekt die,
dan komt de knop in een eigen paneel in de eerste tab), en of Fusion in de Manufacture-werkomgeving een
schets laat maken op het ontwerp. Lukt dat niet, gebruik dan de knop in Design.
