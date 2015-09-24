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

import es.deusto.weblab.client.dto.experiments.Command;

public class SwitchCommand extends Command{

	private final int n;
	private final boolean state;
	
	public SwitchCommand(int n, boolean state){
		this.n = n;
		this.state = state;
	}
	
	@Override
	public String getCommandString() {
		return "ChangeSwitch " + (this.state?"on":"off") + " " + this.n;
	}
}
