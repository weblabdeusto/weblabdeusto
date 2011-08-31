/*
* Copyright (C) 2005-2009 University of Deusto
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
package es.deusto.weblab.client.experiments.pic.commands;

import junit.framework.Assert;

import com.google.gwt.junit.client.GWTTestCase;

import es.deusto.weblab.client.experiments.pic.commands.AdjustCommand;
import es.deusto.weblab.client.experiments.pic.commands.PulseCommand;
import es.deusto.weblab.client.experiments.pic.commands.SwitchCommand;
import es.deusto.weblab.client.experiments.pic.commands.WriteCommand;

public class CommandsTest extends GWTTestCase {

	public void testSwitchCommand(){
		SwitchCommand switchCommand = new SwitchCommand(0,true);
		Assert.assertEquals("SWITCH=0 ON", switchCommand.getCommandString());
		switchCommand = new SwitchCommand(0,false);
		Assert.assertEquals("SWITCH=0 OFF", switchCommand.getCommandString());
		switchCommand = new SwitchCommand(4,true);
		Assert.assertEquals("SWITCH=4 ON", switchCommand.getCommandString());
		switchCommand = new SwitchCommand(4,false);
		Assert.assertEquals("SWITCH=4 OFF", switchCommand.getCommandString());
		switchCommand = new SwitchCommand(9,true);
		Assert.assertEquals("SWITCH=9 ON", switchCommand.getCommandString());
		switchCommand = new SwitchCommand(9,false);
		Assert.assertEquals("SWITCH=9 OFF", switchCommand.getCommandString());
	}
	
	public void testPulseCommand(){
		PulseCommand pulseCommand = new PulseCommand(0,1000);
		Assert.assertEquals("PULSE=0 1000", pulseCommand.getCommandString());
		pulseCommand = new PulseCommand(0,500);
		Assert.assertEquals("PULSE=0 500", pulseCommand.getCommandString());
		pulseCommand = new PulseCommand(3,750);
		Assert.assertEquals("PULSE=3 750", pulseCommand.getCommandString());
		pulseCommand = new PulseCommand(3,1250);
		Assert.assertEquals("PULSE=3 1250", pulseCommand.getCommandString());
	}
	
	public void testAdjustCommand(){
		AdjustCommand adjustCommand = new AdjustCommand(0,0,1);
		Assert.assertEquals("ADJUST=0 0.0", adjustCommand.getCommandString());
		adjustCommand = new AdjustCommand(0,10,1);
		Assert.assertEquals("ADJUST=0 1.0", adjustCommand.getCommandString());
		adjustCommand = new AdjustCommand(3,1,1);
		Assert.assertEquals("ADJUST=3 0.1", adjustCommand.getCommandString());
		adjustCommand = new AdjustCommand(3,9,1);
		Assert.assertEquals("ADJUST=3 0.9", adjustCommand.getCommandString());
		adjustCommand = new AdjustCommand(3,9,2);
		Assert.assertEquals("ADJUST=3 0.09", adjustCommand.getCommandString());
		adjustCommand = new AdjustCommand(3,9,3);
		Assert.assertEquals("ADJUST=3 0.009", adjustCommand.getCommandString());
		adjustCommand = new AdjustCommand(3,9,0);
		Assert.assertEquals("ADJUST=3 9", adjustCommand.getCommandString());
		adjustCommand = new AdjustCommand(3,123456,3);
		Assert.assertEquals("ADJUST=3 123.456", adjustCommand.getCommandString());
	}
	
	public void testWriteCommand(){
		WriteCommand writeCommand = new WriteCommand(0,"hello world");
		Assert.assertEquals("WRITE=0 hello world EOT", writeCommand.getCommandString());
		writeCommand = new WriteCommand(1,"game over");
		Assert.assertEquals("WRITE=1 game over EOT", writeCommand.getCommandString());
	}
	
	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}
}
