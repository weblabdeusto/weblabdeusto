#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
#

from test.util.wlcontext import wlcontext
from test.util.ports import new as new_port
from test.util.module_disposer import uses_module, case_uses_module
from experiments.ud_xilinx.command_senders import SerialPortCommandSender
from experiments.ud_xilinx.programmers import XilinxImpactProgrammer
import test.unit.configuration as configuration
import time
import unittest
import voodoo.configuration as ConfigurationManager
import voodoo.gen.coordinator.Access as Access
import voodoo.gen.coordinator.AccessLevel as AccessLevel
import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.gen.coordinator.CoordinationInformation as CoordInfo
import voodoo.gen.coordinator.CoordinatorServer as CoordinatorServer
import voodoo.gen.generators.ServerSkel as ServerSkel
import voodoo.gen.locator.EasyLocator as EasyLocator
import voodoo.gen.locator.ServerLocator as ServerLocator
import voodoo.gen.locator.ServerTypeHandler as ServerTypeHandler
import voodoo.gen.protocols.Direct.Address as DirectAddress
import voodoo.gen.protocols.Direct.Network as DirectNetwork
import voodoo.gen.protocols.protocols as Protocols
import voodoo.gen.protocols.SOAP.Address as SOAPAddress
import voodoo.gen.protocols.SOAP.Network as SOAPNetwork
import voodoo.gen.protocols.SOAP.ServerSOAP as ServerSOAP
import voodoo.gen.registry.server_registry as ServerRegistry
import voodoo.methods as voodoo_exported_methods
import voodoo.sessions.session_type as SessionType
import weblab.data.command as Command
import weblab.data.server_type as ServerType
import weblab.experiment.util as ExperimentUtil
import experiments.ud_xilinx.server as UdXilinxExperiment
import weblab.lab.server as LaboratoryServer
import weblab.methods as weblab_exported_methods
import weblab.core.reservations as Reservation
import weblab.core.server as UserProcessingServer
import weblab.core.server as core_api
import weblab.core.user_processor       as UserProcessor
import weblab.core.exc             as core_exc
from weblab.core.coordinator.gateway import create as coordinator_create, SQLALCHEMY



# Wait that time at most for the board to finish programming before giving up.
XILINX_TIMEOUT = 4

PORT1 = new_port()
PORT2 = new_port()
PORT3 = new_port()
PORT5 = new_port()
PORT7 = new_port()
PORT8 = new_port()
PORT9 = new_port()

########################################################
# Case 001: a single instance of everything on a       #
# single instance of the WebLab, with two experiments #
########################################################

class FakeUdXilinxExperiment(UdXilinxExperiment.UdXilinxExperiment):
    def __init__(self, coord_address, locator, cfg_manager, fake_xilinx_impact, fake_serial_port, *args, **kargs):
        super(FakeUdXilinxExperiment,self).__init__(coord_address, locator, cfg_manager, *args, **kargs)
        self._xilinx_impact = fake_xilinx_impact
        self._xilinx_impact = fake_xilinx_impact
        self._programmer = XilinxImpactProgrammer(cfg_manager, fake_xilinx_impact)
        self._programmer._xilinx_impact_device = fake_xilinx_impact
        self._command_sender = SerialPortCommandSender(cfg_manager)
        self._command_sender._serial_port = fake_serial_port

class FakeImpact(object):
    def __init__(self):
        super(FakeImpact,self).__init__()
        self.clear()
    def program_device(self, program_path):
        self._paths.append(open(program_path).read())
    def get_suffix(self):
        return "whatever"
    def clear(self):
        self._paths = []

class FakeSerialPort(object):
    def __init__(self):
        super(FakeSerialPort,self).__init__()
        self.clear()
    def open_serial_port(self, number):
        self.dict['open'].append((self.cycle, number))
        self.cycle += 1
    def send_code(self, n):
        self.dict['send'].append((self.cycle, n))
        self.cycle += 1
    def close_serial_port(self):
        self.dict['close'].append((self.cycle, None))
        self.cycle += 1
    def clear(self):
        self.dict = {'open':[], 'close':[], 'send' : []}
        self.cycle = 0

