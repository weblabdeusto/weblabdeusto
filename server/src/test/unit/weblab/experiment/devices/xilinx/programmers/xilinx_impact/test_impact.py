# #!/usr/bin/python
# # -*- coding: utf-8 -*-
# #
# # Copyright (C) 2005 onwards University of Deusto
# # All rights reserved.
# #
# # This software is licensed as described in the file COPYING, which
# # you should have received as part of this distribution.
# #
# # This software consists of contributions made by many individuals,
# # listed below:
# #
# # Author: Pablo Orduña <pablo@ordunya.com>
# #         Jaime Irurzun <jaime.irurzun@gmail.com>
# #
# from __future__ import print_function, unicode_literals
# import unittest
#
#
# import test.unit.configuration as configuration_module
#
# import voodoo.configuration as ConfigurationManager
# from weblab.experiment.devices.xilinx.programmers.xilinx_impact.impact import XilinxImpact
#
#
# class XilinxImpactErrors(object):
#     pass
#
#
# class XilinxImpactTestCase(unittest.TestCase):
#
#     def setUp(self):
#         self.cfg_manager= ConfigurationManager.ConfigurationManager()
#         self.cfg_manager.append_module(configuration_module)
#         self._fpga = XilinxImpact.XilinxImpactFPGA(self.cfg_manager)
#         self._pld = XilinxImpact.XilinxImpactPLD(self.cfg_manager)
#
#     def test_program_device(self):
#         self._fpga.program_device("everything_ok.bit")
#         self._pld.program_device("everything_ok.jed")
#
#     def test_program_device_errors(self):
#         self._test_program_device_errors(self._fpga)
#         self._test_program_device_errors(self._pld)
#
#     def _test_program_device_errors(self, impact):
#         self.assertRaises(
#             XilinxImpactErrors.ProgrammingGotErrors,
#             impact.program_device,
#             "error.file"
#         )
#         self.assertRaises(
#             XilinxImpactErrors.ProgrammingGotErrors,
#             impact.program_device,
#             "stderr.file"
#         )
#         self.assertRaises(
#             XilinxImpactErrors.ProgrammingGotErrors,
#             impact.program_device,
#             "return-1.file"
#         )
#
#         impact._busy = True
#         self.assertRaises(
#             XilinxImpactErrors.AlreadyProgrammingDeviceError,
#             impact.program_device,
#             "file.file"
#         )
#         impact._busy = False
#
#         self.cfg_manager._values['xilinx_impact_full_path'] = ['p0wn3d']
#
#         self.assertRaises(
#             XilinxImpactErrors.ErrorProgrammingDeviceError,
#             impact.program_device,
#             "file.file"
#         )
#         self.cfg_manager._values.pop('xilinx_impact_full_path')
#
#         self.assertRaises(
#             XilinxImpactErrors.CantFindXilinxProperty,
#             impact.program_device,
#             "file.file"
#         )
#         self.cfg_manager.reload()
#
#     def test_source2svf(self):
#         self._fpga.source2svf("everything_ok.bit")
#         self._pld.source2svf("everything_ok.jed")
#
#     def test_source2svf_errors(self):
#         self._test_source2svf_errors(self._fpga)
#         self._test_source2svf_errors(self._pld)
#
#     def _test_source2svf_errors(self, impact):
#         self.assertRaises(
#             XilinxImpactErrors.GeneratingSvfFileGotErrors,
#             impact.source2svf,
#             "error.file"
#         )
#         self.assertRaises(
#             XilinxImpactErrors.GeneratingSvfFileGotErrors,
#             impact.source2svf,
#             "return-1.file"
#         )
#
#         self.cfg_manager._values['xilinx_impact_full_path'] = ['p0wn3d']
#
#         self.assertRaises(
#             XilinxImpactErrors.ErrorProgrammingDeviceError,
#             impact.source2svf,
#             "file.file"
#         )
#         self.cfg_manager._values.pop('xilinx_impact_full_path')
#
#         self.assertRaises(
#             XilinxImpactErrors.CantFindXilinxProperty,
#             impact.source2svf,
#             "file.file"
#         )
#         self.cfg_manager.reload()
#
#
# def suite():
#     return unittest.makeSuite(XilinxImpactTestCase)
#
# if __name__ == '__main__':
#     unittest.main()
