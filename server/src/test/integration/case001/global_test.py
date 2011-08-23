#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2009 University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals, 
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
# 

from test.util.ModuleDisposer import uses_module, case_uses_module
from weblab.experiment.experiments.ud_xilinx.UdXilinxCommandSenders import SerialPortCommandSender
from weblab.experiment.experiments.ud_xilinx.UdXilinxProgrammers import XilinxImpactProgrammer
import sys
import test.unit.configuration as configuration
import time
import unittest
import voodoo.configuration.ConfigurationManager as ConfigurationManager
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
import voodoo.gen.protocols.Protocols as Protocols
import voodoo.gen.protocols.SOAP.Address as SOAPAddress
import voodoo.gen.protocols.SOAP.Network as SOAPNetwork
import voodoo.gen.protocols.SOAP.ServerSOAP as ServerSOAP
import voodoo.gen.registry.ServerRegistry as ServerRegistry
import voodoo.methods as voodoo_exported_methods
import voodoo.sessions.SessionType as SessionType
import weblab.data.ClientAddress as ClientAddress
import weblab.data.Command as Command
import weblab.data.ServerType as ServerType
import weblab.experiment.util as ExperimentUtil
import weblab.experiment.experiments.ud_xilinx.UdXilinxExperiment as UdXilinxExperiment
import weblab.lab.server as LaboratoryServer
import weblab.login.server as LoginServer
import weblab.methods as weblab_exported_methods
import weblab.core.alive_users    as AliveUsersCollection
import weblab.core.reservations             as Reservation
import weblab.core.server    as UserProcessingServer
import weblab.core.UserProcessor           as UserProcessor
import weblab.core.coordinator.Coordinator as Coordinator




# Wait that time at most for the board to finish programming before giving up.
XILINX_TIMEOUT = 4



########################################################
# Case 001: a single instance of everything on a       #
# single instance of the WebLab, with two experiments #
########################################################


