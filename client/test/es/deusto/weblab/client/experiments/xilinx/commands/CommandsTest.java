/*
* Copyright (C) 2005 onwards University of Deusto
* All rights reserved.
*
* This software is licensed as described in the file COPYING, which
* you should have received as part of this distribution.
*
* This software consists of contributions made by many individuals, 
* listed below:
*
* Author: Pablo Orduña <pablo@ordunya.com>
*
*/ 
package es.deusto.weblab.client.experiments.xilinx.commands;

import junit.framework.Assert;

import com.google.gwt.junit.client.GWTTestCase;

import es.deusto.weblab.client.experiments.xilinx.commands.ClockActivationCommand;
import es.deusto.weblab.client.experiments.xilinx.commands.ClockDeactivationCommand;
import es.deusto.weblab.client.experiments.xilinx.commands.PulseCommand;
import es.deusto.weblab.client.experiments.xilinx.commands.SwitchCommand;

public class CommandsTest extends GWTTestCase {

	public void testSwitchCommand(){
		SwitchCommand switchCommand = new SwitchCommand(0,true);
		Assert.assertEquals("ChangeSwitch on 0", switchCommand.getCommandString());
		switchCommand = new SwitchCommand(0,false);
		Assert.assertEquals("ChangeSwitch off 0", switchCommand.getCommandString());
		switchCommand = new SwitchCommand(4,true);
		Assert.assertEquals("ChangeSwitch on 4", switchCommand.getCommandString());
		switchCommand = new SwitchCommand(4,false);
		Assert.assertEquals("ChangeSwitch off 4", switchCommand.getCommandString());
		switchCommand = new SwitchCommand(9,true);
		Assert.assertEquals("ChangeSwitch on 9", switchCommand.getCommandString());
		switchCommand = new SwitchCommand(9,false);
		Assert.assertEquals("ChangeSwitch off 9", switchCommand.getCommandString());
	}
	
	public void testPulseCommand(){
		PulseCommand pulseCommand = new PulseCommand(0,true);
		Assert.assertEquals("SetPulse on 0", pulseCommand.getCommandString());
		pulseCommand = new PulseCommand(0,false);
		Assert.assertEquals("SetPulse off 0", pulseCommand.getCommandString());
		pulseCommand = new PulseCommand(3,true);
		Assert.assertEquals("SetPulse on 3", pulseCommand.getCommandString());
		pulseCommand = new PulseCommand(3,false);
		Assert.assertEquals("SetPulse off 3", pulseCommand.getCommandString());
	}
	
	public void testClockActivation(){
		ClockActivationCommand clockActivation = new ClockActivationCommand(250);
		Assert.assertEquals("ClockActivation on 250", clockActivation.getCommandString());
		clockActivation = new ClockActivationCommand(500);
		Assert.assertEquals("ClockActivation on 500", clockActivation.getCommandString());
		clockActivation = new ClockActivationCommand(1000);
		Assert.assertEquals("ClockActivation on 1000", clockActivation.getCommandString());
		clockActivation = new ClockActivationCommand(1500);
		Assert.assertEquals("ClockActivation on 1500", clockActivation.getCommandString());
		clockActivation = new ClockActivationCommand(2000);
		Assert.assertEquals("ClockActivation on 2000", clockActivation.getCommandString());
	}	
	
	public void testClockDeactivation(){
		final ClockDeactivationCommand clockDeactivation = new ClockDeactivationCommand();
		Assert.assertEquals("ClockActivation off", clockDeactivation.getCommandString());
	}	
	
	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}
}
