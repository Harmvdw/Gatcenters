# -*- coding: utf-8 -*-
"""Tests voor gat_core zonder Fusion: python tests/test_gat_core.py"""
import json
import os
import sys
import unittest

MAP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, MAP)
import gat_core as g  # noqa: E402


def cirkel(x, y, r=0.25):
    return {'soort': 'cirkel', 'midden': (x, y, 0.0), 'straal': r}


def boog(x, y, r=0.25):
    return {'soort': 'boog', 'midden': (x, y, 0.0), 'straal': r}


LIJN = {'soort': 'anders', 'midden': (0, 0, 0), 'straal': 0}


class TestGatCore(unittest.TestCase):
    def test_hele_cirkel(self):
        self.assertEqual(g.gat_midden([cirkel(1, 2)]), (1, 2, 0.0))

    def test_cirkel_in_twee_bogen(self):
        self.assertEqual(g.gat_midden([boog(1, 2), boog(1, 2 + 1e-6)]), (1, 2, 0.0))

    def test_sleufgat_telt_niet(self):
        self.assertIsNone(g.gat_midden([boog(0, 0), LIJN, boog(3, 0), LIJN]))

    def test_bogen_ander_midden_telt_niet(self):
        self.assertIsNone(g.gat_midden([boog(0, 0), boog(0.5, 0)]))
        self.assertIsNone(g.gat_midden([boog(0, 0, 0.25), boog(0, 0, 0.3)]))

    def test_lege_lus(self):
        self.assertIsNone(g.gat_midden([]))

    def test_middens_zonder_dubbele(self):
        lussen = [[cirkel(0, 0)], [cirkel(5, 0)], [LIJN, LIJN, LIJN, LIJN], [cirkel(5, 0)]]
        self.assertEqual(g.gat_middens(lussen), [(0, 0, 0.0), (5, 0, 0.0)])

    def test_lijn_punten(self):
        a, b = g.lijn_punten((1.0, 2.0, 0.0))
        self.assertAlmostEqual(b[0] - a[0], 0.003)  # 0,03 mm in cm
        self.assertAlmostEqual((a[0] + b[0]) / 2, 1.0)
        self.assertEqual(a[1], 2.0)
        self.assertEqual(b[1], 2.0)

    def test_manifest_versie(self):
        with open(os.path.join(MAP, 'GatCenters.manifest'), encoding='utf-8') as f:
            self.assertEqual(json.load(f)['version'], g.VERSIE)


if __name__ == '__main__':
    unittest.main(verbosity=1)