class FakeUdXilinxExperiment(UdXilinxExperiment.UdXilinxExperiment):
    def __init__(self, coord_address, locator, cfg_manager, fake_xilinx_impact, fake_serial_port, *args, **kwargs):
        super(FakeUdXilinxExperiment,self).__init__(coord_address, locator, cfg_manager, *args, **kwargs)
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
class Case001TestCase(object):
    
    def gen_coordination_map(self, protocols):
        map = CoordInfo.CoordinationMap()

        map.add_new_machine('WL_MACHINE1')
        map.add_new_instance('WL_MACHINE1','WL_SERVER1')
        map.add_new_server( 'WL_MACHINE1', 'WL_SERVER1', 'login1',       ServerType.Login, ())
        map.add_new_server( 'WL_MACHINE1', 'WL_SERVER1', 'ups1',         ServerType.UserProcessing, ())
        map.add_new_server( 'WL_MACHINE1', 'WL_SERVER1', 'coordinator1', ServerType.Coordinator, ())
        map.add_new_server( 'WL_MACHINE1', 'WL_SERVER1', 'laboratory1',  ServerType.Laboratory, ())
        map.add_new_server( 'WL_MACHINE1', 'WL_SERVER1', 'experiment1',  ServerType.Experiment, (), ('ud-fpga@FPGA experiments',))
        map.add_new_server( 'WL_MACHINE1', 'WL_SERVER1', 'experiment2',  ServerType.Experiment, (), ('ud-pld@PLD experiments',))

        if len(protocols) == 1 and protocols[0] == Protocols.Direct:
            # They all have Direct 

            # 1st: address
            address1 = map['WL_MACHINE1']['WL_SERVER1']['login1'].address
            address2 = map['WL_MACHINE1']['WL_SERVER1']['ups1'].address
            address3 = map['WL_MACHINE1']['WL_SERVER1']['coordinator1'].address
            address5 = map['WL_MACHINE1']['WL_SERVER1']['laboratory1'].address
            address7 = map['WL_MACHINE1']['WL_SERVER1']['experiment1'].address
            address8 = map['WL_MACHINE1']['WL_SERVER1']['experiment2'].address

            # 2nd: network
            direct_network1 = DirectNetwork.DirectNetwork( DirectAddress.from_coord_address(address1))
            direct_network2 = DirectNetwork.DirectNetwork( DirectAddress.from_coord_address(address2))
            direct_network3 = DirectNetwork.DirectNetwork( DirectAddress.from_coord_address(address3))
            direct_network5 = DirectNetwork.DirectNetwork( DirectAddress.from_coord_address(address5))
            direct_network7 = DirectNetwork.DirectNetwork( DirectAddress.from_coord_address(address7))
            direct_network8 = DirectNetwork.DirectNetwork( DirectAddress.from_coord_address(address8))

            # 3rd: accesses
            access_direct1 = Access.Access( Protocols.Direct, AccessLevel.instance,(direct_network1,))
            access_direct2 = Access.Access( Protocols.Direct, AccessLevel.instance,(direct_network2,))
            access_direct3 = Access.Access( Protocols.Direct, AccessLevel.instance,(direct_network3,))
            access_direct5 = Access.Access( Protocols.Direct, AccessLevel.instance,(direct_network5,))
            access_direct7 = Access.Access( Protocols.Direct, AccessLevel.instance,(direct_network7,))
            access_direct8 = Access.Access( Protocols.Direct, AccessLevel.instance,(direct_network8,))

            # 4th: appending accesses
            map.append_accesses( 'WL_MACHINE1', 'WL_SERVER1', 'login1', ( access_direct1, ))
            map.append_accesses( 'WL_MACHINE1', 'WL_SERVER1', 'ups1', ( access_direct2, ))
            map.append_accesses( 'WL_MACHINE1', 'WL_SERVER1', 'coordinator1', ( access_direct3, ))
            map.append_accesses( 'WL_MACHINE1', 'WL_SERVER1', 'laboratory1', ( access_direct5, ))
            map.append_accesses( 'WL_MACHINE1', 'WL_SERVER1', 'experiment1', ( access_direct7, ))
            map.append_accesses( 'WL_MACHINE1', 'WL_SERVER1', 'experiment2', ( access_direct8, ))

        else:
            # They all have SOAP 

            # 1st: address
            address1 = SOAPAddress.Address('127.0.0.1:10025@NETWORK')
            address2 = SOAPAddress.Address('127.0.0.1:10026@NETWORK')
            address3 = SOAPAddress.Address('127.0.0.1:10027@NETWORK')
            address5 = SOAPAddress.Address('127.0.0.1:10029@NETWORK')
            address7 = SOAPAddress.Address('127.0.0.1:10031@NETWORK')
            address8 = SOAPAddress.Address('127.0.0.1:10032@NETWORK')

            # 2nd: network
            soap_network1 = SOAPNetwork.SOAPNetwork( address1 )
            soap_network2 = SOAPNetwork.SOAPNetwork( address2 )
            soap_network3 = SOAPNetwork.SOAPNetwork( address3 )
            soap_network5 = SOAPNetwork.SOAPNetwork( address5 )
            soap_network7 = SOAPNetwork.SOAPNetwork( address7 )
            soap_network8 = SOAPNetwork.SOAPNetwork( address8 )

            # 3rd: accesses
            access_soap1 = Access.Access( Protocols.SOAP, AccessLevel.network,(soap_network1,) )
            access_soap2 = Access.Access( Protocols.SOAP, AccessLevel.network,(soap_network2,) )
            access_soap3 = Access.Access( Protocols.SOAP, AccessLevel.network,(soap_network3,) )
            access_soap5 = Access.Access( Protocols.SOAP, AccessLevel.network,(soap_network5,) )
            access_soap7 = Access.Access( Protocols.SOAP, AccessLevel.network,(soap_network7,) )
            access_soap8 = Access.Access( Protocols.SOAP, AccessLevel.network,(soap_network8,) )

            # 4th: appending accesses
            map.append_accesses( 'WL_MACHINE1', 'WL_SERVER1', 'login1', ( access_soap1, ))
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
                CoordinatorServer.CoordinatorServer.__init__(self,cfg_manager,map, *args, **kargs)

        real_coordinator_server = RealCoordinatorServer(
                cfg_manager,
                map,
                Direct = ('coordinator1',),
                SOAP   = ('',10027)
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
            ServerType.ServerType,
            {
                ServerType.Coordinator.name :    voodoo_exported_methods.coordinator,
                ServerType.Login.name :          weblab_exported_methods.Login,
                ServerType.UserProcessing.name : weblab_exported_methods.UserProcessing,
                ServerType.Proxy.name :          weblab_exported_methods.Proxy,
                ServerType.Laboratory.name :     weblab_exported_methods.Laboratory,
                ServerType.Translator.name :     weblab_exported_methods.Translator,
                ServerType.Experiment.name :     weblab_exported_methods.Experiment
            }
        )

        locator = ServerLocator.ServerLocator(
            coordinator_server_address,
            server_type_handler
        )

        easy_locator = EasyLocator.EasyLocator(
                CoordAddress.CoordAddress('WL_MACHINE1','WL_SERVER1','coordinator1'),
                locator
            )

        return easy_locator

    def generate_configuration_server(self):
        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration)
        return cfg_manager

    def generate_login_server(self, protocols, cfg_manager):
        login_coord_address = CoordAddress.CoordAddress.translate_address("login1:WL_SERVER1@WL_MACHINE1")
        locator = self.generate_locator()

        generated_login_server = ServerSkel.factory(
                self.generate_configuration_server(),
                protocols, 
                weblab_exported_methods.Login
            )

        class RealLoginServer(LoginServer.LoginServer,generated_login_server):
            def __init__(self, coord_address, locator, cfg_manager, *args,**kargs):
                LoginServer.LoginServer.__init__(self, coord_address, locator, cfg_manager, *args, **kargs)

        real_login_server = RealLoginServer(
                login_coord_address,
                locator,
                cfg_manager,
                Direct = ('login1',),
                SOAP   = ('',10025)
            )
        real_login_server.start()

        login_client = locator.get_server(ServerType.Login, None)
        return login_client, real_login_server

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

        coordinator = Coordinator.Coordinator(locator, cfg_manager)
        coordinator._clean()

        real_core_server = RealUserProcessingServer(
                ups_coord_address,
                locator,
                cfg_manager,
                Direct = ('ups1',),
                SOAP   = ('',10026)
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
        locator = self.generate_locator()

        real_experiment = RealUdXilinxExperiment(
                None,
                None,
                cfg_manager,
                fake_xilinx_impact,
                fake_serial_port,
                Direct = ('experiment' + number,),
                SOAP   = ('',10031 + (int(number)-1))
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
                Direct = ('laboratory1',),
                SOAP   = ('',10029)
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
        self.login_server, reals       = self.generate_login_server(
                                protocols,
                                self.cfg_manager
                            )
        self.real_login = reals

        self.real_servers.append(reals)
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
        backup_poll_time           = configuration.core_experiment_poll_time
        backup_time_between_checks = self.cfg_manager.get_value('core_time_between_checks', AliveUsersCollection.DEFAULT_TIME_BETWEEN_CHECKS)
        try:
            self.cfg_manager._set_value('core_experiment_poll_time',1.5)
            self.cfg_manager._set_value('core_time_between_checks',1.5)
            self._single_use(logout = False, plus_async_use = False)
            time.sleep(self.cfg_manager.get_value('core_experiment_poll_time') + 0.3 + self.cfg_manager.get_value('core_time_between_checks'))
            self._single_use(logout = False, plus_async_use = False)
        finally:
            self.cfg_manager._set_value('core_experiment_poll_time',backup_poll_time)
            self.cfg_manager._set_value('core_time_between_checks',backup_time_between_checks)

    @uses_module(UserProcessingServer)
    @uses_module(UserProcessor)
    @uses_module(ServerSOAP)
    def test_simple_single_uses(self):
        for _ in range(1):
            self._single_use()
        self._single_use()
        self._single_use()
        
    def _wait_async_done(self, session_id, reqids):
        """
        _wait_async_done(session_id, reqids)
        Helper methods that waits for the specified asynchronous requests to be finished,
        and which asserts that they were successful. Note that it doesn't actually return
        their responses.
        @param reqids Tuple containing the request ids for the commands to check.
        @return Nothing
        """
        # Wait until send_async_file query is actually finished.
        reqsl = list(reqids)
        while len(reqsl) > 0:
            requests = self.real_ups.check_async_command_status(session_id, tuple(reqsl))
            self.assertEquals(len(reqsl), len(requests))
            for rid, req in requests.iteritems():
                status = req[0]
                self.assertTrue(status in ("running", "ok", "error"))
                if status != "running":
                    self.assertEquals("ok", status, "Contents: " + req[1])
                    reqsl.remove(rid)
        
        
    def _get_async_response(self, session_id, reqid):
        """
        _get_async_response(reqids)
        Helper method that synchronously gets the response for the specified async request, asserting that
        it was successful.
        @param reqid The request identifier for the async request whose response we want
        @return Response to the request, if successful. None, otherwise.
        """
        # Wait until send_async_file query is actually finished.
        while True:
            requests = self.real_ups.check_async_command_status(session_id, (reqid,))
            self.assertEquals(1, len(requests))
            self.assertTrue(reqid in requests)
            req = requests[reqid]
            status = req[0]
            self.assertTrue(status in ("running", "ok", "error"))
            if status != "running":
                self.assertEquals("ok", status, "Contents: " + req[1])
                return Command.Command(req[1])
        
    def _single_async_use(self, logout = True):
        self.fake_impact1.clear()
        self.fake_impact2.clear()
        self.fake_serial_port1.clear()
        self.fake_serial_port2.clear()

        session_id = self.real_login.login('student1','password')
        
        user_information = self.real_ups.get_user_information(session_id)
        self.assertEquals(
                'student1',
                user_information.login
            )

        self.assertEquals(
                'Name of student 1',
                user_information.full_name
            )
        self.assertEquals(
                'weblab@deusto.es',
                user_information.email
            )

        experiments = self.real_ups.list_experiments(session_id)
        self.assertEquals( 5, len(experiments))
        
        fpga_experiments = [ exp.experiment for exp in experiments if exp.experiment.name == 'ud-fpga' ]
        self.assertEquals(
                len(fpga_experiments),
                1
            )

        # reserve it
        _ = self.real_ups.reserve_experiment(
                session_id,
                fpga_experiments[0].to_experiment_id(),
                "{}",
                ClientAddress.ClientAddress("127.0.0.1")
            )

        # wait until it is reserved
        short_time = 0.1
        
        # Time extended from 9.0 to 13.0 because at times the test failed, possibly for that reason.
        times      = 13.0 / short_time

        while times > 0:
            time.sleep(short_time)
            new_status = self.real_ups.get_reservation_status(session_id)
            if not isinstance(new_status, Reservation.WaitingConfirmationReservation) and not isinstance(new_status, Reservation.WaitingReservation):
                break
            times -= 1
        reservation = self.real_ups.get_reservation_status(
                        session_id
                    )
        self.assertTrue(
                isinstance(
                    reservation, 
                    Reservation.ConfirmedReservation 
                ),
                "Reservation %s is not Confirmed, as expected by this time" % reservation
            )   
        
        
        
        # send the program again, but asynchronously. Though this should work, it is not really very customary
        # to send_file more than once in the same session. In fact, it is a feature which might get removed in
        # the future. When/if that happens, this will need to be modified.
        CONTENT = "content of the program FPGA"
        reqid = self.real_ups.send_async_file(session_id, ExperimentUtil.serialize(CONTENT), 'program')
        
        # Wait until send_async_file query is actually finished.
        #self._get_async_response(session_id, reqid)
        self._wait_async_done(session_id, (reqid,))
        
        # We need to wait for the programming to finish, while at the same
        # time making sure that the tests don't dead-lock.
        start_time = time.time()
        response = "STATE=not_ready"
        while response in ("STATE=not_ready", "STATE=programming") and time.time() - start_time < XILINX_TIMEOUT:
            reqid = self.real_ups.send_async_command(session_id, Command.Command("STATE"))
            respcmd = self._get_async_response(session_id, reqid)
            response = respcmd.get_command_string()
            time.sleep(0.2)
        
        # Check that the current state is "Ready"
        self.assertEquals("STATE=ready", response)
        
        
        reqid = self.real_ups.send_async_command(session_id, Command.Command("ChangeSwitch on 0"))
        self._wait_async_done(session_id, (reqid,))
        
        reqid = self.real_ups.send_async_command(session_id, Command.Command("ClockActivation on 250"))
        self._wait_async_done(session_id, (reqid,))

        # Checking the commands sent
        # Note that the number of paths is 2 now that we send a file twice (sync and async).
        self.assertEquals(
                1,
                len(self.fake_impact1._paths)
            )
        self.assertEquals(
                0,
                len(self.fake_impact2._paths)
            )

        self.assertEquals(
                CONTENT,
                self.fake_impact1._paths[0]
            )

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
        
        if logout:
            self.real_ups.logout(session_id)
            
   
    def _single_use(self, logout = True, plus_async_use = True):
        """
        Will use an experiment. 
        @param logout If true, the user will be logged out after the use. Otherwise not.
        @param plus_async_use If true, after using the experiment synchronously, it will use it
        again using the asynchronous versions of the send_command and send_file requests.
        """
        self._single_sync_use(logout)
        if plus_async_use:
            self._single_async_use(logout)


    def _single_sync_use(self, logout = True):
        
        self.fake_impact1.clear()
        self.fake_impact2.clear()
        self.fake_serial_port1.clear()
        self.fake_serial_port2.clear()

        session_id = self.real_login.login('student1','password')
        
        user_information = self.real_ups.get_user_information(session_id)
        self.assertEquals(
                'student1',
                user_information.login
            )

        self.assertEquals(
                'Name of student 1',
                user_information.full_name
            )
        self.assertEquals(
                'weblab@deusto.es',
                user_information.email
            )

        experiments = self.real_ups.list_experiments(session_id)
        self.assertEquals( 5, len(experiments))
        
        fpga_experiments = [ exp.experiment for exp in experiments if exp.experiment.name == 'ud-fpga' ]
        self.assertEquals(
                len(fpga_experiments),
                1
            )

        # reserve it
        _ = self.real_ups.reserve_experiment(
                session_id,
                fpga_experiments[0].to_experiment_id(),
                "{}",
                ClientAddress.ClientAddress("127.0.0.1")
            )
        # wait until it is reserved
        short_time = 0.1
        times      = 13.0 / short_time

        while times > 0:
            new_status = self.real_ups.get_reservation_status(session_id)
            if not isinstance(new_status, Reservation.WaitingConfirmationReservation) and not isinstance(new_status, Reservation.WaitingReservation):
                break
            times -= 1
            time.sleep(short_time)
        reservation = self.real_ups.get_reservation_status(
                        session_id
                    )
        self.assertTrue(
                isinstance(
                    reservation, 
                    Reservation.ConfirmedReservation 
                ),
                "Reservation %s is not Confirmed, as expected by this time" % reservation
            )


        # send a program synchronously (the "traditional" way)
        CONTENT = "content of the program FPGA"
        self.real_ups.send_file(session_id, ExperimentUtil.serialize(CONTENT), 'program')
        
        # We need to wait for the programming to finish, while at the same
        # time making sure that the tests don't dead-lock.
        start_time = time.time()
        response = "STATE=not_ready"
        while response in ("STATE=not_ready", "STATE=programming") and time.time() - start_time < XILINX_TIMEOUT:
            respcmd = self.real_ups.send_command(session_id, Command.Command("STATE"))
            response = respcmd.get_command_string()
            time.sleep(0.2)
        
        # Check that the current state is "Ready"
        self.assertEquals("STATE=ready", response)
        
        
        # We need to wait for the programming to finish, while at the same
        # time making sure that the tests don't dead-lock.
        start_time = time.time()
        response = "STATE=not_ready"
        while response in ("STATE=not_ready", "STATE=programming") and time.time() - start_time < XILINX_TIMEOUT:
            respcmd = self.real_ups.send_command(session_id, Command.Command("STATE"))
            response = respcmd.get_command_string()
            time.sleep(0.2)
        
        # Check that the current state is "Ready"
        self.assertEquals("STATE=ready", response)
        
        
        self.real_ups.send_command(session_id, Command.Command("ChangeSwitch on 0"))
        self.real_ups.send_command(session_id, Command.Command("ClockActivation on 250"))

        # Checking the commands sent
        # Note that the number of paths is 2 now that we send a file twice (sync and async).
        self.assertEquals(
                1,
                len(self.fake_impact1._paths)
            )
        self.assertEquals(
                0,
                len(self.fake_impact2._paths)
            )

        self.assertEquals(
                CONTENT,
                self.fake_impact1._paths[0]
            )

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
        
        
#         end session
#         Note: Before async commands were implemented, this was actually done before
#         checking the commands sent. If it was that way for a reason, it might be
#         necessary to change it in the future.
        if logout:
            self.real_ups.logout(session_id)
        
        
        

    @uses_module(UserProcessingServer)
    @uses_module(UserProcessor)
    @uses_module(ServerSOAP)
    def test_two_multiple_uses_of_different_devices(self):
        user1_session_id = self.real_login.login('student1','password')
        user1_experiments = self.real_ups.list_experiments(user1_session_id)
        self.assertEquals(
                5,
                len(user1_experiments)
            )
        
        fpga_experiments = [ exp.experiment for exp in user1_experiments if exp.experiment.name == 'ud-fpga' ]
        self.assertEquals(
                len(fpga_experiments),
                1
            )

        # reserve it
        self.real_ups.reserve_experiment(
                user1_session_id,
                fpga_experiments[0].to_experiment_id(),
                "{}",
                ClientAddress.ClientAddress("127.0.0.1")
            )

        user2_session_id = self.real_login.login('student2','password')
        user2_experiments = self.real_ups.list_experiments(user2_session_id)
        self.assertEquals(
                7,
                len(user2_experiments)
            )
        
        pld_experiments = [ exp.experiment for exp in user2_experiments if exp.experiment.name == 'ud-pld' ]
        self.assertEquals(
                len(pld_experiments),
                1
            )

        # reserve it
        self.real_ups.reserve_experiment(
                user2_session_id,
                pld_experiments[0].to_experiment_id(),
                "{}",
                ClientAddress.ClientAddress("127.0.0.1")
            )

        short_time = 0.1
        times      = 3.0 / short_time

        while times > 0:
            time.sleep(short_time)
            new_status1 = self.real_ups.get_reservation_status(user1_session_id)
            new_status2 = self.real_ups.get_reservation_status(user2_session_id)
            if not isinstance(new_status1, Reservation.WaitingConfirmationReservation):
                if not isinstance(new_status2, Reservation.WaitingConfirmationReservation):
                    break
            times -= 1

        self.assertTrue(
                isinstance(
                    self.real_ups.get_reservation_status(
                        user1_session_id
                    ), 
                    Reservation.ConfirmedReservation
                )
            )

        self.assertTrue(
                isinstance(
                    self.real_ups.get_reservation_status(
                        user2_session_id
                    ), 
                    Reservation.ConfirmedReservation
                )
            )

        # send a program
        CONTENT1 = "content of the program FPGA"
        self.real_ups.send_file(user1_session_id, ExperimentUtil.serialize(CONTENT1), 'program')
        
        # We need to wait for the programming to finish.
        start_time = time.time()
        response = "STATE=not_ready"
        while response in ("STATE=not_ready", "STATE=programming") and time.time() - start_time < XILINX_TIMEOUT:
            respcmd = self.real_ups.send_command(user1_session_id, Command.Command("STATE"))
            response = respcmd.get_command_string()
            time.sleep(0.2)
        
        # Check that the current state is "Ready"
        self.assertEquals("STATE=ready", response)
        
        self.real_ups.send_command(user1_session_id, Command.Command("ChangeSwitch off 1"))
        self.real_ups.send_command(user1_session_id, Command.Command("ClockActivation on 250"))

        CONTENT2 = "content of the program PLD"
        self.real_ups.send_file(user2_session_id, ExperimentUtil.serialize(CONTENT2), 'program')
       
        # We need to wait for the programming to finish.
        start_time = time.time()
        response = "STATE=not_ready"
        while response in ("STATE=not_ready", "STATE=programming") and time.time() - start_time < XILINX_TIMEOUT:
            respcmd = self.real_ups.send_command(user1_session_id, Command.Command("STATE"))
            response = respcmd.get_command_string()
            time.sleep(0.2)
            
        # Check that the current state is "Ready"
        self.assertEquals("STATE=ready", response)
        
        self.real_ups.send_command(user2_session_id, Command.Command("ChangeSwitch on 0"))
        self.real_ups.send_command(user2_session_id, Command.Command("ClockActivation on 250"))

        # end session
        self.real_ups.logout(user1_session_id)
        self.real_ups.logout(user2_session_id)

        # Checking the commands sent
        self.assertEquals(
                1,
                len(self.fake_impact1._paths)
            )
        self.assertEquals(
                1,
                len(self.fake_impact2._paths)
            )
        self.assertEquals(
                CONTENT1,
                self.fake_impact1._paths[0]
            )
        self.assertEquals(
                CONTENT2,
                self.fake_impact2._paths[0]
            )

        initial_open  = 1
        initial_send  = 1
        initial_close = 1

        initial_total = initial_open + initial_send + initial_close

        # ChangeSwitch off 1
        self.assertEquals(  
                (0 + initial_total,1),
                self.fake_serial_port1.dict['open'][0 + initial_open]
            )
        self.assertEquals(  
                (1 + initial_total,4),
                self.fake_serial_port1.dict['send'][0 + initial_send]
            )
        self.assertEquals(  
                (2 + initial_total,None),
                self.fake_serial_port1.dict['close'][0 + initial_close]
            )

        self.assertEquals(  
                (0 + initial_total,1),
                self.fake_serial_port2.dict['open'][0 + initial_open]
            )
        self.assertEquals(  
                (1 + initial_total,1),
                self.fake_serial_port2.dict['send'][0 + initial_send]
            )
        self.assertEquals(  
                (2 + initial_total,None),
                self.fake_serial_port2.dict['close'][0 + initial_close]
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

        self.assertEquals(  
                (3 + initial_total,1),
                self.fake_serial_port2.dict['open'][1 + initial_open]
            )
        self.assertEquals(  
                (4 + initial_total,32),
                self.fake_serial_port2.dict['send'][1 + initial_send]
            )
    
        self.assertEquals(  
                (5 + initial_total,None),
                self.fake_serial_port2.dict['close'][1 + initial_close]
            )

    def tearDown(self):
        ServerRegistry.get_instance().clear()

        for i in self.real_servers:
            i.stop()

class Case001_Direct_Memory_TestCase(Case001TestCase, unittest.TestCase):
    def get_protocols(self):
        return (Protocols.Direct, )
    def get_session_type(self):
        return SessionType.Memory

Case001_Direct_Memory_TestCase = case_uses_module(UserProcessingServer)(Case001_Direct_Memory_TestCase)

if ServerSOAP.SOAPPY_AVAILABLE:
    class Case001_SOAP_MySQL_TestCase(Case001TestCase, unittest.TestCase):
        def get_protocols(self):
            return (Protocols.SOAP, )
        def get_session_type(self):
            return SessionType.sqlalchemy

    Case001_SOAP_MySQL_TestCase = case_uses_module(UserProcessingServer)(Case001_SOAP_MySQL_TestCase)

    class Case001_SOAP_Memory_TestCase(Case001TestCase, unittest.TestCase):
        def get_protocols(self):
            return (Protocols.SOAP, )
        def get_session_type(self):
            return SessionType.Memory

    Case001_SOAP_Memory_TestCase = case_uses_module(UserProcessingServer)(Case001_SOAP_Memory_TestCase)
else:
    print >> sys.stderr, "Case001_SOAP_MySQL_TestCase and Case001_SOAP_Memory_TestCase skipped; SOAPpy not installed"

def suite():
    suites = (unittest.makeSuite(Case001_Direct_Memory_TestCase), )
    if ServerSOAP.SOAPPY_AVAILABLE:
        suites += ( unittest.makeSuite(Case001_SOAP_MySQL_TestCase), unittest.makeSuite(Case001_SOAP_Memory_TestCase) )
    return unittest.TestSuite( suites )

if __name__ == '__main__':
    unittest.main()


