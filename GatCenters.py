# -*- coding: utf-8 -*-
#
#  Gatcenters  -  Fusion 360 add-in
#
#  Knop "Gatcenters" in Manufacture (Fabrication, het lasersnijden) en in Design (Solid en Sheet Metal).
#  Selecteer een of meer vlakke vlakken: per vlak komt er een schets met in het middelpunt van elk rond gat
#  een korte lijn (standaard 0,03 mm). De lasersnijder brandt die als een stip, zodat het gat later
#  makkelijk te boren of te tappen is.
#
#  Logica zonder Fusion in gat_core.py (los te testen).
#
import adsk.core
import adsk.fusion
import traceback
import os
import sys

_dir = os.path.dirname(os.path.realpath(__file__))
if _dir not in sys.path:
    sys.path.insert(0, _dir)
import gat_core as core

CMD_ID = 'HvdW_GatCenters'
CMD_NAME = 'Gatcenters'
CMD_TIP = 'Selecteer een vlak: schets met een lijntje van 0,03 mm in het midden van elk gat'
SCHETS_NAAM = 'Gatcenters'

# Plekken voor de knop: (werkomgeving, tab, paneel of None). Ontbreekt het paneel, dan een eigen paneel
# "Gatcenters" in die tab; ontbreekt de tab, dan in de eerste tab van de werkomgeving.
PLEKKEN = [('CAMEnvironment', 'FabricationTab', None),
           ('FusionSolidEnvironment', 'SolidTab', 'SolidCreatePanel'),
           ('FusionSolidEnvironment', 'SheetMetalTab', 'SheetMetalCreatePanel')]
EIGEN_PANEEL = ('HvdW_GatPaneel_', 'Gatcenters')

app = adsk.core.Application.get()
ui = app.userInterface
_handlers = []
_geplaatst = set()
_t = {'lengte': '0.03 mm'}  # laatst gebruikte lengte, deze Fusion-sessie

CIRKELS = {adsk.core.Curve3DTypes.Circle3DCurveType: 'cirkel', adsk.core.Curve3DTypes.Arc3DCurveType: 'boog'}


def fout(titel):
    ui.messageBox('%s:\n\n%s' % (titel, traceback.format_exc()), CMD_NAME)


# ============================================================================
#  Gaten zoeken en schetsen
# ============================================================================
def lussen_van(face):
    """Binnenlussen van het vlak als lijsten krommen voor gat_core (coördinaten van het vlak zelf)."""
    uit = []
    for lus in face.loops:
        if lus.isOuter:
            continue
        krommen = []
        for edge in lus.edges:
            geo = edge.geometry
            soort = CIRKELS.get(geo.curveType, 'anders')
            if soort == 'anders':
                krommen.append({'soort': soort, 'midden': (0, 0, 0), 'straal': 0})
            else:
                c = geo.center
                krommen.append({'soort': soort, 'midden': (c.x, c.y, c.z), 'straal': geo.radius})
        uit.append(krommen)
    return uit


def gekozen_vlakken(inputs):
    sel = adsk.core.SelectionCommandInput.cast(inputs.itemById('vlak'))
    return [adsk.fusion.BRepFace.cast(sel.selection(i).entity) for i in range(sel.selectionCount)]


def maak_schets(face, lengte):
    """Schets op het vlak met een lijn per gatmidden. Geeft het aantal lijnen terug."""
    # In een samenstelling is het vlak een proxy; de schets hoort in de component van het lichaam.
    eigen = face.nativeObject if face.assemblyContext else face
    middens = core.gat_middens(lussen_van(eigen))
    if not middens:
        return 0
    comp = eigen.body.parentComponent
    schets = comp.sketches.addWithoutEdges(eigen)
    schets.name = SCHETS_NAAM
    lijnen = schets.sketchCurves.sketchLines
    schets.isComputeDeferred = True
    try:
        for m in middens:
            p = schets.modelToSketchSpace(adsk.core.Point3D.create(*m))
            a, b = core.lijn_punten((p.x, p.y, p.z), lengte)
            lijnen.addByTwoPoints(adsk.core.Point3D.create(*a), adsk.core.Point3D.create(*b))
    finally:
        schets.isComputeDeferred = False
    return len(middens)


# ============================================================================
#  Dialoog
# ============================================================================
def werk_info_bij(inputs):
    tb = adsk.core.TextBoxCommandInput.cast(inputs.itemById('info'))
    vlakken = gekozen_vlakken(inputs)
    if not vlakken:
        tb.formattedText = 'Selecteer een vlak met gaten (bijv. de bovenkant van de plaat).'
        return
    n = sum(len(core.gat_middens(lussen_van(f.nativeObject if f.assemblyContext else f))) for f in vlakken)
    tb.formattedText = '<b>%d</b> rond%s gat%s gevonden op %d vlak%s.' % (
        n, '' if n == 1 else 'e', '' if n == 1 else 'en', len(vlakken), '' if len(vlakken) == 1 else 'ken')


class CreatedHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        try:
            cmd = args.command
            inputs = cmd.commandInputs
            sel = inputs.addSelectionInput('vlak', 'Vlak', 'Selecteer een vlak met gaten')
            sel.addSelectionFilter('PlanarFaces')
            sel.setSelectionLimits(1, 0)
            inputs.addValueInput('lengte', 'Lijnlengte', 'mm', adsk.core.ValueInput.createByString(_t['lengte']))
            inputs.addTextBoxCommandInput('info', '', '', 2, True)
            werk_info_bij(inputs)
            cmd.okButtonText = 'Schets maken'
            for handler, event in ((InputChangedHandler(), cmd.inputChanged), (ValidateHandler(), cmd.validateInputs),
                                   (ExecuteHandler(), cmd.execute)):
                event.add(handler)
                _handlers.append(handler)
        except Exception:
            fout('Dialoog opbouwen mislukt')


class InputChangedHandler(adsk.core.InputChangedEventHandler):
    def notify(self, args):
        try:
            if args.input.id == 'vlak':
                werk_info_bij(args.input.parentCommand.commandInputs)
        except Exception:
            fout('Fout in de dialoog')


class ValidateHandler(adsk.core.ValidateInputsEventHandler):
    def notify(self, args):
        try:
            lengte = adsk.core.ValueCommandInput.cast(args.inputs.itemById('lengte'))
            args.areInputsValid = lengte.isValidExpression and lengte.value > 0
        except Exception:
            args.areInputsValid = False


class ExecuteHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        try:
            inputs = args.command.commandInputs
            lengte = adsk.core.ValueCommandInput.cast(inputs.itemById('lengte'))
            _t['lengte'] = lengte.expression
            totaal, zonder = 0, 0
            for face in gekozen_vlakken(inputs):
                n = maak_schets(face, lengte.value)
                totaal += n
                zonder += n == 0
            if totaal == 0:
                ui.messageBox('Geen ronde gaten gevonden op het gekozen vlak. Er is geen schets gemaakt.', CMD_NAME)
            elif zonder:
                ui.messageBox('%d lijnen gezet. %d vlak(ken) zonder ronde gaten overgeslagen.' % (totaal, zonder), CMD_NAME)
        except Exception:
            fout('Schets maken mislukt')


class WorkspaceActivatedHandler(adsk.core.WorkspaceEventHandler):
    def notify(self, args):
        try:
            plaats_knoppen()
        except Exception:
            pass


# ============================================================================
#  Knoppen
# ============================================================================
def plaats_knoppen():
    cmd_def = ui.commandDefinitions.itemById(CMD_ID)
    for ws_id, tab_id, paneel_id in PLEKKEN:
        if (ws_id, tab_id) in _geplaatst:
            continue
        ws = ui.workspaces.itemById(ws_id)
        if not cmd_def or not ws or ws.toolbarTabs.count == 0:
            continue  # werkomgeving nog niet opgebouwd; WorkspaceActivatedHandler probeert later
        tab = ws.toolbarTabs.itemById(tab_id) or ws.toolbarTabs.item(0)
        paneel = tab.toolbarPanels.itemById(paneel_id) if paneel_id else None
        if not paneel:
            eigen_id = EIGEN_PANEEL[0] + tab.id
            paneel = tab.toolbarPanels.itemById(eigen_id) or tab.toolbarPanels.add(eigen_id, EIGEN_PANEEL[1])
        if not paneel.controls.itemById(CMD_ID):
            knop = paneel.controls.addCommand(cmd_def)
            knop.isPromoted = paneel.id.startswith(EIGEN_PANEEL[0])
        _geplaatst.add((ws_id, tab_id))


def verwijder_knoppen():
    for ws_id, _, paneel_id in PLEKKEN:
        ws = ui.workspaces.itemById(ws_id)
        if not ws:
            continue
        for i in range(ws.toolbarTabs.count):
            tab = ws.toolbarTabs.item(i)
            for p in (tab.toolbarPanels.itemById(paneel_id) if paneel_id else None,
                      tab.toolbarPanels.itemById(EIGEN_PANEEL[0] + tab.id)):
                if not p:
                    continue
                c = p.controls.itemById(CMD_ID)
                if c:
                    c.deleteMe()
                if p.id.startswith(EIGEN_PANEEL[0]) and p.controls.count == 0:
                    p.deleteMe()


def run(context):
    try:
        cmd_def = ui.commandDefinitions.itemById(CMD_ID) or ui.commandDefinitions.addButtonDefinition(
            CMD_ID, CMD_NAME, CMD_TIP, os.path.join(_dir, 'resources'))
        on_created = CreatedHandler()
        cmd_def.commandCreated.add(on_created)
        _handlers.append(on_created)
        on_ws = WorkspaceActivatedHandler()
        ui.workspaceActivated.add(on_ws)
        _handlers.append(on_ws)
        plaats_knoppen()
    except Exception:
        fout('Add-in starten mislukt')


def stop(context):
    try:
        for h in _handlers:
            if isinstance(h, WorkspaceActivatedHandler):
                ui.workspaceActivated.remove(h)
        verwijder_knoppen()
        cmd_def = ui.commandDefinitions.itemById(CMD_ID)
        if cmd_def:
            cmd_def.deleteMe()
        _handlers.clear()
        _geplaatst.clear()
    except Exception:
        fout('Add-in stoppen mislukt')