# Abstract
class Case002TestCase(object):

    def gen_coordination_map(self, protocols):
        map = CoordInfo.CoordinationMap()

        map.add_new_machine('WL_MACHINE1')
        map.add_new_instance('WL_MACHINE1','WL_SERVER1')
        map.add_new_server( 'WL_MACHINE1', 'WL_SERVER1', 'ups1',         ServerType.UserProcessing, ())
        map.add_new_server( 'WL_MACHINE1', 'WL_SERVER1', 'coordinator1', ServerType.Coordinator, ())
        map.add_new_server( 'WL_MACHINE1', 'WL_SERVER1', 'laboratory1',  ServerType.Laboratory, ())
        map.add_new_server( 'WL_MACHINE1', 'WL_SERVER1', 'experiment1',  ServerType.Experiment, (), ('ud-fpga@FPGA experiments',))
        map.add_new_server( 'WL_MACHINE1', 'WL_SERVER1', 'experiment2',  ServerType.Experiment, (), ('ud-pld@PLD experiments',))

        if len(protocols) == 1 and protocols[0] == Protocols.Direct:
            # They all have Direct

            # 1st: address
            address2 = map['WL_MACHINE1']['WL_SERVER1']['ups1'].address
            address3 = map['WL_MACHINE1']['WL_SERVER1']['coordinator1'].address
            address5 = map['WL_MACHINE1']['WL_SERVER1']['laboratory1'].address
            address7 = map['WL_MACHINE1']['WL_SERVER1']['experiment1'].address
            address8 = map['WL_MACHINE1']['WL_SERVER1']['experiment2'].address

            # 2nd: network
            direct_network2 = DirectNetwork.DirectNetwork( DirectAddress.from_coord_address(address2))
            direct_network3 = DirectNetwork.DirectNetwork( DirectAddress.from_coord_address(address3))
            direct_network5 = DirectNetwork.DirectNetwork( DirectAddress.from_coord_address(address5))
            direct_network7 = DirectNetwork.DirectNetwork( DirectAddress.from_coord_address(address7))
            direct_network8 = DirectNetwork.DirectNetwork( DirectAddress.from_coord_address(address8))

            # 3rd: accesses
            access_direct2 = Access.Access( Protocols.Direct, AccessLevel.instance,(direct_network2,))
            access_direct3 = Access.Access( Protocols.Direct, AccessLevel.instance,(direct_network3,))
            access_direct5 = Access.Access( Protocols.Direct, AccessLevel.instance,(direct_network5,))
            access_direct7 = Access.Access( Protocols.Direct, AccessLevel.instance,(direct_network7,))
            access_direct8 = Access.Access( Protocols.Direct, AccessLevel.instance,(direct_network8,))

            # 4th: appending accesses
            map.append_accesses( 'WL_MACHINE1', 'WL_SERVER1', 'ups1', ( access_direct2, ))
            map.append_accesses( 'WL_MACHINE1', 'WL_SERVER1', 'coordinator1', ( access_direct3, ))
            map.append_accesses( 'WL_MACHINE1', 'WL_SERVER1', 'laboratory1', ( access_direct5, ))
            map.append_accesses( 'WL_MACHINE1', 'WL_SERVER1', 'experiment1', ( access_direct7, ))
            map.append_accesses( 'WL_MACHINE1', 'WL_SERVER1', 'experiment2', ( access_direct8, ))

        else:
            # They all have SOAP

            # 1st: address
            address2 = SOAPAddress.Address('127.0.0.1:%s@NETWORK' % PORT2)
            address3 = SOAPAddress.Address('127.0.0.1:%s@NETWORK' % PORT3)
            address5 = SOAPAddress.Address('127.0.0.1:%s@NETWORK' % PORT5)
            address7 = SOAPAddress.Address('127.0.0.1:%s@NETWORK' % PORT7)
            address8 = SOAPAddress.Address('127.0.0.1:%s@NETWORK' % PORT8)

            # 2nd: network
            soap_network2 = SOAPNetwork.SOAPNetwork( address2 )
            soap_network3 = SOAPNetwork.SOAPNetwork( address3 )
            soap_network5 = SOAPNetwork.SOAPNetwork( address5 )
            soap_network7 = SOAPNetwork.SOAPNetwork( address7 )
            soap_network8 = SOAPNetwork.SOAPNetwork( address8 )

            # 3rd: accesses
            access_soap2 = Access.Access( Protocols.SOAP, AccessLevel.network,(soap_network2,) )
            access_soap3 = Access.Access( Protocols.SOAP, AccessLevel.network,(soap_network3,) )
            access_soap5 = Access.Access( Protocols.SOAP, AccessLevel.network,(soap_network5,) )
            access_soap7 = Access.Access( Protocols.SOAP, AccessLevel.network,(soap_network7,) )
            access_soap8 = Access.Access( Protocols.SOAP, AccessLevel.network,(soap_network8,) )

            # 4th: appending accesses
            map.append_accesses( 'WL_MACHINE1', 'WL_SERVER1', 'ups1', ( access_soap2, ))
            map.append_accesses( 'WL_MACHINE1', 'WL_SERVER1', 'coordinator1', ( access_soap3, ))
            map.append_accesses( 'WL_MACHINE1', 'WL_SERVER1', 'laboratory1', ( access_soap5, ))
            map.append_accesses( 'WL_MACHINE1', 'WL_SERVER1', 'experiment1', ( access_soap7, ))
            map.append_accesses( 'WL_MACHINE1', 'WL_SERVER1', 'experiment2', ( access_soap8, ))

        return map

    def generate_coordinator_server(self, protocol, cfg_manager):
        map = self.gen_coordination_map(protocol)

        protocols = protocol
        if protocol[0] != Protocols.Direct:
            protocols += (Protocols.Direct,)

        generated_coordinator = ServerSkel.factory(
                cfg_manager,
                protocols,
                voodoo_exported_methods.coordinator
            )

        class RealCoordinatorServer(CoordinatorServer.CoordinatorServer,generated_coordinator):
            def __init__(self,cfg_manager,map,*args,**kargs):
                CoordinatorServer.CoordinatorServer.__init__(self,cfg_manager,map,*args,**kargs)

        real_coordinator_server = RealCoordinatorServer(
                cfg_manager,
                map,
                Direct = (map['WL_MACHINE1']['WL_SERVER1']['coordinator1'].address.address,),
                SOAP   = ('',new_port())
            )
        real_coordinator_server.start()
        self.map = map
        return real_coordinator_server

    def generate_locator(self):
        coordinator_server_address = DirectAddress.Address(
                'WL_MACHINE1',
                'WL_SERVER1',
                'coordinator1'
            )
        server_type_handler = ServerTypeHandler.ServerTypeHandler(
            ServerType,
            {
                ServerType.Coordinator :       voodoo_exported_methods.coordinator,
                ServerType.UserProcessing :    weblab_exported_methods.UserProcessing,
                ServerType.Proxy :             weblab_exported_methods.Proxy,
                ServerType.Laboratory :        weblab_exported_methods.Laboratory,
                ServerType.Translator :        weblab_exported_methods.Translator,
                ServerType.Experiment :        weblab_exported_methods.Experiment
            }
        )

        locator = ServerLocator.ServerLocator(
            coordinator_server_address,
            server_type_handler
        )
        easy_locator = EasyLocator.EasyLocator(
                CoordAddress.CoordAddress('WL_MACHINE1','WL_SERVER1', 'coordinator1'),
                locator
            )

        return easy_locator

    def generate_configuration_server(self):
        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration)
        return cfg_manager

    def generate_core_server(self, cfg_manager, protocols):
        ups_coord_address = CoordAddress.CoordAddress.translate_address("ups1:WL_SERVER1@WL_MACHINE1")
        locator = self.generate_locator()

        generated_ups = ServerSkel.factory(
                cfg_manager,
                protocols,
                weblab_exported_methods.UserProcessing
            )

        class RealUserProcessingServer(UserProcessingServer.UserProcessingServer,generated_ups):
            def __init__(self, coord_address, locator, cfg_manager, *args,**kargs):
                UserProcessingServer.UserProcessingServer.__init__(
                        self,
                        coord_address,
                        locator,
                        cfg_manager,
                        *args,
                        **kargs
                    )

        coordinator = coordinator_create(SQLALCHEMY, self.locator, self.cfg_manager)
        coordinator._clean()
        coordinator.stop()

        real_core_server = RealUserProcessingServer(
                ups_coord_address,
                locator,
                cfg_manager,
                Direct = (ups_coord_address.address,),
                SOAP   = ('',new_port())
            )
        real_core_server.start()

        core_client = locator.get_server(ServerType.UserProcessing, None)
        return core_client, real_core_server

    def generate_fake_experiment(self, cfg_manager, fake_xilinx_impact, fake_serial_port, number, experiment_name, experiment_category_name, protocols):
        generated_experiment = ServerSkel.factory(
                cfg_manager,
                protocols,
                weblab_exported_methods.Experiment
            )
        locator = self.generate_locator()

        class RealUdXilinxExperiment(FakeUdXilinxExperiment,generated_experiment):
            def __init__(self, coord_address, locator, cfg_manager, fake_xilinx_impact, fake_serial_port, *args,**kargs):
                FakeUdXilinxExperiment.__init__(
                        self,
                        coord_address,
                        locator,
                        cfg_manager,
                        fake_xilinx_impact,
                        fake_serial_port,
                        *args,
                        **kargs
                    )

        real_experiment = RealUdXilinxExperiment(
                None,
                None,
                cfg_manager,
                fake_xilinx_impact,
                fake_serial_port,
                Direct = ( self.map['WL_MACHINE1']['WL_SERVER1']['experiment' + number].address.address,),
                SOAP   = ('',new_port() + (int(number)-1))
            )
        real_experiment.start()

        def on_finish():
            experiment_client = locator.get_server(
                            ServerType.Experiment,
                            experiment_name + '@' + experiment_category_name
                        )
            return experiment_client, real_experiment
        return on_finish

    def generate_laboratory_server(self, cfg_manager, protocols):
        generated_laboratory_server = ServerSkel.factory(
                cfg_manager,
                protocols,
                weblab_exported_methods.Laboratory
            )
        locator = self.generate_locator()

        class RealLaboratoryServer(LaboratoryServer.LaboratoryServer,generated_laboratory_server):
            def __init__(self, coord_address, locator, cfg_manager, *args,**kargs):
                LaboratoryServer.LaboratoryServer.__init__(
                        self,
                        coord_address,
                        locator,
                        cfg_manager,
                        *args,
                        **kargs
                    )

        real_laboratory_server = RealLaboratoryServer(
                self.map['WL_MACHINE1']['WL_SERVER1']['laboratory1'].address,
                locator,
                cfg_manager,
                Direct = (self.map['WL_MACHINE1']['WL_SERVER1']['laboratory1'].address.address,),
                SOAP   = ('',new_port())
            )
        real_laboratory_server.start()

        laboratory_client = locator.get_server(ServerType.Laboratory, None)
        return laboratory_client, real_laboratory_server

    def setUp(self):
        protocols                      = self.get_protocols()

        self.real_servers              = []

        self.fake_impact1              = FakeImpact()
        self.fake_serial_port1         = FakeSerialPort()

        self.fake_impact2              = FakeImpact()
        self.fake_serial_port2         = FakeSerialPort()

        self.cfg_manager               = self.generate_configuration_server()
        self.coordinator_server        = self.generate_coordinator_server(protocols, self.cfg_manager)
        self.real_servers.append(self.coordinator_server)

        self.locator                   = None

        self.core_server, reals    = self.generate_core_server(
                                self.cfg_manager,
                                protocols
                            )
        self.real_ups = reals
        self.real_servers.append(reals)
        on_finish1                     = self.generate_fake_experiment(
                                self.cfg_manager,
                                self.fake_impact1,
                                self.fake_serial_port1,
                                '1',
                                'ud-fpga',
                                'FPGA experiments',
                                protocols
                            )
        on_finish2                     = self.generate_fake_experiment(
                                self.cfg_manager,
                                self.fake_impact2,
                                self.fake_serial_port2,
                                '2',
                                'ud-pld',
                                'PLD experiments',
                                protocols
                            )
        self.experiment1, reals       = on_finish1()
        self.real_servers.append(reals)
        self.experiment2, reals       = on_finish2()
        self.real_servers.append(reals)

        self.laboratory_server, reals   = self.generate_laboratory_server(
                                self.cfg_manager,
                                protocols
                            )
        self.real_servers.append(reals)

    @uses_module(UserProcessingServer)
    @uses_module(UserProcessor)
    @uses_module(ServerSOAP)
    def test_single_uses_timeout(self):
        self.fake_impact1.clear()
        self.fake_impact2.clear()
        self.fake_serial_port1.clear()
        self.fake_serial_port2.clear()

        # 6 users get into the system
        with wlcontext(self.real_ups):
            session_id1 = core_api.login('student1','password')
        with wlcontext(self.real_ups):
            session_id2 = core_api.login('student2','password')
        with wlcontext(self.real_ups):
            session_id3 = core_api.login('student3','password')
        with wlcontext(self.real_ups):
            session_id4 = core_api.login('student4','password')
        with wlcontext(self.real_ups):
            session_id5 = core_api.login('student5','password')
        with wlcontext(self.real_ups):
            session_id6 = core_api.login('student6','password')

        # they all have access to the ud-fpga experiment
        with wlcontext(self.real_ups, session_id = session_id1):
            experiments1 = core_api.list_experiments()
            fpga_experiments1 = [ exp.experiment for exp in experiments1 if exp.experiment.name == 'ud-fpga' ]
            self.assertEquals( len(fpga_experiments1), 1 )

        with wlcontext(self.real_ups, session_id = session_id2):
            experiments2 = core_api.list_experiments()
            fpga_experiments2 = [ exp.experiment for exp in experiments2 if exp.experiment.name == 'ud-fpga' ]
            self.assertEquals( len(fpga_experiments2), 1 )

        with wlcontext(self.real_ups, session_id = session_id3):
            experiments3 = core_api.list_experiments()
            fpga_experiments3 = [ exp.experiment for exp in experiments3 if exp.experiment.name == 'ud-fpga' ]
            self.assertEquals( len(fpga_experiments3), 1 )

        with wlcontext(self.real_ups, session_id = session_id4):
            experiments4 = core_api.list_experiments()
            fpga_experiments4 = [ exp.experiment for exp in experiments4 if exp.experiment.name == 'ud-fpga' ]
            self.assertEquals( len(fpga_experiments4), 1 )

        with wlcontext(self.real_ups, session_id = session_id5):
            experiments5 = core_api.list_experiments()
            fpga_experiments5 = [ exp.experiment for exp in experiments5 if exp.experiment.name == 'ud-fpga' ]
            self.assertEquals( len(fpga_experiments5), 1 )

        with wlcontext(self.real_ups, session_id = session_id6):
            experiments6 = core_api.list_experiments()
            fpga_experiments6 = [ exp.experiment for exp in experiments6 if exp.experiment.name == 'ud-fpga' ]
            self.assertEquals( len(fpga_experiments6), 1 )


        # 3 users try to reserve the experiment
        with wlcontext(self.real_ups, session_id = session_id1):
            status1 = core_api.reserve_experiment(fpga_experiments1[0].to_experiment_id(), "{}", "{}")
            reservation_id1 = status1.reservation_id

        with wlcontext(self.real_ups, session_id = session_id2):
            status2 = core_api.reserve_experiment(fpga_experiments2[0].to_experiment_id(), "{}", "{}")
            reservation_id2 = status2.reservation_id
    
        with wlcontext(self.real_ups, session_id = session_id3):
            status3 = core_api.reserve_experiment(fpga_experiments3[0].to_experiment_id(), "{}", "{}")
            reservation_id3 = status3.reservation_id

        # wait until it is reserved
        short_time = 0.1
        times      = 10.0 / short_time

        with wlcontext(self.real_ups, reservation_id = reservation_id1):
            while times > 0:
                time.sleep(short_time)
                new_status = core_api.get_reservation_status()
                if not isinstance(new_status, Reservation.WaitingConfirmationReservation):
                    break
                times -= 1

            # first user got the device. The other two are in WaitingReservation
            reservation1 = core_api.get_reservation_status()
            self.assertTrue(isinstance(reservation1, Reservation.ConfirmedReservation))

        with wlcontext(self.real_ups, reservation_id = reservation_id2):
            reservation2 = core_api.get_reservation_status()
            self.assertTrue(isinstance(reservation2, Reservation.WaitingReservation))
            self.assertEquals( 0, reservation2.position)

        with wlcontext(self.real_ups, reservation_id = reservation_id3):
            reservation3 = core_api.get_reservation_status()
            self.assertTrue(isinstance(reservation3, Reservation.WaitingReservation))
            self.assertEquals( 1, reservation3.position)

        with wlcontext(self.real_ups, session_id = session_id4):
            # Another user tries to reserve the experiment. He goes to the WaitingReservation, position 2
            status4 = core_api.reserve_experiment(fpga_experiments4[0].to_experiment_id(), "{}", "{}")

            reservation_id4 = status4.reservation_id

        with wlcontext(self.real_ups, reservation_id = reservation_id4):
            reservation4 = core_api.get_reservation_status()
            self.assertTrue(isinstance( reservation4, Reservation.WaitingReservation))
            self.assertEquals( 2, reservation4.position)

        with wlcontext(self.real_ups, reservation_id = reservation_id1):
            # The state of other users does not change
            reservation1 = core_api.get_reservation_status()
            self.assertTrue(isinstance( reservation1, Reservation.ConfirmedReservation))

        with wlcontext(self.real_ups, reservation_id = reservation_id2):
            reservation2 = core_api.get_reservation_status()
            self.assertTrue(isinstance( reservation2, Reservation.WaitingReservation))
            self.assertEquals( 0, reservation2.position)

        with wlcontext(self.real_ups, reservation_id = reservation_id3):
            reservation3 = core_api.get_reservation_status()
            self.assertTrue(isinstance(reservation3, Reservation.WaitingReservation))
            self.assertEquals( 1, reservation3.position )

        with wlcontext(self.real_ups, reservation_id = reservation_id2):
            # The user number 2 frees the experiment
            core_api.finished_experiment()

        with wlcontext(self.real_ups, reservation_id = reservation_id2):
            # Whenever he tries to do poll or send_command, he receives an exception
            try:
                core_api.poll()
                core_api.poll()
                core_api.poll()
            except core_exc.NoCurrentReservationError:
                pass # All right :-)

        with wlcontext(self.real_ups, reservation_id = reservation_id1):
            # send a program
            CONTENT = "content of the program FPGA"
            core_api.send_file(ExperimentUtil.serialize(CONTENT), 'program')


            # We need to wait for the programming to finish.
            start_time = time.time()
            response = "STATE=not_ready"
            while response in ("STATE=not_ready", "STATE=programming") and time.time() - start_time < XILINX_TIMEOUT:
                respcmd = core_api.send_command(Command.Command("STATE"))
                response = respcmd.get_command_string()
                time.sleep(0.2)

            # Check that the current state is "Ready"
            self.assertEquals("STATE=ready", response)


            core_api.send_command(Command.Command("ChangeSwitch on 0"))
            core_api.send_command(Command.Command("ClockActivation on 250"))

        with wlcontext(self.real_ups, session_id = session_id1):
            # end session
            core_api.logout()

        # Checking the commands sent
        self.assertEquals(1, len(self.fake_impact1._paths))
        self.assertEquals(0, len(self.fake_impact2._paths))

        self.assertEquals(CONTENT, self.fake_impact1._paths[0])

        initial_open = 1
        initial_send = 1
        initial_close = 1
        initial_total = initial_open + initial_send + initial_close

        # ChangeSwitch on 0
        self.assertEquals(
                (0 + initial_total,1),
                self.fake_serial_port1.dict['open'][0 + initial_open]
            )
        self.assertEquals(
                (1 + initial_total,1),
                self.fake_serial_port1.dict['send'][0 + initial_send]
            )
        self.assertEquals(
                (2 + initial_total,None),
                self.fake_serial_port1.dict['close'][0 + initial_close]
            )

        # ClockActivation on 250
        self.assertEquals(
                (3 + initial_total,1),
                self.fake_serial_port1.dict['open'][1 + initial_open]
            )
        self.assertEquals(
                (4 + initial_total,32),
                self.fake_serial_port1.dict['send'][1 + initial_send]
            )

        self.assertEquals(
                (5 + initial_total,None),
                self.fake_serial_port1.dict['close'][1 + initial_close]
            )
        # TODO: what if the user doesn't say "logout"? check that he dies everywhere

    def tearDown(self):
        ServerRegistry.get_instance().clear()

        for i in self.real_servers:
            i.stop()


@case_uses_module(UserProcessingServer)
class Case002_Direct_Memory_TestCase(Case002TestCase, unittest.TestCase):
    def get_protocols(self):
        return (Protocols.Direct, )
    def get_session_type(self):
        return SessionType.Memory


@case_uses_module(UserProcessingServer)
class Case002_Direct_MySQL_TestCase(Case002TestCase, unittest.TestCase):
    def get_protocols(self):
        return (Protocols.Direct, )
    def get_session_type(self):
        return SessionType.sqlalchemy


def suite():
    return unittest.TestSuite(
        (
            unittest.makeSuite(Case002_Direct_Memory_TestCase),
            unittest.makeSuite(Case002_Direct_MySQL_TestCase)
        )
    )

if __name__ == '__main__':
    unittest.main()


