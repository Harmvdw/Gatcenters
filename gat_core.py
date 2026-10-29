# -*- coding: utf-8 -*-
"""gat_core - logica van de Fusion-add-in Gatcenters, zonder Fusion.

Een vlak heeft een buitenlus en binnenlussen. Een binnenlus is een gat als ze alleen uit cirkels en bogen
bestaat met hetzelfde middelpunt (een hele cirkel, of een cirkel die Fusion in twee bogen heeft geknipt).
Sleufgaten (bogen + rechte lijnen) en vierkante gaten tellen niet mee.

Een lus is hier een lijst krommen: {'soort': 'cirkel'|'boog'|'anders', 'midden': (x, y, z), 'straal': r}.
Maten in cm, zoals de Fusion-API. Tests: python tests/test_gat_core.py
"""
import math

VERSIE = "0.1.0"
TOLERANTIE = 1e-4  # cm (1 µm)
STANDAARD_LENGTE = 0.003  # cm = 0,03 mm


def _dichtbij(a, b, tol=TOLERANTIE):
    return math.dist(a, b) <= tol


def gat_midden(lus, tol=TOLERANTIE):
    """Middelpunt (x, y, z) als de lus een rond gat is, anders None."""
    if not lus or any(k['soort'] not in ('cirkel', 'boog') for k in lus):
        return None
    eerste = lus[0]
    for k in lus[1:]:
        if not _dichtbij(k['midden'], eerste['midden'], tol) or abs(k['straal'] - eerste['straal']) > tol:
            return None
    return tuple(eerste['midden'])


def gat_middens(binnenlussen, tol=TOLERANTIE):
    """Middelpunten van alle ronde gaten, zonder dubbele (bijv. als hetzelfde gat twee keer wordt aangeboden)."""
    uit = []
    for lus in binnenlussen:
        m = gat_midden(lus, tol)
        if m is not None and not any(_dichtbij(m, u, tol) for u in uit):
            uit.append(m)
    return uit


def lijn_punten(midden, lengte=STANDAARD_LENGTE):
    """Begin- en eindpunt (in schetsvlak, x-richting) van een lijn met dit midden en deze lengte."""
    x, y = midden[0], midden[1]
    h = lengte / 2.0
    return (x - h, y, 0.0), (x + h, y, 0.0)
