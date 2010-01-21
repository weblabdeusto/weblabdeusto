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
package es.deusto.weblab.client.experiment.plugins.es.deusto.weblab.javadummy.commands;

import es.deusto.weblab.client.experiment.plugins.java.Command;

public class PulseCommand extends Command{
	private final int number;
	private final boolean state;
	
	public PulseCommand(int number, boolean state){
		this.number = number;
		this.state  = state;
		
	}

	public String getCommandString() {
		return "SetPulse " + (this.state?"on":"off") + " " + this.number;
	}
}
