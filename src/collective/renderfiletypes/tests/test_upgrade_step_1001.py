# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from collective.renderfiletypes.testing import COLLECTIVE_RENDERFILETYPES_FUNCTIONAL_TESTING
from collective.renderfiletypes.testing import COLLECTIVE_RENDERFILETYPES_INTEGRATION_TESTING

import unittest


class UpgradeStepIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_RENDERFILETYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_upgrade_step(self):
        # dummy, add tests here
        self.assertTrue(True)


# class UpgradeStepFunctionalTest(unittest.TestCase):
#
#     layer = COLLECTIVE_RENDERFILETYPES_FUNCTIONAL_TESTING
#
#     def setUp(self):
#         self.portal = self.layer['portal']
#         setRoles(self.portal, TEST_USER_ID, ['Manager'])
