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
package es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.pic.commands;

import es.deusto.weblab.client.dto.experiments.Command;

public class PulseCommand extends Command{
	private final int number;
	private final int millis;
	
	public PulseCommand(int number, int millis){
		this.number = number;
		this.millis = millis;
	}

	@Override
	public String getCommandString() {
		return "PULSE=" + this.number + " " + this.millis;
	}
}
